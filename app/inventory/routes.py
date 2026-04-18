import csv
from io import StringIO
from datetime import datetime

from flask import render_template, request, redirect, session, url_for, flash, current_app, jsonify
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from flask_babel import _

from models import db, InventoryItem, Supplier
from extensions import limiter

from . import inventory
from .services import InventoryService

@inventory.route('/<int:company_id>/inventory')
@login_required
@limiter.exempt
def index(company_id):
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 15))
    
    # Get filters and sorting from request
    search = request.args.get('search', '')
    supplier_id = request.args.get('supplier_id', '')
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    
    # Apply sorting and pagination using InventoryService
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
    
    # Filter options
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    
    # Stats
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

@inventory.route('/<int:company_id>/inventory/create_item', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def create(company_id):
    # Get suppliers for dropdown
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    selected_id = request.args.get('supplier_id', type=int)
    
    if request.method == 'POST':
        try:
            InventoryService.create_inventory_item(
                company_id=company_id,
                name=request.form.get('name', '').strip(),
                description=request.form.get('description', '').strip(),
                quantity=int(request.form.get('quantity', 0)),
                price=float(request.form.get('price', 0.0)),
                supplier_id=request.form.get('supplier_id')
            )
            flash(_('Inventory item created successfully'), 'success')
            return redirect(url_for('inventory.index', company_id=company_id))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=None, form_data=request.form)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(_('An error occurred while creating the inventory item'), 'error')
            current_app.logger.error(f"Database error: {str(e)}")
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=None, form_data=request.form)
    
    return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=None, form_data=None)

@inventory.route('/<int:company_id>/inventory/<int:id>')
@login_required
@limiter.exempt
def view(company_id, id):
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    # Fetch movements using InventoryService
    pagination = InventoryService.get_stock_movements(company_id, item_id=id, per_page=100)
    db_movements = pagination.items
    
    movements = []
    for m in db_movements:
        movements.append({
            'date': m.date,
            'type': m.type.value.title(),
            'reference': m.reference or '-',
            'qty_change': m.quantity,
            'status': 'completed', # All movements in this table are considered completed
            'notes': m.notes
        })
    
    return render_template('inventory/view.html', 
                          company_id=company_id, 
                          item=item,
                          movements=movements)

@inventory.route('/<int:company_id>/inventory/movements')
@login_required
@limiter.exempt
def movements(company_id):
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 20))
    search = request.args.get('search', '')
    movement_type = request.args.get('type')
    period = request.args.get('period', 'all')
    
    pagination = InventoryService.get_stock_movements(
        company_id=company_id,
        movement_type=movement_type,
        period=period,
        search=search,
        page=page,
        per_page=per_page
    )
    movements = pagination.items
    
    return render_template('inventory/movements.html',
                          company_id=company_id,
                          movements=movements,
                          pagination=pagination,
                          search=search,
                          movement_type=movement_type,
                          period=period)

@inventory.route('/<int:company_id>/inventory/<int:id>/edit_item', methods=['GET'])
@login_required
@limiter.exempt
def edit(company_id, id):
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    selected_id = request.args.get('supplier_id', type=int)
    
    return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=item, form_data=None)

@inventory.route('/<int:company_id>/inventory/<int:id>/update_item', methods=['POST'])
@login_required
@limiter.exempt
def update(company_id, id):
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    
    try:
        InventoryService.update_inventory_item(
            company_id=company_id,
            item_id=id,
            name=request.form.get('name', '').strip(),
            description=request.form.get('description', '').strip(),
            quantity=int(request.form.get('quantity', 0)),
            price=float(request.form.get('price', 0.0)),
            supplier_id=request.form.get('supplier_id')
        )
        
        flash(_('Inventory item updated successfully'), 'success')
        return redirect(url_for('inventory.index', company_id=company_id))
        
    except ValueError as e:
        flash(str(e), 'error')
        return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, item=item, form_data=request.form)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(_('An error occurred while updating the inventory item'), 'error')
        current_app.logger.error(f"Database error: {str(e)}")
        return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, item=item, form_data=request.form)

@inventory.route('/<int:company_id>/inventory/<int:id>/delete_item', methods=['POST'])
@login_required
def delete(company_id, id):
    try:
        InventoryService.delete_inventory_item(company_id, id)
        flash(_('Inventory item deleted successfully'), 'success')
    except Exception as e:
        flash(_('An error occurred while deleting the inventory item'), 'error')
        current_app.logger.error(f"Delete error: {str(e)}")
    
    return redirect(url_for('inventory.index', company_id=company_id))

@inventory.route('/<int:company_id>/inventory/export')
@login_required
@limiter.exempt
def export(company_id):
    items = InventoryItem.query.filter_by(company_id=company_id).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Name'), _('Description'), _('Quantity'), _('Price'), _('Supplier')
    ])
    
    # Write data
    for item in items:
        writer.writerow([
            item.name,
            item.description or '',
            item.quantity,
            item.price,
            item.supplier.name if item.supplier else ''
        ])
    
    output.seek(0)
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=inventory_{company_id}_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

# API Routes
@inventory.route('/api/<int:company_id>/inventory/items', methods=['GET'])
@login_required
@limiter.exempt
def api_get_items(company_id):
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

