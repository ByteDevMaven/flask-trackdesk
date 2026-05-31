import math
from datetime import datetime, UTC
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import _
from . import contacts
from app.models import db, Contact, Company, user_companies, Role, Document, InventoryItem
from app.models.enums import ContactType
from sqlalchemy import exc

@contacts.route('/<int:company_id>/contacts', methods=['GET'])
@login_required
def index(company_id):
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    contact_type_filter = request.args.get('type', '', type=str)
    per_page = 20

    query = Contact.query.filter_by(company_id=company_id)

    if contact_type_filter in ['customer', 'supplier']:
        query = query.filter_by(type=ContactType[contact_type_filter])

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Contact.name.ilike(search_term)) |
            (Contact.email.ilike(search_term)) |
            (Contact.identifier.ilike(search_term)) |
            (Contact.phone.ilike(search_term))
        )
    
    total_contacts = query.count()
    total_pages = math.ceil(total_contacts / per_page) if per_page else 1
    
    contacts_paginated = query.order_by(Contact.name).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'contacts/index.html',
        contacts=contacts_paginated,
        search=search,
        contact_type_filter=contact_type_filter,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        companies=[],
        selected_company_id=company_id,
        ContactType=ContactType
    )

@contacts.route('/<int:company_id>/contacts/create', methods=['GET', 'POST'])
@login_required
def create(company_id):
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash(_('Contact name is required'), 'error')
            return redirect(url_for('contacts.create', company_id=company_id))

        contact_type_str = request.form.get('type', 'customer')
        contact_type = ContactType[contact_type_str] if contact_type_str in ['customer', 'supplier'] else ContactType.customer

        contact = Contact(
            company_id=company_id,
            name=name,
            type=contact_type,
            identifier=request.form.get('identifier', ''),
            email=request.form.get('email', ''),
            phone=request.form.get('phone', ''),
            address=request.form.get('address', '')
        )
        
        try:
            db.session.add(contact)
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': _('Contact created successfully'),
                    'contact': {
                        'id': contact.id,
                        'name': contact.name,
                        'email': contact.email
                    }
                })
            flash(_('Contact created successfully'), 'success')
            return redirect(url_for('contacts.index', company_id=company_id))
        except exc.IntegrityError:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': _('A database error occurred.')})
            flash(_('Error creating contact'), 'error')
            return redirect(url_for('contacts.create', company_id=company_id))

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    return render_template(
        'contacts/form.html', 
        contact=None,
        company_id=company_id,
        is_ajax=is_ajax,
        ContactType=ContactType
    )

@contacts.route('/<int:company_id>/contacts/<int:contact_id>', methods=['GET'])
@login_required
def view(company_id, contact_id):
    contact = Contact.query.filter_by(id=contact_id, company_id=company_id).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    per_page = 15
    stats = {}
    items = None

    if contact.type.name == 'customer':
        items = Document.query.filter_by(client_id=contact.id).order_by(Document.issued_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        all_docs = Document.query.filter_by(client_id=contact.id).all()
        
        total_revenue = sum(doc.calculate_paid_amount() for doc in all_docs)
        pending_payments = sum(doc.calculate_balance_due() for doc in all_docs)
        total_invoices = len(all_docs)
        
        stats = {
            'total_revenue': total_revenue,
            'pending_payments': pending_payments,
            'total_invoices': total_invoices
        }
    else:
        items = InventoryItem.query.filter_by(supplier_id=contact.id).order_by(InventoryItem.name).paginate(page=page, per_page=per_page, error_out=False)
        all_items = InventoryItem.query.filter_by(supplier_id=contact.id).all()
        
        total_inventory_value = sum((item.price or 0) * (item.quantity or 0) for item in all_items)
        total_products = len(all_items)
        low_stock_products = sum(1 for item in all_items if (item.quantity or 0) <= 5)
        
        stats = {
            'total_value': total_inventory_value,
            'total_products': total_products,
            'low_stock': low_stock_products
        }

    return render_template(
        'contacts/view.html',
        contact=contact,
        company_id=company_id,
        ContactType=ContactType,
        items=items,
        stats=stats
    )

@contacts.route('/<int:company_id>/contacts/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(company_id, contact_id):
    contact = Contact.query.filter_by(id=contact_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash(_('Contact name is required'), 'error')
            return redirect(url_for('contacts.edit', company_id=company_id, contact_id=contact.id))

        contact_type_str = request.form.get('type')
        if contact_type_str in ['customer', 'supplier']:
            contact.type = ContactType[contact_type_str]
            
        contact.name = name
        contact.identifier = request.form.get('identifier', '')
        contact.email = request.form.get('email', '')
        contact.phone = request.form.get('phone', '')
        contact.address = request.form.get('address', '')
        
        try:
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': _('Contact updated successfully')})
            flash(_('Contact updated successfully'), 'success')
            return redirect(url_for('contacts.index', company_id=company_id))
        except exc.IntegrityError:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': _('A database error occurred.')})
            flash(_('Error updating contact'), 'error')
            return redirect(url_for('contacts.edit', company_id=company_id, contact_id=contact.id))

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    return render_template(
        'contacts/form.html', 
        contact=contact,
        company_id=company_id,
        is_ajax=is_ajax,
        ContactType=ContactType
    )

@contacts.route('/<int:company_id>/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete(company_id, contact_id):
    contact = Contact.query.filter_by(id=contact_id, company_id=company_id).first_or_404()
    try:
        contact.is_deleted = True
        contact.deleted_at = datetime.now(UTC)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': _('Contact deleted successfully')})
        flash(_('Contact deleted successfully'), 'success')
        return redirect(url_for('contacts.index', company_id=company_id))
    except exc.IntegrityError:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False, 
                'error': _('Cannot delete contact because it has related records (invoices, items, etc).')
            })
        flash(_('Cannot delete contact because it has related records (invoices, items, etc).'), 'error')
        return redirect(url_for('contacts.index', company_id=company_id))

@contacts.route('/<int:company_id>/contacts/api/search', methods=['GET'])
@login_required
def api_search(company_id):
    search_term = request.args.get('q', '')
    contact_type = request.args.get('type', '')
    
    query = Contact.query.filter_by(company_id=company_id)
    if contact_type in ['customer', 'supplier']:
        query = query.filter_by(type=ContactType[contact_type])
        
    if search_term:
        query = query.filter(Contact.name.ilike(f'%{search_term}%'))
        
    contacts = query.order_by(Contact.name).limit(10).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'identifier': c.identifier,
        'email': c.email
    } for c in contacts])
