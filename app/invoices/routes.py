from flask import render_template, request, redirect, session, url_for, flash, make_response
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from flask_babel import _
from sqlalchemy import or_
from datetime import datetime
from wtforms import ValidationError

from extensions import limiter

from models import db, Document, DocumentItem, Client, InventoryItem, DocumentType

from .services import get_invoice_list, create_invoice_or_quote, update_invoice_or_quote, generate_invoice_pdf
from . import invoices


@invoices.route('/<int:company_id>/invoices')
@login_required
@limiter.exempt
def index(company_id):
    pagination = get_invoice_list(company_id, request.args)

    for doc in pagination.items:
        doc.client = Client.query.get(doc.client_id) if doc.client_id else None

    return render_template(
        "invoices/index.html",
        invoices=pagination.items,
        pagination=pagination
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
    
    return render_template('invoices/item_row.html', index=index, inventory_items=inventory_items)


@invoices.route('/<int:company_id>/invoices/create')
@login_required
@limiter.exempt
def create(company_id):
    # Get clients and inventory items for the form
    clients = Client.query.filter_by(company_id=company_id).all()
    inventory_items = InventoryItem.query.filter(
        InventoryItem.company_id == company_id,
        InventoryItem.quantity > 0
    ).all()

    selected_client_id = int(request.args.get('client_id', 0))
    selected_type = request.args.get('type', None)

    return render_template('invoices/form.html',
                         customer_id=selected_client_id, 
                         doc_type=selected_type,
                         invoice=None, 
                         clients=clients, 
                         inventory_items=inventory_items,
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
    
    # Get client information
    if document.client_id:
        document.client = Client.query.get(document.client_id)
    else:
        document.client = None
    
    # Get document items with inventory information
    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    for item in document_items:
        if item.inventory_item_id:
            item.inventory_item = InventoryItem.query.get(item.inventory_item_id)
        else:
            item.inventory_item = None
    
    return render_template('invoices/view.html', 
                         invoice=document, 
                         document_items=document_items)


@invoices.route('/<int:company_id>/invoices/<int:id>/edit')
@login_required
@limiter.exempt
def edit(company_id, id):
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
    # Get client information
    if document.client_id:
        document.client = Client.query.get(document.client_id)
    else:
        document.client = None
    
    clients = Client.query.filter_by(company_id=company_id).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).all()
    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    
    # Get inventory information for each document item
    for item in document_items:
        if item.inventory_item_id:
            item.inventory_item = InventoryItem.query.get(item.inventory_item_id)
        else:
            item.inventory_item = None
    
    return render_template('invoices/form.html', 
                         invoice=document, 
                         clients=clients, 
                         inventory_items=inventory_items,
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

        if new_doc_type != document.type or not request.form.get('document_number'):
            company_id_str = str(company_id)
            type_letter = 'I' if new_doc_type == DocumentType.invoice else 'Q'

            try:
                seq_num = int(document.document_number.split('-')[-1])
            except Exception:
                seq_num = None

            if seq_num is not None:
                new_number = f"{type_letter}-{company_id_str}-{seq_num:06d}"
                exists = Document.query.filter(
                    Document.company_id == company_id,
                    Document.type == new_doc_type,
                    Document.document_number == new_number,
                    Document.id != document.id
                ).first()
                if exists:
                    raise ValueError(_("Document number already exists"))

                document.document_number = new_number
            else:
                last_doc = Document.query.filter(
                    Document.company_id == company_id,
                    Document.type == new_doc_type
                ).order_by(Document.id.desc()).first()

                last_seq = (
                    int(last_doc.document_number.split('-')[-1])
                    if last_doc else 0
                )

                document.document_number = (
                    f"{type_letter}-{company_id_str}-{last_seq + 1:06d}"
                )
        else:
            document.document_number = request.form.get(
                'document_number',
                document.document_number
            )

        document.type = new_doc_type
        document.client_id = (
            int(request.form.get('client_id'))
            if request.form.get('client_id') else None
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
        # Delete related items first
        DocumentItem.query.filter_by(document_id=document.id).delete()
        
        # Delete the document
        db.session.delete(document)
        db.session.commit()
        
        doc_type_name = _('Invoice') if document.type == DocumentType.invoice else _('Quote')
        flash(_(f'{doc_type_name} deleted successfully'), 'success')
    except Exception as e:
        db.session.rollback()
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
        pdf_bytes, filename = generate_invoice_pdf(
            document=document,
            request=request
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