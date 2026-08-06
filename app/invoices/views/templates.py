from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, send_file, session, url_for
from flask_login import current_user, login_required
from flask_wtf.csrf import validate_csrf
from sqlalchemy import or_
from wtforms import ValidationError

from app.extensions import limiter
from app.models import Contact, Document, DocumentItem, DocumentType, InventoryItem, Payment, PaymentMethod, Project, db
from app.models.enums import ContactType, DocumentStatus
from app.utils import resolve_company

from .. import invoices
from ..services import create_invoice_or_quote, generate_invoice_pdf_from_request, get_invoice_list, update_invoice_or_quote
from ..services.invoice_create_service import _generate_document_number
from ..services.invoice_query_service import export_invoice_report_xlsx
from ..services.template_service import TemplateService


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
        from ..services.invoice_pdf_service import generate_invoice_pdf
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
        from ..services.invoice_pdf_service import generate_invoice_pdf
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
