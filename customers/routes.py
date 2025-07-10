from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import _, get_locale
from sqlalchemy import or_
import math

from models import Client, Document, DocumentType, db

from . import customers

@customers.route('/<int:company_id>/clients')
@login_required
def index(company_id = None):
    """
    Display list of clients with pagination and search functionality
    """
    # Get the current user's active company
    if not current_user.companies:
        flash(_('You need to be associated with a company to view clients'), 'error')
        return redirect(url_for('dashboard.index'))
    
    # Use the first company if user has multiple (you might want to add company selection UI)
    if not company_id and current_user.companies:
        company_id = current_user.companies[0].id
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_dir = request.args.get('sort_dir', 'asc')
    
    # Base query - filter by company_id
    query = Client.query.filter_by(company_id=company_id)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Client.name.ilike(search_term),
                Client.email.ilike(search_term),
                Client.phone.ilike(search_term),
                Client.address.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort_by == 'name':
        if sort_dir == 'asc':
            query = query.order_by(Client.name.asc())
        else:
            query = query.order_by(Client.name.desc())
    elif sort_by == 'email':
        if sort_dir == 'asc':
            query = query.order_by(Client.email.asc())
        else:
            query = query.order_by(Client.email.desc())
    elif sort_by == 'created_at':
        if sort_dir == 'asc':
            query = query.order_by(Client.created_at.asc())
        else:
            query = query.order_by(Client.created_at.desc())
    
    # Get total count for pagination
    total_clients = query.count()
    total_pages = math.ceil(total_clients / per_page) if total_clients > 0 else 1
    
    # Apply pagination
    clients = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Get client statistics
    client_stats = {}
    for client in clients:
        # Count documents for each client - filter by company_id
        client_stats[client.id] = {
            'total_invoices': Document.query.filter_by(
                client_id=client.id,
                company_id=company_id,
                type=DocumentType.invoice
            ).count(),
            'total_quotes': Document.query.filter_by(
                client_id=client.id,
                company_id=company_id,
                type=DocumentType.quote
            ).count(),
            'outstanding_amount': db.session.query(
                db.func.sum(Document.total_amount)
            ).filter(
                Document.client_id == client.id,
                Document.company_id == company_id,
                Document.type == DocumentType.invoice,
                Document.status != 'paid'
            ).scalar() or 0
        }
    
    # Prepare pagination links
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_items': total_clients,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
    }
    
    # Get current locale for formatting
    current_locale = get_locale()
    
    # Get company name for display
    company_name = next((c.name for c in current_user.companies if c.id == company_id), '')
    
    return render_template(
        'customers/index.html',
        clients=clients,
        client_stats=client_stats,
        pagination=pagination,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page_title=_('Clients'),
        current_locale=current_locale,
        company_name=company_name,
        company_id=company_id
    )

@customers.route('/<int:company_id>/create', methods=['GET'])
@login_required
def create(company_id = None):
    """Display client creation form"""
    # Get the current user's active company
    if not current_user.companies:
        flash(_('You need to be associated with a company to create clients'), 'error')
        return redirect(url_for('dashboard.index'))
    
    if not company_id and current_user.companies:
        company_id = current_user.companies[0].id
    
    return render_template(
        'customers/form.html',
        client=None,
        form_action=url_for('customers.store', company_id=company_id),
        page_title=_('Create Client'),
        company_id=company_id
    )

