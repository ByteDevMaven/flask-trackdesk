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


def _get_suppliers(company_id):
    return Contact.query.filter(
        Contact.company_id == company_id,
        Contact.type.in_([ContactType.supplier, ContactType.customer_supplier]),
    ).order_by(Contact.name).all()


@inventory.route('/<string:company_id>/inventory')
@login_required
@limiter.exempt
def index(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 15))
    
                                          
    search = request.args.get('search', '')
    supplier_id = request.args.get('supplier_id', '')
    category_id_filter = request.args.get('category_id', type=int)
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    
                                                         
    pagination = InventoryService.get_inventory_items(
        company_id=company_id,
        page=page,
        per_page=per_page,
        search=search,
        supplier_id=supplier_id,
        category_id=category_id_filter,
        sort_by=sort_by,
        sort_order=sort_order
    )
    inventory_items = pagination.items
    
                    
    suppliers = _get_suppliers(company_id)
    
    from app.models import Category
    categories = Category.query.filter_by(company_id=company_id).order_by(Category.name).all()
    
       
    stats = InventoryService.get_inventory_stats(company_id)

    return render_template('inventory/index.html', 
                          company_id=company_id,
                          inventory_items=inventory_items, 
                          pagination=pagination,
                          suppliers=suppliers,
                          categories=categories,
                          stats=stats,
                          search=search,
                          supplier_id=supplier_id,
                          category_id=category_id_filter,
                          sort_by=sort_by,
                          sort_order=sort_order)


@inventory.route('/<string:company_id>/inventory/create_item', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def create(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Warehouse, Category
    suppliers = _get_suppliers(company_id)
    categories = Category.query.filter_by(company_id=company_id).order_by(Category.name).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    selected_id = request.args.get('supplier_id', type=int)
    
    if request.method == 'POST':
        try:
            item = InventoryService.create_inventory_item(
                company_id=company_id,
                name=request.form.get('name', '').strip(),
                description=request.form.get('description', '').strip(),
                quantity=int(request.form.get('quantity', 0)),
                price=float(request.form.get('price', 0.0)),
                cost_price=float(request.form.get('cost_price', 0.0) or 0.0),
                discount=float(request.form.get('discount', 0.0) or 0.0),
                supplier_id=request.form.get('supplier_id'),
                category_id=request.form.get('category_id'),
                is_service=request.form.get('is_service') == 'on',
                warehouse_id=request.form.get('warehouse_id'),
                sku=request.form.get('sku', '').strip() or None
            )
            flash('Inventory item created successfully', 'success')
            return redirect(url_for('inventory.view', company_id=company_id, sku=item.sku))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, categories=categories, warehouses=warehouses, selected_id=selected_id, item=None, form_data=request.form)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while creating the inventory item', 'error')
            current_app.logger.error(f"Database error: {str(e)}")
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, categories=categories, warehouses=warehouses, selected_id=selected_id, item=None, form_data=request.form)
    
    return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, categories=categories, warehouses=warehouses, selected_id=selected_id, item=None, form_data=None)


@inventory.route('/<string:company_id>/inventory/<string:sku>')
@login_required
@limiter.exempt
def view(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort
        abort(404)
    company = Company.query.get_or_404(company_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    pagination = InventoryService.get_stock_movements(company_id, item_id=item.id, page=page, per_page=per_page)
    db_movements = pagination.items
    
    movements = []
    for m in db_movements:
        movements.append({
            'date': m.date,
            'type': m.type.value,
            'reference': m.reference or '-',
            'warehouse': m.warehouse.name if m.warehouse else '-',
            'destination': m.destination_warehouse.name if m.destination_warehouse else '-',
            'qty_change': m.qty_change,
            'notes': m.notes
        })
    
    from app.models import Warehouse, WarehouseItem
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    warehouse_items = WarehouseItem.query.filter_by(inventory_item_id=item.id).all()
    
    return render_template('inventory/view.html',
                          company_id=company_id,
                          company=company,
                          item=item,
                          movements=movements,
                          pagination=pagination,
                          warehouses=warehouses,
                          warehouse_items=warehouse_items)


@inventory.route('/<string:company_id>/inventory/<string:sku>/edit_item', methods=['GET'])
@login_required
@limiter.exempt
def edit(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    from app.models import Warehouse, Category
    suppliers = _get_suppliers(company_id)
    categories = Category.query.filter_by(company_id=company_id).order_by(Category.name).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    selected_id = request.args.get('supplier_id', type=int)
    
    return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, categories=categories, warehouses=warehouses, selected_id=selected_id, item=item, form_data=None)


@inventory.route('/<string:company_id>/inventory/<string:sku>/update_item', methods=['POST'])
@login_required
@limiter.exempt
def update(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    from app.models import Warehouse, Category
    suppliers = _get_suppliers(company_id)
    categories = Category.query.filter_by(company_id=company_id).order_by(Category.name).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    
    try:
        InventoryService.update_inventory_item(
            company_id=company_id,
            item_id=item.id,
            name=request.form.get('name', '').strip(),
            description=request.form.get('description', '').strip(),
            quantity=int(request.form.get('quantity', 0)),
            price=float(request.form.get('price', 0.0)),
            cost_price=float(request.form.get('cost_price', 0.0) or 0.0),
            discount=float(request.form.get('discount', 0.0) or 0.0),
            supplier_id=request.form.get('supplier_id'),
            category_id=request.form.get('category_id'),
            is_service=request.form.get('is_service') == 'on',
            sku=request.form.get('sku', '').strip() or None
        )
        
        # Reload item to get potentially updated SKU
        item = InventoryItem.query.get(item.id)
        flash('Inventory item updated successfully', 'success')
        return redirect(url_for('inventory.view', company_id=company_id, sku=item.sku))
        
    except ValueError as e:
        flash(str(e), 'error')
        return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, categories=categories, warehouses=warehouses, item=item, form_data=request.form)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while updating the inventory item', 'error')
        current_app.logger.error(f"Database error: {str(e)}")
        return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, categories=categories, warehouses=warehouses, item=item, form_data=request.form)


@inventory.route('/<string:company_id>/inventory/<string:sku>/delete_item', methods=['POST'])
@login_required
def delete(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    try:
        InventoryService.delete_inventory_item(company_id, item.id)
        flash('Inventory item deleted successfully', 'success')
    except Exception as e:
        flash('An error occurred while deleting the inventory item', 'error')
        current_app.logger.error(f"Delete error: {str(e)}")
    
    return redirect(url_for('inventory.index', company_id=company_id))
