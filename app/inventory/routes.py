from app.utils import resolve_company
import io
from flask import render_template, request, redirect, session, url_for, flash, current_app, jsonify, Response, send_file
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from flask_babel import _

from app.models import db, InventoryItem, Contact
from app.extensions import limiter

from . import inventory
from app.models.enums import ContactType
from .services import InventoryService

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
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    
                                                         
    pagination = InventoryService.get_inventory_items(
        company_id=company_id,
        page=page,
        per_page=per_page,
        search=search,
        supplier_id=supplier_id,
        sort_by=sort_by,
        sort_order=sort_order
    )
    inventory_items = pagination.items
    
                    
    suppliers = Contact.query.filter_by(company_id=company_id, type=ContactType.supplier).order_by(Contact.name).all()
    
           
    stats = InventoryService.get_inventory_stats(company_id)

    return render_template('inventory/index.html', 
                          company_id=company_id,
                          inventory_items=inventory_items, 
                          pagination=pagination,
                          suppliers=suppliers,
                          stats=stats,
                          search=search,
                          supplier_id=supplier_id,
                          sort_by=sort_by,
                          sort_order=sort_order)

@inventory.route('/<string:company_id>/inventory/create_item', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def create(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Warehouse
    suppliers = Contact.query.filter_by(company_id=company_id, type=ContactType.supplier).order_by(Contact.name).all()
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
                warehouse_id=request.form.get('warehouse_id'),
                sku=request.form.get('sku', '').strip() or None
            )
            flash(_('Inventory item created successfully'), 'success')
            return redirect(url_for('inventory.view', company_id=company_id, sku=item.sku))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, warehouses=warehouses, selected_id=selected_id, item=None, form_data=request.form)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(_('An error occurred while creating the inventory item'), 'error')
            current_app.logger.error(f"Database error: {str(e)}")
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, warehouses=warehouses, selected_id=selected_id, item=None, form_data=request.form)
    
    return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, warehouses=warehouses, selected_id=selected_id, item=None, form_data=None)

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

@inventory.route('/<string:company_id>/inventory/movements')
@login_required
@limiter.exempt
def movements(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 20))
    search = request.args.get('search', '')
    movement_type = request.args.get('type')
    period = request.args.get('period', 'all')
    client_id = request.args.get('client_id', type=int)
    supplier_id = request.args.get('supplier_id', type=int)
    
    pagination = InventoryService.get_stock_movements(
        company_id=company_id,
        movement_type=movement_type,
        period=period,
        search=search,
        client_id=client_id,
        supplier_id=supplier_id,
        page=page,
        per_page=per_page
    )
    movements = pagination.items
    
    from app.models import Contact
    from app.models.enums import ContactType
    clients = Contact.query.filter_by(company_id=company_id, type=ContactType.customer).order_by(Contact.name).all()
    suppliers = Contact.query.filter_by(company_id=company_id, type=ContactType.supplier).order_by(Contact.name).all()
    
    return render_template('inventory/movements.html',
                          company_id=company_id,
                          movements=movements,
                          pagination=pagination,
                          search=search,
                          movement_type=movement_type,
                          period=period,
                          clients=clients,
                          suppliers=suppliers,
                          client_id=client_id,
                          supplier_id=supplier_id)

@inventory.route('/<string:company_id>/inventory/<string:sku>/edit_item', methods=['GET'])
@login_required
@limiter.exempt
def edit(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    from app.models import Warehouse
    suppliers = Contact.query.filter_by(company_id=company_id, type=ContactType.supplier).order_by(Contact.name).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    selected_id = request.args.get('supplier_id', type=int)
    
    return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, warehouses=warehouses, selected_id=selected_id, item=item, form_data=None)

@inventory.route('/<string:company_id>/inventory/<string:sku>/update_item', methods=['POST'])
@login_required
@limiter.exempt
def update(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    from app.models import Warehouse
    suppliers = Contact.query.filter_by(company_id=company_id, type=ContactType.supplier).order_by(Contact.name).all()
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
            sku=request.form.get('sku', '').strip() or None
        )
        
        # Reload item to get potentially updated SKU
        item = InventoryItem.query.get(item.id)
        flash(_('Inventory item updated successfully'), 'success')
        return redirect(url_for('inventory.view', company_id=company_id, sku=item.sku))
        
    except ValueError as e:
        flash(str(e), 'error')
        return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, warehouses=warehouses, item=item, form_data=request.form)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(_('An error occurred while updating the inventory item'), 'error')
        current_app.logger.error(f"Database error: {str(e)}")
        return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, warehouses=warehouses, item=item, form_data=request.form)

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
        flash(_('Inventory item deleted successfully'), 'success')
    except Exception as e:
        flash(_('An error occurred while deleting the inventory item'), 'error')
        current_app.logger.error(f"Delete error: {str(e)}")
    
    return redirect(url_for('inventory.index', company_id=company_id))