@customers.route('/<int:company_id>/store', methods=['POST'])
@login_required
def store(company_id = None):
    """Store a new client"""
    # Validate company access
    if not company_id or not any(c.id == company_id for c in current_user.companies):
        flash(_('Invalid company selected'), 'error')
        return redirect(url_for('customers.index'))
    
    # Extract form data
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    identifier = request.form.get('identifier', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # Validate required fields
    if not name:
        flash(_('Client name is required'), 'error')
        return redirect(url_for('customers.create', company_id=company_id))
    
    # Check for duplicate email if provided - within the same company
    if email and Client.query.filter_by(email=email, company_id=company_id).first():
        flash(_('A client with this email already exists in this company'), 'error')
        return redirect(url_for('customers.create', company_id=company_id))
    
    # Create new client
    client = Client(
        company_id=company_id,
        name=name,
        email=email,
        identifier=identifier,
        phone=phone,
        address=address
    )
    
    # Save to database
    db.session.add(client)
    db.session.commit()
    
    flash(_('Client created successfully'), 'success')
    return redirect(url_for('customers.index', company_id=company_id))

@customers.route('/<int:company_id>/<int:id>/edit', methods=['GET'])
@login_required
def edit(company_id = None, id = 0):
    """Display client edit form"""
    client = Client.query.get_or_404(id)
    
    # Verify company access
    if not any(c.id == client.company_id for c in current_user.companies):
        flash(_('You do not have access to this client'), 'error')
        return redirect(url_for('customers.index'))
    
    return render_template(
        'customers/form.html',
        client=client,
        form_action=url_for('customers.update', company_id=company_id, id=id),
        page_title=_('Edit Client'),
        company_id=client.company_id
    )

@customers.route('/<int:id>/update', methods=['POST'])
@login_required
def update(id = 0):
    """Update an existing client"""
    client = Client.query.get_or_404(id)
    
    # Verify company access
    if not any(c.id == client.company_id for c in current_user.companies):
        flash(_('You do not have access to this client'), 'error')
        return redirect(url_for('customers.index'))
    
    # Extract form data
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    identifier = request.form.get('identifier', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # Validate required fields
    if not name:
        flash(_('Client name is required'), 'error')
        return redirect(url_for('customers.edit', id=id))
    
    # Check for duplicate email if changed - within the same company
    if email and email != client.email and Client.query.filter_by(email=email, company_id=client.company_id).first():
        flash(_('A client with this email already exists in this company'), 'error')
        return redirect(url_for('customers.edit', id=id))
    
    # Update client
    client.name = name
    client.email = email
    client.identifier = identifier
    client.phone = phone
    client.address = address
    
    # Save to database
    db.session.commit()
    
    flash(_('Client updated successfully'), 'success')
    return redirect(url_for('customers.index', company_id=client.company_id))

@customers.route('/<int:company_id>/<int:id>/delete', methods=['POST'])
@login_required
def delete(company_id = None, id = 0):
    """Delete a client"""
    client = Client.query.get_or_404(id)
    
    # Verify company access
    if not any(c.id == client.company_id for c in current_user.companies):
        flash(_('You do not have access to this client'), 'error')
        return redirect(url_for('customers.index'))
    
    # Check if client has associated documents
    has_documents = Document.query.filter_by(
        client_id=id, 
        company_id=company_id
    ).first() is not None
    
    if has_documents:
        flash(_('Cannot delete client with associated documents'), 'error')
        return redirect(url_for('customers.index', company_id=company_id))
    
    # Delete client
    db.session.delete(client)
    db.session.commit()
    
    flash(_('Client deleted successfully'), 'success')
    return redirect(url_for('customers.index', company_id=company_id))

@customers.route('/<int:company_id>/<int:id>/view', methods=['GET'])
@login_required
def view(company_id = None, id = 0):
    """View client details"""
    client = Client.query.get_or_404(id)
    
    # Verify company access
    if not any(c.id == client.company_id for c in current_user.companies):
        flash(_('You do not have access to this client'), 'error')
        return redirect(url_for('customers.index'))
    
    # Get client documents - filter by company_id
    invoices = Document.query.filter_by(
        client_id=id,
        company_id=client.company_id,
        type=DocumentType.invoice
    ).order_by(Document.issued_date.desc()).all()
    
    quotes = Document.query.filter_by(
        client_id=id,
        company_id=client.company_id,
        type=DocumentType.quote
    ).order_by(Document.issued_date.desc()).all()
    
    # Calculate statistics
    total_invoiced = db.session.query(
        db.func.sum(Document.total_amount)
    ).filter(
        Document.client_id == id,
        Document.company_id == client.company_id,
        Document.type == DocumentType.invoice
    ).scalar() or 0
    
    outstanding_amount = db.session.query(
        db.func.sum(Document.total_amount)
    ).filter(
        Document.client_id == id,
        Document.company_id == client.company_id,
        Document.type == DocumentType.invoice,
        Document.status != 'paid'
    ).scalar() or 0
    
    return render_template(
        'customers/view.html',
        client=client,
        invoices=invoices,
        quotes=quotes,
        total_invoiced=total_invoiced,
        outstanding_amount=outstanding_amount,
        page_title=_('Client Details'),
        company_id=company_id
    )