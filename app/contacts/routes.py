from app.utils import resolve_company
import math
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from flask_babel import _
from . import contacts
from app.models.enums import ContactType
from sqlalchemy import exc

from .services import ContactService

@contacts.route('/<string:company_id>/contacts', methods=['GET'])
@login_required
def index(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    contact_type_filter = request.args.get('type', '', type=str)
    per_page = 20

    contacts_paginated, total_pages = ContactService.get_paginated_contacts(
        company_id, page, per_page, search, contact_type_filter
    )

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

@contacts.route('/<string:company_id>/contacts/create', methods=['GET', 'POST'])
@login_required
def create(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    if request.method == 'POST':
        try:
            contact = ContactService.create_contact(company_id, request.form)
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
        except ValueError as e:
            flash(_(str(e)), 'error')
            return redirect(url_for('contacts.create', company_id=company_id))
        except exc.IntegrityError:
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

@contacts.route('/<string:company_id>/contacts/<int:contact_id>', methods=['GET'])
@login_required
def view(company_id, contact_id):
    company = resolve_company(company_id)
    company_id = company.id
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    contact, items, stats = ContactService.get_contact_with_stats(company_id, contact_id, page, per_page)

    return render_template(
        'contacts/view.html',
        contact=contact,
        company_id=company_id,
        ContactType=ContactType,
        items=items,
        stats=stats
    )

@contacts.route('/<string:company_id>/contacts/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(company_id, contact_id):
    company = resolve_company(company_id)
    company_id = company.id
    # Fetch contact details to populate form for GET request
    contact, _, _ = ContactService.get_contact_with_stats(company_id, contact_id, 1, 1)

    if request.method == 'POST':
        try:
            ContactService.update_contact(company_id, contact_id, request.form)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': _('Contact updated successfully')})
            flash(_('Contact updated successfully'), 'success')
            return redirect(url_for('contacts.index', company_id=company_id))
        except ValueError as e:
            flash(_(str(e)), 'error')
            return redirect(url_for('contacts.edit', company_id=company_id, contact_id=contact_id))
        except exc.IntegrityError:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': _('A database error occurred.')})
            flash(_('Error updating contact'), 'error')
            return redirect(url_for('contacts.edit', company_id=company_id, contact_id=contact_id))

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    return render_template(
        'contacts/form.html', 
        contact=contact,
        company_id=company_id,
        is_ajax=is_ajax,
        ContactType=ContactType
    )

@contacts.route('/<string:company_id>/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete(company_id, contact_id):
    company = resolve_company(company_id)
    company_id = company.id
    try:
        ContactService.delete_contact(company_id, contact_id)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': _('Contact deleted successfully')})
        flash(_('Contact deleted successfully'), 'success')
        return redirect(url_for('contacts.index', company_id=company_id))
    except exc.IntegrityError:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False, 
                'error': _('Cannot delete contact because it has related records (invoices, items, etc).')
            })
        flash(_('Cannot delete contact because it has related records (invoices, items, etc).'), 'error')
        return redirect(url_for('contacts.index', company_id=company_id))

@contacts.route('/<string:company_id>/contacts/api/search', methods=['GET'])
@login_required
def api_search(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    search_term = request.args.get('q', '')
    contact_type = request.args.get('type', '')
    
    contacts = ContactService.search_contacts(company_id, search_term, contact_type)
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'identifier': c.identifier,
        'email': c.email
    } for c in contacts])
