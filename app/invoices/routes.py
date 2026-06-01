from flask import render_template, request, redirect, session, url_for, flash, make_response
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from flask_babel import _
from sqlalchemy import or_
from datetime import datetime, UTC
from wtforms import ValidationError

from app.extensions import limiter

from app.models import db, Document, DocumentItem, Contact, InventoryItem, DocumentType, Payment, PaymentMethod

from app.models.enums import ContactType, DocumentStatus
from .services import get_invoice_list, create_invoice_or_quote, update_invoice_or_quote, generate_invoice_pdf_from_request
from .services.invoice_create_service import _generate_document_number
from . import invoices


@invoices.route('/<int:company_id>/invoices')
@login_required
@limiter.exempt
def index(company_id):
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

    return render_template(
        "invoices/index.html",
        invoices=pagination.items,
        pagination=pagination,
        stats=stats
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
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login")) 

    inventory_items = InventoryItem.query.filter(
        InventoryItem.company_id == session.get('selected_company_id'),
        InventoryItem.quantity > 0
    ).all()
    
    return render_template('invoices/item_row.html', index=index, inventory_items=inventory_items, item=None)


@invoices.route('/<int:company_id>/invoices/create')
@login_required
@limiter.exempt
def create(company_id):
                                                  
    from app.models import Warehouse
    clients = Contact.query.filter_by(company_id=company_id, type=ContactType.customer).all()
    inventory_items = InventoryItem.query.filter(
        InventoryItem.company_id == company_id,
        InventoryItem.quantity > 0
    ).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()

    selected_client_id = int(request.args.get('client_id', 0))
    selected_type = request.args.get('type', None)

    return render_template('invoices/form.html',
                         customer_id=selected_client_id, 
                         doc_type=selected_type,
                         invoice=None, 
                         clients=clients, 
                         inventory_items=inventory_items,
                         warehouses=warehouses,
                         document_items=None)

@invoices.route('/<int:company_id>/invoices/store', methods=['POST'])
@login_required
@limiter.exempt
def store(company_id):
    csrf_token = request.form.get("csrf_token")

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login"))

    try:
        document = create_invoice_or_quote(
            company_id=company_id,
            form=request.form,
            user_id=current_user.id
        )

        doc_type_name = (
            _('Invoice') if document.type == DocumentType.invoice else _('Quote')
        )
        flash(_(f'{doc_type_name} created successfully'), 'success')

        return redirect(
            url_for('invoices.view', company_id=company_id, id=document.id)
        )

    except Exception as e:
        db.session.rollback()
        flash(_('Error creating document: %(error)s', error=str(e)), 'error')
        return redirect(url_for('invoices.create', company_id=company_id))


@invoices.route('/<int:company_id>/invoices/<int:id>')
@login_required
@limiter.exempt
def view(company_id, id):
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
    
    return render_template('invoices/view.html', 
                         invoice=document, 
                         document_items=document_items,
                         payments=payments,
                         now=datetime.now(UTC))


@invoices.route('/<int:company_id>/invoices/<int:id>/add-payment', methods=['POST'])
@login_required
@limiter.exempt
def add_payment(company_id, id):
    csrf_token = request.form.get("csrf_token")

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login"))

    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id
    ).first_or_404()

    try:
        from .services import add_invoice_payment
        add_invoice_payment(document, request.form)
        flash(_('Payment recorded successfully'), 'success')
        return redirect(url_for('invoices.view', company_id=company_id, id=id))

    except ValueError as e:
        flash(_('Invalid payment data: %(error)s', error=str(e)), 'error')
        return redirect(url_for('invoices.view', company_id=company_id, id=id))
    except Exception as e:
        flash(_('Error recording payment: %(error)s', error=str(e)), 'error')
        return redirect(url_for('invoices.view', company_id=company_id, id=id))


@invoices.route('/<int:company_id>/invoices/<int:id>/edit')
@login_required
@limiter.exempt
def edit(company_id, id):
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
    
                                                      
    for item in document_items:
        if item.inventory_item_id:
            item.inventory_item = InventoryItem.query.get(item.inventory_item_id)
        else:
            item.inventory_item = None
    
    return render_template('invoices/form.html', 
                         invoice=document, 
                         clients=clients, 
                         inventory_items=inventory_items,
                         warehouses=warehouses,
                         document_items=document_items)


@invoices.route('/<int:company_id>/invoices/<int:id>/update', methods=['POST'])
@login_required
@limiter.exempt
def update(company_id, id):
    csrf_token = request.form.get("csrf_token")

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
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
            _('Invoice')
            if document.type == DocumentType.invoice
            else _('Quote')
        )
        flash(doc_type_name + ' ' + _('updated successfully'), 'success')

        return redirect(
            url_for('invoices.view', company_id=company_id, id=document.id)
        )

    except Exception as e:
        db.session.rollback()
        flash(_('Error updating document: %(error)s', error=str(e)), 'error')
        return redirect(
            url_for('invoices.edit', company_id=company_id, id=id)
        )


@invoices.route('/<int:company_id>/invoices/<int:id>/delete', methods=['POST'])
@login_required
def delete(company_id, id):
    csrf_token = request.form.get("csrf_token") 

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login")) 
    
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
    try:
        from .services import delete_invoice_or_quote
        delete_invoice_or_quote(document)
        doc_type_name = _('Invoice') if document.type == DocumentType.invoice else _('Quote')
        flash(_(f'{doc_type_name} deleted successfully'), 'success')
    except Exception as e:
        flash(_('Error deleting document: %(error)s', error=str(e)), 'error')
    
    return redirect(url_for('invoices.index', company_id=company_id))


@invoices.route('/<int:company_id>/invoices/<int:id>/print')
@login_required
def print_invoice(company_id, id):
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(
            Document.type == DocumentType.invoice,
            Document.type == DocumentType.quote
        )
    ).first_or_404()

    try:
        pdf_bytes, filename = generate_invoice_pdf_from_request(
            document=document,
            request=request,
            session=session,
            current_user=current_user,
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