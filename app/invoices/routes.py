from app.utils import resolve_company
from flask import render_template, request, redirect, session, url_for, flash, make_response, send_file, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from sqlalchemy import or_
from datetime import datetime, UTC
from wtforms import ValidationError

from app.extensions import limiter

from app.models import db, Document, DocumentItem, Contact, InventoryItem, DocumentType, Payment, PaymentMethod, Project

from app.models.enums import ContactType, DocumentStatus
from .services import get_invoice_list, create_invoice_or_quote, update_invoice_or_quote, generate_invoice_pdf_from_request
from .services.invoice_query_service import export_invoice_report_xlsx
from .services.invoice_create_service import _generate_document_number
from .services.template_service import TemplateService
from . import invoices


@invoices.route('/<string:company_id>/invoices')
@login_required
@limiter.exempt
def index(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    pagination = get_invoice_list(company_id, request.args)

    for doc in pagination.items:
        doc.client = Contact.query.get(doc.client_id) if doc.client_id else None

                                            
    from app.models.enums import DocumentType
    stats = {
        'total': Document.query.filter(Document.company_id == company_id, Document.type.in_([DocumentType.invoice, DocumentType.quote])).count(),
        'invoices': Document.query.filter_by(company_id=company_id, type=DocumentType.invoice).count(),
        'quotes': Document.query.filter_by(company_id=company_id, type=DocumentType.quote).count(),
        'paid': Document.query.filter_by(company_id=company_id, status='paid').count(),
        'pending': Document.query.filter_by(company_id=company_id, status='pending').count(),
        'overdue': Document.query.filter_by(company_id=company_id, status='overdue').count(),
        'draft': Document.query.filter_by(company_id=company_id, status='draft').count()
    }

    export_args = request.args.to_dict(flat=True)
    export_args.pop('page', None)
    export_url = url_for('invoices.export', company_id=company.slug or company.id, **export_args)

    return render_template(
        "invoices/index.html",
        invoices=pagination.items,
        pagination=pagination,
        stats=stats,
        export_url=export_url
    )


@invoices.route('/<string:company_id>/invoices/export')
@login_required
def export(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    import io

    wb, filename = export_invoice_report_xlsx(company_id, request.args)
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)

    return send_file(
        out,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@invoices.route('/invoices/item-row', methods=['POST'])
@login_required
@limiter.exempt
def item_row():
    index = int(request.form.get('index', 0))
    csrf_token = request.form.get("csrf_token") 

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash("Invalid CSRF token. Please try again.", "error")
        return redirect(url_for("auth.login")) 

    inventory_items = InventoryItem.query.filter(
        InventoryItem.company_id == session.get('selected_company_id'),
        InventoryItem.quantity > 0
    ).all()
    
    return render_template('invoices/item_row.html', index=index, inventory_items=inventory_items, item=None)


@invoices.route('/<string:company_id>/invoices/create')
@login_required
@limiter.exempt
def create(company_id):
    company = resolve_company(company_id)
    company_id = company.id
                                                  
    from app.models import Warehouse
    clients = Contact.query.filter_by(company_id=company_id, type=ContactType.customer).all()
    inventory_items = InventoryItem.query.filter(
        InventoryItem.company_id == company_id,
        InventoryItem.quantity > 0
    ).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    projects = Project.query.filter_by(company_id=company_id, status='active').order_by(Project.name).all()

    selected_client_id = int(request.args.get('client_id', 0))
    selected_type = request.args.get('type', None)

    return render_template('invoices/form.html',
                         customer_id=selected_client_id, 
                         doc_type=selected_type,
                         invoice=None, 
                         company=company,
                         clients=clients, 
                         inventory_items=inventory_items,
                         warehouses=warehouses,
                         projects=projects,
                         document_items=None)

@invoices.route('/<string:company_id>/invoices/store', methods=['POST'])
@login_required
@limiter.exempt
def store(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    csrf_token = request.form.get("csrf_token")

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash("Invalid CSRF token. Please try again.", "error")
        return redirect(url_for("auth.login"))

    try:
        document = create_invoice_or_quote(
            company_id=company_id,
            form=request.form,
            user_id=current_user.id
        )

        doc_type_name = (
            'Invoice' if document.type == DocumentType.invoice else 'Quote'
        )
        flash(f'{doc_type_name} created successfully', 'success')

        return redirect(
            url_for('invoices.view', company_id=company_id, id=document.id)
        )

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating document: {e}', 'error')
        return redirect(url_for('invoices.create', company_id=company_id))


@invoices.route('/<string:company_id>/invoices/<int:id>')
@login_required
@limiter.exempt
def view(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
                            
    if document.client_id:
        document.client = Contact.query.get(document.client_id)
    else:
        document.client = None
    
                                                   
    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    for item in document_items:
        if item.inventory_item_id:
            item.inventory_item = InventoryItem.query.get(item.inventory_item_id)
        else:
            item.inventory_item = None
    
    payments = Payment.query.filter_by(document_id=document.id).order_by(Payment.payment_date.desc()).all()

    from app.models.accounting_attachment import AccountingAttachment
    payment_ids = [p.id for p in payments]
    if payment_ids:
        p_atts = AccountingAttachment.query.filter(
            AccountingAttachment.reference_type == 'Payment',
            AccountingAttachment.reference_id.in_(payment_ids),
            AccountingAttachment.is_deleted == False
        ).all()
    else:
        p_atts = []
    payment_attachments = {}
    for att in p_atts:
        payment_attachments.setdefault(att.reference_id, []).append(att)
    
    from app.models.audit import AuditLog
    from sqlalchemy.orm import joinedload
    audit_logs = AuditLog.query.filter_by(
        table_name='documents',
        record_id=document.id
    ).options(joinedload(AuditLog.user)).order_by(AuditLog.created_at.desc()).all()
    templates = TemplateService.list_for_company(company_id)
    
    return render_template('invoices/view.html', 
                         invoice=document, 
                         document_items=document_items,
                         payments=payments,
                         payment_attachments=payment_attachments,
                         audit_logs=audit_logs,
                         templates=templates,
                         now=datetime.now(UTC))


@invoices.route('/<string:company_id>/invoices/<int:id>/add-payment', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def add_payment(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id
    ).first_or_404()
    
    if request.method == 'GET':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return render_template('invoices/partials/payment_form.html', invoice=document, now=datetime.now(UTC))
        return redirect(url_for('invoices.view', company_id=company_id, id=id))

    csrf_token = request.form.get("csrf_token")
    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash("Invalid CSRF token. Please try again.", "error")
        return redirect(url_for("auth.login"))

    try:
        from .services import add_invoice_payment
        add_invoice_payment(document, request.form, request.files)
        flash('Payment recorded successfully', 'success')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return {"success": True}
        return redirect(url_for('invoices.view', company_id=company_id, id=id))

    except ValueError as e:
        flash(f'Invalid payment data: {e}', 'error')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return {"success": False, "message": str(e)}, 400

        return redirect(url_for('invoices.view', company_id=company_id, id=id))
    except Exception as e:
        flash(f'Error recording payment: {e}', 'error')
        return redirect(url_for('invoices.view', company_id=company_id, id=id))


@invoices.route('/<string:company_id>/invoices/<int:id>/edit')
@login_required
@limiter.exempt
def edit(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
                            
    if document.client_id:
        document.client = Contact.query.get(document.client_id)
    else:
        document.client = None
    
    from app.models import Warehouse
    clients = Contact.query.filter_by(company_id=company_id, type=ContactType.customer).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).all()
    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    projects = Project.query.filter_by(company_id=company_id, status='active').order_by(Project.name).all()
    
    # Include a currently assigned project even if it's inactive
    if document.project_id:
        assigned = Project.query.get(document.project_id)
        if assigned and assigned not in projects:
            projects = [assigned] + projects
    
                                                      
    for item in document_items:
        if item.inventory_item_id:
            item.inventory_item = InventoryItem.query.get(item.inventory_item_id)
        else:
            item.inventory_item = None
    
    return render_template('invoices/form.html', 
                         invoice=document, 
                         company=company,
                         clients=clients, 
                         inventory_items=inventory_items,
                         warehouses=warehouses,
                         projects=projects,
                         document_items=document_items)


@invoices.route('/<string:company_id>/invoices/<int:id>/update', methods=['POST'])
@login_required
@limiter.exempt
def update(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    csrf_token = request.form.get("csrf_token")

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash("Invalid CSRF token. Please try again.", "error")
        return redirect(url_for("auth.login"))

    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(
            Document.type == DocumentType.invoice,
            Document.type == DocumentType.quote
        )
    ).first_or_404()

    try:
        doc_type_str = request.form.get('type', 'invoice')
        new_doc_type = (
            DocumentType.invoice
            if doc_type_str == 'invoice'
            else DocumentType.quote
        )

        submitted_doc_num = request.form.get('document_number')

        if new_doc_type != document.type:
            document.document_number = _generate_document_number(company_id, new_doc_type)
        elif submitted_doc_num:
            document.document_number = submitted_doc_num

        document.type = new_doc_type
        document.client_id = (
            int(request.form.get('client_id'))
            if request.form.get('client_id') else None
        )
        document.warehouse_id = (
            int(request.form.get('warehouse_id'))
            if request.form.get('warehouse_id') else None
        )
        document.status = request.form.get('status', document.status)
        document.issued_date = (
            datetime.strptime(request.form.get('issued_date'), '%Y-%m-%d')
            if request.form.get('issued_date') else document.issued_date
        )
        document.due_date = (
            datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
            if request.form.get('due_date') else document.due_date
        )

        update_invoice_or_quote(
            document=document,
            form=request.form
        )

        db.session.commit()

        doc_type_name = (
            'Invoice'
            if document.type == DocumentType.invoice
            else 'Quote'
        )
        flash(doc_type_name + ' ' + 'updated successfully', 'success')

        return redirect(
            url_for('invoices.view', company_id=company_id, id=document.id)
        )

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating document: {e}', 'error')
        return redirect(
            url_for('invoices.edit', company_id=company_id, id=id)
        )


@invoices.route('/<string:company_id>/invoices/<int:id>/delete', methods=['POST'])
@login_required
def delete(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    csrf_token = request.form.get("csrf_token") 

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash("Invalid CSRF token. Please try again.", "error")
        return redirect(url_for("auth.login")) 
    
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
    try:
        from .services import delete_invoice_or_quote
        delete_invoice_or_quote(document)
        doc_type_name = 'Invoice' if document.type == DocumentType.invoice else 'Quote'
        flash(f'{doc_type_name} deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting document: {e}', 'error')
    
    return redirect(url_for('invoices.index', company_id=company_id))


@invoices.route('/<string:company_id>/invoices/<int:id>/print')
@login_required
def print_invoice(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(
            Document.type == DocumentType.invoice,
            Document.type == DocumentType.quote
        )
    ).first_or_404()

    try:
        # Check if user selected a specific template
        template_id_param = request.args.get('template_id')
        template = None
        if template_id_param:
            try:
                template = TemplateService.get(company_id, int(template_id_param))
            except Exception:
                pass
                
        pdf_bytes, filename = generate_invoice_pdf_from_request(
            document=document,
            request=request,
            session=session,
            current_user=current_user,
            template=template,
        )

        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'inline; filename="{filename}"'
        return response

    except Exception as e:
        flash(f"Error generating PDF: {str(e)}", "error")
        return redirect(
            url_for("invoices.view", company_id=company_id, id=id)
        )


# ============================================================================
# Template Management Routes
# ============================================================================

@invoices.route('/<string:company_id>/templates')
@login_required
@limiter.exempt
def templates_index(company_id):
    company = resolve_company(company_id)
    templates = TemplateService.list_for_company(company.id)
    return render_template('invoices/templates/index.html',
                           company=company,
                           templates=templates)


@invoices.route('/<string:company_id>/templates/new')
@login_required
@limiter.exempt
def templates_new(company_id):
    company = resolve_company(company_id)
    default_coords = TemplateService.get_default_coords()
    import json
    return render_template('invoices/templates/form.html',
                           company=company,
                           template=None,
                           html_content='',
                           default_coords_json=json.dumps(default_coords, indent=2))


@invoices.route('/<string:company_id>/templates/store', methods=['POST'])
@login_required
@limiter.exempt
def templates_store(company_id):
    company = resolve_company(company_id)
    try:
        pdf_file = request.files.get('pdf_background')
        tpl = TemplateService.create(company.id, request.form, pdf_file)
        flash('Plantilla creada correctamente.', 'success')
        return redirect(url_for('invoices.templates_index', company_id=company_id))
    except Exception as e:
        flash(f'Error al crear plantilla: {str(e)}', 'error')
        return redirect(url_for('invoices.templates_new', company_id=company_id))


@invoices.route('/<string:company_id>/templates/<int:template_id>/edit')
@login_required
@limiter.exempt
def templates_edit(company_id, template_id):
    company = resolve_company(company_id)
    tpl = TemplateService.get(company.id, template_id)
    html_content = TemplateService.read_html_content(tpl)
    import json
    coords_json = json.dumps(tpl.pdf_coordinates or TemplateService.get_default_coords(), indent=2)
    return render_template('invoices/templates/form.html',
                           company=company,
                           template=tpl,
                           html_content=html_content,
                           default_coords_json=coords_json)


@invoices.route('/<string:company_id>/templates/<int:template_id>/update', methods=['POST'])
@login_required
@limiter.exempt
def templates_update(company_id, template_id):
    company = resolve_company(company_id)
    try:
        pdf_file = request.files.get('pdf_background')
        TemplateService.update(company.id, template_id, request.form, pdf_file)
        flash('Plantilla actualizada correctamente.', 'success')
        return redirect(url_for('invoices.templates_index', company_id=company_id))
    except Exception as e:
        flash(f'Error al actualizar plantilla: {str(e)}', 'error')
        return redirect(url_for('invoices.templates_edit', company_id=company_id, template_id=template_id))


@invoices.route('/<string:company_id>/templates/<int:template_id>/set-default', methods=['POST'])
@login_required
def templates_set_default(company_id, template_id):
    company = resolve_company(company_id)
    try:
        TemplateService.set_default(company.id, template_id)
        flash('Plantilla establecida como predeterminada.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('invoices.templates_index', company_id=company_id))


@invoices.route('/<string:company_id>/templates/<int:template_id>/delete', methods=['POST'])
@login_required
def templates_delete(company_id, template_id):
    company = resolve_company(company_id)
    try:
        TemplateService.delete(company.id, template_id)
        flash('Plantilla eliminada.', 'success')
    except Exception as e:
        flash(f'Error al eliminar plantilla: {str(e)}', 'error')
    return redirect(url_for('invoices.templates_index', company_id=company_id))


@invoices.route('/<string:company_id>/templates/<int:template_id>/preview')
@login_required
def templates_preview(company_id, template_id):
    """Stream a live PDF preview using the most recent invoice for this company."""
    company = resolve_company(company_id)
    tpl = TemplateService.get(company.id, template_id)

    # Use the most recent issued invoice as preview subject, fallback to any
    document = (
        Document.query
        .filter_by(company_id=company.id)
        .filter(or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote))
        .order_by(Document.id.desc())
        .first()
    )

    if not document:
        flash('No hay facturas disponibles para previsualizar. Crea una factura primero.', 'error')
        return redirect(url_for('invoices.templates_index', company_id=company_id))

    try:
        from .services.invoice_pdf_service import generate_invoice_pdf
        try:
            tax_rate = float(session.get('tax_rate', 15)) / 100
        except (TypeError, ValueError):
            tax_rate = 0.15
        currency = session.get('currency', 'L')
        seller = current_user.name if current_user and current_user.name else 'ADMIN'

        pdf_bytes, filename = generate_invoice_pdf(
            document,
            template=tpl,
            currency=currency,
            tax_rate=tax_rate,
            include_tax=True,
            seller_name=seller,
        )
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="preview_{filename}"'
        return response
    except Exception as e:
        flash(f'Error al generar vista previa: {str(e)}', 'error')
        return redirect(url_for('invoices.templates_index', company_id=company_id))

@invoices.route('/<string:company_id>/templates/live-preview', methods=['POST'])
@login_required
@limiter.exempt
def templates_live_preview(company_id):
    """Generate a PDF on the fly using the submitted form data for a live preview."""
    company = resolve_company(company_id)

    document = (
        Document.query
        .filter_by(company_id=company.id)
        .filter(or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote))
        .order_by(Document.id.desc())
        .first()
    )

    if not document:
        return "No hay facturas disponibles para previsualizar. Crea una factura primero.", 400

    from app.models.document_template import DocumentTemplate, DocumentTemplateType
    import json
    
    tpl_type_str = request.form.get("type", "html")
    template_id = request.form.get("template_id")
    
    existing_tpl = None
    if template_id and template_id.isdigit():
        try:
            existing_tpl = TemplateService.get(company.id, int(template_id))
        except:
            pass

    tpl = DocumentTemplate(
        company_id=company.id,
        name="Preview",
        type=DocumentTemplateType(tpl_type_str)
    )

    if tpl.type == DocumentTemplateType.html:
        tpl.raw_html_content = request.form.get("html_content", "<h1>Sin contenido</h1>")
    else:
        coords_json = request.form.get("pdf_coordinates_json", "{}")
        try:
            tpl.pdf_coordinates = json.loads(coords_json)
        except Exception:
            tpl.pdf_coordinates = {}
            
        if existing_tpl and existing_tpl.pdf_background_path:
            tpl.pdf_background_path = existing_tpl.pdf_background_path
        else:
            tpl.pdf_background_path = "Factura Ferre-lagos.pdf" # Default fallback for preview

    try:
        from .services.invoice_pdf_service import generate_invoice_pdf
        try:
            tax_rate = float(session.get('tax_rate', 15)) / 100
        except (TypeError, ValueError):
            tax_rate = 0.15
        currency = session.get('currency', 'L')
        seller = current_user.name if current_user and current_user.name else 'ADMIN'

        pdf_bytes, filename = generate_invoice_pdf(
            document,
            template=tpl,
            currency=currency,
            tax_rate=tax_rate,
            include_tax=True,
            seller_name=seller,
        )
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename="live_preview.pdf"'
        return response
    except Exception as e:
        return f"Error al generar vista previa: {str(e)}", 500
