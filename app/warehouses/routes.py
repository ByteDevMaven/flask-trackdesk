from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from flask_wtf.csrf import validate_csrf
from flask_babel import _
from wtforms import ValidationError

from . import warehouses
from app.extensions import limiter
from .services import WarehouseService

@warehouses.route('/<int:company_id>/warehouses/create', methods=['GET'])
@login_required
@limiter.exempt
def create(company_id):
    return render_template('warehouses/form.html', warehouse=None, company_id=company_id)

@warehouses.route('/<int:company_id>/warehouses/<int:id>/edit', methods=['GET'])
@login_required
@limiter.exempt
def edit(company_id, id):
    warehouse = WarehouseService.get_warehouse(company_id, id)
    return render_template('warehouses/form.html', warehouse=warehouse, company_id=company_id)

@warehouses.route('/<int:company_id>/warehouses')
@login_required
@limiter.exempt
def index(company_id):
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    pagination = WarehouseService.get_paginated_warehouses(company_id, page, 10, search)
    
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
        flash(_("Token CSRF inválido. Por favor, inténtelo de nuevo."), "error")
        return redirect(url_for("warehouses.index", company_id=company_id))
        
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        WarehouseService.create_warehouse(company_id, request.form)
        
        if is_ajax:
            return jsonify({
                'success': True,
                'message': _('Almacén creado con éxito')
            })
            
        flash(_('Almacén creado con éxito'), 'success')
        return redirect(url_for('warehouses.index', company_id=company_id))
    except ValueError as e:
        if is_ajax:
            return jsonify({'success': False, 'error': str(e)})
        flash(str(e), 'error')
        return redirect(url_for('warehouses.index', company_id=company_id))

@warehouses.route('/<int:company_id>/warehouses/<int:id>/update', methods=['POST'])
@login_required
def update(company_id, id):
    csrf_token = request.form.get("csrf_token")
    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Token CSRF inválido. Por favor, inténtelo de nuevo."), "error")
        return redirect(url_for("warehouses.index", company_id=company_id))
        
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        WarehouseService.update_warehouse(company_id, id, request.form)
        
        if is_ajax:
            return jsonify({
                'success': True,
                'message': _('Almacén actualizado con éxito')
            })
            
        flash(_('Almacén actualizado con éxito'), 'success')
        return redirect(url_for('warehouses.index', company_id=company_id))
    except ValueError as e:
        if is_ajax:
            return jsonify({'success': False, 'error': str(e)})
        flash(str(e), 'error')
        return redirect(url_for('warehouses.index', company_id=company_id))
