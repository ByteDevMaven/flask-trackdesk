import io

from flask import Response, current_app, flash, jsonify, redirect, render_template, request, send_file, session, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import limiter
from app.models import Contact, InventoryItem, db
from app.models.enums import ContactType
from app.utils import resolve_company

from .. import inventory
from ..services import InventoryService


@inventory.route('/<string:company_id>/inventory/categories', methods=['GET'])
@login_required
@limiter.exempt
def categories(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.inventory.services.category_service import CategoryService
    categories = CategoryService.get_categories(company_id)
    return render_template('inventory/categories.html', company_id=company_id, categories=categories)


@inventory.route('/<string:company_id>/inventory/categories/create', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def create_category(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.inventory.services.category_service import CategoryService
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            CategoryService.create_category(company_id, name, description)
            flash('Category created successfully', 'success')
            return redirect(url_for('inventory.categories', company_id=company_id))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('inventory/category_form.html', company_id=company_id, category=None, form_data=request.form)
            
    return render_template('inventory/category_form.html', company_id=company_id, category=None, form_data=None)


@inventory.route('/<string:company_id>/inventory/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def edit_category(company_id, category_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.inventory.services.category_service import CategoryService
    
    category = CategoryService.get_category(company_id, category_id)
    if not category:
        from flask import abort; abort(404)
        
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            CategoryService.update_category(company_id, category_id, name, description)
            flash('Category updated successfully', 'success')
            return redirect(url_for('inventory.categories', company_id=company_id))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('inventory/category_form.html', company_id=company_id, category=category, form_data=request.form)
            
    return render_template('inventory/category_form.html', company_id=company_id, category=category, form_data=None)


@inventory.route('/<string:company_id>/inventory/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@limiter.exempt
def delete_category(company_id, category_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.inventory.services.category_service import CategoryService
    
    try:
        CategoryService.delete_category(company_id, category_id)
        flash('Category deleted successfully', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('An error occurred while deleting the category', 'error')
        current_app.logger.error(f"Category delete error: {str(e)}")
        
    return redirect(url_for('inventory.categories', company_id=company_id))
