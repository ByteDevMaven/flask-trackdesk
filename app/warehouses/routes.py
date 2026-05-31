from flask import render_template, request, redirect, session, url_for, flash, jsonify
from flask_login import login_required
from flask_wtf.csrf import validate_csrf
from flask_babel import _
from wtforms import ValidationError

from app.models import db, Warehouse
from . import warehouses
from app.extensions import limiter

@warehouses.route('/<int:company_id>/warehouses/create', methods=['GET'])
@login_required
@limiter.exempt
def create(company_id):
    return render_template('warehouses/form.html', warehouse=None, company_id=company_id)

@warehouses.route('/<int:company_id>/warehouses/<int:id>/edit', methods=['GET'])
@login_required
@limiter.exempt
def edit(company_id, id):
    warehouse = Warehouse.query.filter_by(id=id, company_id=company_id).first_or_404()
    return render_template('warehouses/form.html', warehouse=warehouse, company_id=company_id)


@warehouses.route('/<int:company_id>/warehouses')
@login_required
@limiter.exempt
def index(company_id):
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Warehouse.query.filter_by(company_id=company_id)
    if search:
        query = query.filter(Warehouse.name.ilike(f'%{search}%') | Warehouse.location.ilike(f'%{search}%'))
        
    pagination = query.order_by(Warehouse.id.asc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('warehouses/index.html',
                           company_id=company_id,
                           warehouses=pagination.items,
                           pagination=pagination,
                           search=search)

@warehouses.route('/<int:company_id>/warehouses/store', methods=['POST'])
@login_required
def store(company_id):
    csrf_token = request.form.get("csrf_token")
    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("warehouses.index", company_id=company_id))
        
    name = request.form.get('name')
    location = request.form.get('location', '')
    is_active = request.form.get('is_active') == 'on'
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if not name:
        if is_ajax:
            return jsonify({'success': False, 'error': _('Warehouse name is required')})
        flash(_('Warehouse name is required'), 'error')
        return redirect(url_for('warehouses.index', company_id=company_id))
        
    exists = Warehouse.query.filter_by(company_id=company_id, name=name).first()
    if exists:
        if is_ajax:
            return jsonify({'success': False, 'error': _('Warehouse with this name already exists')})
        flash(_('Warehouse with this name already exists'), 'error')
        return redirect(url_for('warehouses.index', company_id=company_id))
        
    warehouse = Warehouse(
        company_id=company_id,
        name=name,
        location=location,
        is_active=is_active
    )
    
    db.session.add(warehouse)
    db.session.commit()
    
    if is_ajax:
        return jsonify({
            'success': True,
            'message': _('Warehouse created successfully')
        })
        
    flash(_('Warehouse created successfully'), 'success')
    return redirect(url_for('warehouses.index', company_id=company_id))

@warehouses.route('/<int:company_id>/warehouses/<int:id>/update', methods=['POST'])
@login_required
def update(company_id, id):
    csrf_token = request.form.get("csrf_token")
    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("warehouses.index", company_id=company_id))
        
    warehouse = Warehouse.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    name = request.form.get('name')
    location = request.form.get('location', '')
    is_active = request.form.get('is_active') == 'on'
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if not name:
        if is_ajax:
            return jsonify({'success': False, 'error': _('Warehouse name is required')})
        flash(_('Warehouse name is required'), 'error')
        return redirect(url_for('warehouses.index', company_id=company_id))
        
    exists = Warehouse.query.filter(Warehouse.company_id == company_id, Warehouse.name == name, Warehouse.id != id).first()
    if exists:
        if is_ajax:
            return jsonify({'success': False, 'error': _('Another warehouse with this name already exists')})
        flash(_('Another warehouse with this name already exists'), 'error')
        return redirect(url_for('warehouses.index', company_id=company_id))
        
    warehouse.name = name
    warehouse.location = location
    warehouse.is_active = is_active
    
    db.session.commit()
    
    if is_ajax:
        return jsonify({
            'success': True,
            'message': _('Warehouse updated successfully')
        })
        
    flash(_('Warehouse updated successfully'), 'success')
    return redirect(url_for('warehouses.index', company_id=company_id))