@inventory.route('/api/<int:company_id>/inventory/items/<int:id>', methods=['GET'])
@login_required
@limiter.exempt
def api_get_item(company_id, id):
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

@inventory.route('/api/<int:company_id>/inventory/items', methods=['POST'])
@login_required
@limiter.exempt
def api_create_item(company_id):
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
            supplier_id=data.get('supplier_id')
        )
        
        return jsonify({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'quantity': item.quantity,
            'price': item.price,
            'supplier_id': item.supplier_id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"API create error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<int:company_id>/inventory/items/<int:id>', methods=['PUT'])
@login_required
@limiter.exempt
def api_update_item(company_id, id):
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
            supplier_id=data.get('supplier_id')
        )
        
        return jsonify({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'quantity': item.quantity,
            'price': item.price,
            'supplier_id': item.supplier_id
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"API update error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<int:company_id>/inventory/items/<int:id>', methods=['DELETE'])
@login_required
@limiter.exempt
def api_delete_item(company_id, id):
    """Delete an inventory item"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"API delete error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<int:company_id>/inventory/items/bulk-delete', methods=['POST'])
@login_required
@limiter.exempt
def api_bulk_delete(company_id):
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

@inventory.route('/api/<int:company_id>/inventory/items/<int:id>/adjust-stock', methods=['POST'])
@login_required
@limiter.exempt
def api_adjust_stock(company_id, id):
    """Adjust stock quantity for an item"""
    data = request.get_json()
    adjustment = int(data.get('adjustment', 0)) if data else 0
    
    try:
        new_quantity = InventoryService.adjust_stock(
            company_id=company_id,
            item_id=id,
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

@inventory.route('/api/<int:company_id>/inventory/search', methods=['GET'])
@login_required
@limiter.exempt
def api_search(company_id):
    """Search inventory items"""
    query = request.args.get('q', '').strip()
    items = InventoryService.search_inventory_items(company_id, query)
    
    results = []
    for item in items:
        results.append({
            'id': item.id,
            'name': item.name,
            'quantity': item.quantity,
            'price': item.price,
            'description': item.description
        })
    
    return jsonify(results)

@inventory.route('/api/<int:company_id>/inventory/stats', methods=['GET'])
@login_required
@limiter.exempt
def api_stats(company_id):
    """Get inventory statistics"""
    stats = InventoryService.get_inventory_stats(company_id)
    return jsonify(stats)

@inventory.route('/<int:company_id>/inventory/<int:id>/barcode')
@login_required
@limiter.exempt
def view_barcode(company_id, id):
    """Generate and return barcode image for an inventory item"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    try:
        currency_symbol = session.get('currency', '$')
        output_buffer, barcode_data = InventoryService.generate_barcode_image(
            company_id=company_id, 
            item_id=item.id, 
            item_name=item.name, 
            item_price=item.price, 
            currency_symbol=currency_symbol,
            for_download=False,
            compact=False
        )
        from flask import Response
        return Response(
            output_buffer.getvalue(),
            mimetype='image/png',
            headers={'Content-Disposition': f'inline; filename=barcode_{barcode_data}.png'}
        )
        
    except Exception as e:
        current_app.logger.error(f"Barcode generation error: {str(e)}")
        # Return a simple error response or default image
        from flask import Response
        return Response('Barcode generation failed', status=500)

@inventory.route('/<int:company_id>/inventory/<int:id>/barcode/download')
@login_required
@limiter.exempt
def download_barcode(company_id, id):
    """Download barcode as PNG file"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    try:
        currency_symbol = session.get('currency', '$')
        output_buffer, barcode_data = InventoryService.generate_barcode_image(
            company_id=company_id, 
            item_id=item.id, 
            item_name=item.name, 
            item_price=item.price, 
            currency_symbol=currency_symbol,
            for_download=True,
            compact=False
        )
        
        from flask import Response
        return Response(
            output_buffer.getvalue(),
            mimetype='image/png',
            headers={
                'Content-Disposition': f'attachment; filename=barcode_{item.name.replace(" ", "_")}_{barcode_data}.png'
            }
        )
        
    except Exception as e:
        current_app.logger.error(f"Barcode download error: {str(e)}")
        flash(_('An error occurred while generating the barcode'), 'error')
        return redirect(url_for('inventory.view', company_id=company_id, id=id))

@inventory.route('/<int:company_id>/inventory/<int:id>/print-barcodes')
@login_required
@limiter.exempt
def print_barcodes(company_id, id):
    """Print multiple tight-packed barcodes on a letter-sized page"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    copies = request.args.get('copies', 48, type=int)
    
    try:
        currency_symbol = session.get('currency', '$')
        import base64
        output_buffer, barcode_data = InventoryService.generate_barcode_image(
            company_id=company_id, 
            item_id=item.id, 
            item_name=item.name, 
            item_price=item.price, 
            currency_symbol=currency_symbol,
            for_download=False,
            compact=True
        )
        barcode_b64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
    except Exception as e:
        current_app.logger.error(f"Barcode print prep error: {str(e)}")
        flash(_('An error occurred while generating the printable barcodes'), 'error')
        return redirect(url_for('inventory.view', company_id=company_id, id=id))

    return render_template('inventory/print_barcodes.html',
                          company_id=company_id,
                          item=item,
                          copies=copies,
                          barcode_b64=barcode_b64)
