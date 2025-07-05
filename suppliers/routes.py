import math

from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from flask_babel import _

from models import db, Supplier, Company, InventoryItem, user_companies

from . import suppliers

@suppliers.route('/<int:company_id>/suppliers')
@login_required
def index(company_id = None):
    # Get company context
    if not company_id and 'selected_company_id' in session:
        company_id = session['selected_company_id']
    
    # If user has access to multiple companies, get the list for the dropdown
    user_companies_query = db.session.query(user_companies).filter_by(user_id=current_user.id).all()
    companies = []
    if len(user_companies_query) > 1:
        companies = Company.query.filter(Company.id.in_([uc.company_id for uc in user_companies_query])).all()
    
    # Ensure user has access to the selected company
    if company_id:
        has_access = db.session.query(user_companies).filter_by(
            user_id=current_user.id, 
            company_id=company_id
        ).first()
        if not has_access:
            flash(_('You do not have access to this company'), 'error')
            return redirect(url_for('suppliers.index', company_id=company_id))
        session['selected_company_id'] = company_id
    elif user_companies_query:
        # Default to first company user has access to
        company_id = user_companies_query[0].company_id
        session['selected_company_id'] = company_id
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Base query with company filter
    query = Supplier.query.filter_by(company_id=company_id)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Supplier.name.ilike(search_term)) |
            (Supplier.contact_email.ilike(search_term)) |
            (Supplier.phone.ilike(search_term))
        )
    
    # Get total count for pagination
    total_suppliers = query.count()
    total_pages = math.ceil(total_suppliers / per_page)
    
    # Get paginated suppliers
    suppliers = query.order_by(Supplier.name).paginate(page=page, per_page=per_page)
    
    # Get stats
    stats = {
        'total': total_suppliers,
        'with_items': db.session.query(Supplier.id).join(InventoryItem).filter(Supplier.company_id == company_id).distinct().count(),
        'without_items': total_suppliers - db.session.query(Supplier.id).join(InventoryItem).filter(Supplier.company_id == company_id).distinct().count()
    }
    
    return render_template(
        'suppliers/index.html',
        suppliers=suppliers,
        stats=stats,
        search=search,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        companies=companies,
        selected_company_id=company_id
    )

@suppliers.route('/<int:company_id>/create_supplier', methods=['GET', 'POST'])
@login_required
def create(company_id = None):
    if not company_id:
        flash(_('Please select a company first'), 'warning')
        return redirect(url_for('suppliers.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        contact_email = request.form.get('contact_email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if not name:
            flash(_('Supplier name is required'), 'error')
            return render_template(
                'suppliers/form.html',
                supplier=None,
                company_id=company_id,
                action='create'
            )
        
        supplier = Supplier(
            name=name,
            contact_email=contact_email,
            phone=phone,
            address=address,
            company_id=company_id
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        flash(_('Supplier created successfully'), 'success')
        return redirect(url_for('suppliers.index', company_id=company_id))
    
    return render_template(
        'suppliers/form.html',
        supplier=None,
        company_id=company_id,
        action='create'
    )

@suppliers.route('/<int:company_id>/<int:supplier_id>/edit_supplier', methods=['GET', 'POST'])
@login_required
def edit(company_id, supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id, company_id=company_id).first_or_404()
    
    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.contact_email = request.form.get('contact_email')
        supplier.phone = request.form.get('phone')
        supplier.address = request.form.get('address')
        
        if not supplier.name:
            flash(_('Supplier name is required'), 'error')
            return render_template(
                'suppliers/form.html',
                supplier=supplier,
                company_id=company_id,
                action='edit'
            )
        
        db.session.commit()
        
        flash(_('Supplier updated successfully'), 'success')
        return redirect(url_for('suppliers.view', supplier_id=supplier.id, company_id=company_id))
    
    return render_template(
        'suppliers/form.html',
        supplier=supplier,
        company_id=company_id,
        action='edit'
    )

@suppliers.route('/<int:company_id>/<int:supplier_id>/supplier')
@login_required
def view(company_id, supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id, company_id=company_id).first_or_404()
    
    # Get inventory items for this supplier
    inventory_items = InventoryItem.query.filter_by(
        supplier_id=supplier.id,
        company_id=company_id
    ).all()
    
    return render_template(
        'suppliers/view.html',
        supplier=supplier,
        inventory_items=inventory_items,
        company_id=company_id
    )

@suppliers.route('/<int:company_id>/<int:supplier_id>/delete_supplier', methods=['POST'])
@login_required
def delete(company_id, supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id, company_id=company_id).first_or_404()
    
    # Check if supplier has inventory items
    has_items = InventoryItem.query.filter_by(supplier_id=supplier.id).first() is not None
    
    if has_items:
        flash(_('Cannot delete supplier with associated inventory items'), 'error')
        return redirect(url_for('suppliers.view', supplier_id=supplier.id, company_id=company_id))
    
    db.session.delete(supplier)
    db.session.commit()
    
    flash(_('Supplier deleted successfully'), 'success')
    return redirect(url_for('suppliers.index', company_id=company_id))

@suppliers.route('/api/list_suppliers')
@login_required
def api_list():
    company_id = session.get('selected_company_id')
    search = request.args.get('search', '')
    
    query = Supplier.query.filter_by(company_id=company_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(Supplier.name.ilike(search_term))
    
    suppliers = query.order_by(Supplier.name).limit(10).all()
    
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'contact_email': s.contact_email,
        'phone': s.phone
    } for s in suppliers])