@inventory.route('/<string:company_id>/inventory/export')
@login_required
@limiter.exempt
def export(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    import io
    from flask import send_file
    
    search = request.args.get('search', '')
    supplier_id = request.args.get('supplier_id', type=int)
    
    wb, filename = InventoryService.export_inventory_items_xlsx(
        company_id=company_id,
        search=search,
        supplier_id=supplier_id
    )
    
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    
    return send_file(
        out,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@inventory.route('/<string:company_id>/inventory/movements/export')
@login_required
@limiter.exempt
def export_movements(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    search = request.args.get('search', '')
    movement_type = request.args.get('type')
    period = request.args.get('period', 'all')
    client_id = request.args.get('client_id', type=int)
    supplier_id = request.args.get('supplier_id', type=int)
    
    wb, filename = InventoryService.export_stock_movements_xlsx(
        company_id=company_id,
        movement_type=movement_type,
        period=period,
        search=search,
        client_id=client_id,
        supplier_id=supplier_id
    )
    
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    
    return send_file(
        out,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@inventory.route('/<string:company_id>/inventory/<string:sku>/drawer_adjust', methods=['GET'])
@login_required
@limiter.exempt
def drawer_adjust(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    from app.models import Warehouse
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    return render_template('inventory/drawer_adjust.html', company_id=company_id, item=item, warehouses=warehouses)

@inventory.route('/<string:company_id>/inventory/<string:sku>/drawer_transfer', methods=['GET'])
@login_required
@limiter.exempt
def drawer_transfer(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    from app.models import Warehouse
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()
    return render_template('inventory/drawer_transfer.html', company_id=company_id, item=item, warehouses=warehouses)

@inventory.route('/<string:company_id>/inventory/<string:sku>/transfer', methods=['POST'])
@login_required
@limiter.exempt
def transfer(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    from_warehouse_id = request.form.get('from_warehouse_id', type=int)
    to_warehouse_id = request.form.get('to_warehouse_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if not from_warehouse_id or not to_warehouse_id or not quantity:
        if is_ajax: return jsonify({'success': False, 'error': _('All fields are required for transfer')})
        flash(_('All fields are required for transfer'), 'error')
        return redirect(url_for('inventory.view', company_id=company_id, sku=sku))
        
    if from_warehouse_id == to_warehouse_id:
        if is_ajax: return jsonify({'success': False, 'error': _('Source and destination warehouses must be different')})
        flash(_('Source and destination warehouses must be different'), 'error')
        return redirect(url_for('inventory.view', company_id=company_id, sku=sku))
        
    try:
        InventoryService.transfer_stock(
            company_id=company_id,
            item_id=item.id,
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id,
            quantity=quantity
        )
        if is_ajax: return jsonify({'success': True, 'message': _('Stock transferred successfully')})
        flash(_('Stock transferred successfully'), 'success')
    except ValueError as e:
        if is_ajax: return jsonify({'success': False, 'error': str(e)})
        flash(str(e), 'error')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Transfer error: {str(e)}")
        if is_ajax: return jsonify({'success': False, 'error': _('An error occurred during transfer')})
        flash(_('An error occurred during transfer'), 'error')
        
    if is_ajax: return jsonify({'success': False, 'error': _('Unknown error')})
    return redirect(url_for('inventory.view', company_id=company_id, sku=sku))

@inventory.route('/api/<string:company_id>/inventory/items', methods=['GET'])
@login_required
@limiter.exempt
def api_get_items(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    """Get all inventory items with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '')
    supplier_id = request.args.get('supplier_id')
    
    pagination = InventoryService.get_inventory_items(
        company_id=company_id,
        page=page,
        per_page=per_page,
        search=search,
        supplier_id=supplier_id
    )
    items = pagination.items
    
    return jsonify({
        'items': [{
            'id': item.id,
            'sku': item.sku,
            'barcode': item.generated_tag,
            'name': item.name,
            'description': item.description,
            'quantity': item.quantity,
            'price': item.price,
            'supplier_id': item.supplier_id,
            'supplier_name': item.supplier.name if item.supplier else None
        } for item in items],
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@inventory.route('/api/<string:company_id>/inventory/items/<int:id>', methods=['GET'])
@login_required
@limiter.exempt
def api_get_item(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    """Get a specific inventory item"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    return jsonify({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'quantity': item.quantity,
        'price': item.price,
        'supplier_id': item.supplier_id,
        'supplier_name': item.supplier.name if item.supplier else None
    })

@inventory.route('/api/<string:company_id>/inventory/items', methods=['POST'])
@login_required
@limiter.exempt
def api_create_item(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    """Create a new inventory item"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        item = InventoryService.create_inventory_item(
            company_id=company_id,
            name=data.get('name'),
            description=data.get('description'),
            quantity=data.get('quantity', 0),
            price=data.get('price', 0.0),
            cost_price=data.get('cost_price', 0.0),
            discount=data.get('discount', 0.0),
            supplier_id=data.get('supplier_id')
        )
        
        return jsonify({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'quantity': item.quantity,
            'price': item.price,
            'cost_price': item.cost_price,
            'discount': item.discount,
            'supplier_id': item.supplier_id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"API create error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<string:company_id>/inventory/items/<int:id>', methods=['PUT'])
@login_required
@limiter.exempt
def api_update_item(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    """Update an inventory item"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        item = InventoryService.update_inventory_item(
            company_id=company_id,
            item_id=id,
            name=data.get('name'),
            description=data.get('description'),
            quantity=data.get('quantity'),
            price=data.get('price'),
            cost_price=data.get('cost_price'),
            discount=data.get('discount'),
            supplier_id=data.get('supplier_id')
        )
        
        return jsonify({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'quantity': item.quantity,
            'price': item.price,
            'cost_price': item.cost_price,
            'discount': item.discount,
            'supplier_id': item.supplier_id
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"API update error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<string:company_id>/inventory/items/<int:id>', methods=['DELETE'])
@login_required
@limiter.exempt
def api_delete_item(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    """Delete an inventory item"""
    try:
        InventoryService.delete_inventory_item(company_id, id)
        return jsonify({'message': 'Item deleted successfully'})
        
    except SQLAlchemyError as e:
        current_app.logger.error(f"API delete error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@inventory.route('/api/<string:company_id>/inventory/items/bulk-delete', methods=['POST'])
@login_required
@limiter.exempt
def api_bulk_delete(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    """Bulk delete inventory items"""
    data = request.get_json()
    item_ids = data.get('item_ids', []) if data else []
    
    if not item_ids:
        return jsonify({'error': 'No items selected'}), 400
    
    try:
        deleted_count = InventoryService.bulk_delete_items(company_id, item_ids)
        return jsonify({
            'message': f'{deleted_count} items deleted successfully',
            'deleted_count': deleted_count
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Bulk delete error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<string:company_id>/inventory/items/<int:id>/adjust-stock', methods=['POST'])
@login_required
@limiter.exempt
def api_adjust_stock(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    """Adjust stock quantity for an item"""
    data = request.get_json()
    adjustment = int(data.get('adjustment', 0)) if data else 0
    warehouse_id = data.get('warehouse_id')
    
    if not warehouse_id:
        return jsonify({'error': 'Warehouse ID is required'}), 400
        
    try:
        new_quantity = InventoryService.adjust_stock(
            company_id=company_id,
            item_id=id,
            warehouse_id=int(warehouse_id),
            adjustment=adjustment
        )

        return jsonify({
            'success': True,
            'id': id,
            'new_quantity': new_quantity,
            'adjustment': adjustment,
            'message': _('Stock adjusted successfully')
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Stock adjustment error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<string:company_id>/inventory/search', methods=['GET'])
@login_required
@limiter.exempt
def api_search(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    """Search inventory items"""
    query = request.args.get('q', '').strip()
    items = InventoryService.search_inventory_items(company_id, query)
    
    results = []
    for item in items:
        results.append({
            'id': item.id,
            'sku': item.sku,
            'barcode': item.generated_tag,
            'name': item.name,
            'quantity': item.quantity,
            'price': item.price,
            'description': item.description
        })
    
    return jsonify(results)

@inventory.route('/api/<string:company_id>/inventory/stats', methods=['GET'])
@login_required
@limiter.exempt
def api_stats(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    """Get inventory statistics"""
    stats = InventoryService.get_inventory_stats(company_id)
    return jsonify(stats)

@inventory.route('/<string:company_id>/inventory/<string:sku>/barcode')
@login_required
@limiter.exempt
def barcode(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    """Barcode label for an inventory item"""
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    copies = request.args.get('copies', 12, type=int)
    currency_symbol = session.get('currency', '$')
    barcode_value = item.generated_tag

    return render_template('inventory/barcode.html',
                          company_id=company_id,
                          item=item,
                          copies=copies,
                          currency_symbol=currency_symbol,
                          barcode_value=barcode_value)
