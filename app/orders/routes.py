import csv
from io import StringIO
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, desc, asc, func
from flask_babel import _

from models import db, PurchaseOrder, PurchaseOrderItem, Supplier, InventoryItem

from . import orders

@orders.route('/<int:company_id>/purchase-orders')
@login_required
def index(company_id):
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 15))
    
    query = PurchaseOrder.query.filter_by(company_id=company_id)
    
    # Apply search filter
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            or_(
                PurchaseOrder.order_number.ilike(f'%{search}%'),
                PurchaseOrder.supplier.has(Supplier.name.ilike(f'%{search}%'))
            )
        )
    
    # Apply supplier filter
    supplier_id = request.args.get('supplier_id', '')
    if supplier_id and supplier_id.isdigit():
        query = query.filter_by(supplier_id=int(supplier_id))
    
    # Apply sorting
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    
    if sort_by == 'order_number':
        query = query.order_by(asc(PurchaseOrder.order_number) if sort_order == 'asc' else desc(PurchaseOrder.order_number))
    elif sort_by == 'total_amount':
        query = query.order_by(asc(PurchaseOrder.total_amount) if sort_order == 'asc' else desc(PurchaseOrder.total_amount))
    elif sort_by == 'created_at':
        query = query.order_by(asc(PurchaseOrder.created_at) if sort_order == 'asc' else desc(PurchaseOrder.created_at))
    else:
        query = query.order_by(desc(PurchaseOrder.created_at))
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    purchase_orders = pagination.items
    
    # Filter options
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    
    # Stats
    total_orders = PurchaseOrder.query.filter_by(company_id=company_id).count()
    total_value = db.session.query(func.sum(PurchaseOrder.total_amount))\
        .filter_by(company_id=company_id).scalar() or 0
    recent_orders = PurchaseOrder.query.filter_by(company_id=company_id)\
        .filter(PurchaseOrder.created_at >= datetime.now().replace(day=1)).count()
    avg_order_value = total_value / total_orders if total_orders > 0 else 0
    
    stats = {
        'total_orders': total_orders,
        'total_value': total_value,
        'recent_orders': recent_orders,
        'avg_order_value': avg_order_value
    }

    # Remove conflicting query parameters
    from werkzeug.datastructures import MultiDict
    filtered_args = MultiDict(request.args)
    filtered_args.pop('sort', None)
    filtered_args.pop('order', None)

    return render_template('orders/index.html', 
                          company_id=company_id,
                          orders=purchase_orders, 
                          pagination=pagination,
                          suppliers=suppliers,
                          stats=stats,
                          search=search,
                          supplier_id=supplier_id,
                          sort_by=sort_by,
                          sort_order=sort_order,
                          filtered_args=filtered_args)

@orders.route('/<int:company_id>/purchase-orders/create', methods=['GET', 'POST'])
@login_required
def create(company_id):
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).order_by(InventoryItem.name).all()
    
    if request.method == 'POST':
        try:
            supplier_id = request.form.get('supplier_id')
            
            # Validation
            if not supplier_id or not supplier_id.isdigit():
                flash(_('Supplier is required'), 'error')
                return render_template('orders/form.html', 
                                     company_id=company_id, 
                                     suppliers=suppliers,
                                     inventory_items=inventory_items,
                                     purchase_order=None, 
                                     form_data=request.form)
            
            # Generate order number
            last_order = PurchaseOrder.query.filter_by(company_id=company_id)\
                .order_by(desc(PurchaseOrder.id)).first()
            order_number = f"PO-{company_id}-{(last_order.id + 1) if last_order else 1:06d}"
            
            # Create purchase order
            purchase_order = PurchaseOrder(
                company_id=company_id, # type: ignore
                order_number=order_number, # type: ignore
                supplier_id=int(supplier_id), # type: ignore
                total_amount=0.0 # type: ignore
            )
            
            db.session.add(purchase_order)
            db.session.flush()  # Get the ID
            
            # Process items
            total_amount = 0.0
            item_count = 0
            
            for key in request.form.keys():
                if key.startswith('item_') and key.endswith('_id'):
                    current_app.logger.debug(f"Processing key: {key}")
                    index = key.split('_')[1]
                    item_id = request.form.get(f'item_{index}_id')
                    code = request.form.get(f'item_{index}_code')
                    quantity = request.form.get(f'item_{index}_quantity')
                    price = request.form.get(f'item_{index}_price')
                    
                    if item_id and quantity and price:
                        try:
                            quantity = int(quantity)
                            price = float(price)
                            
                            if quantity > 0 and price >= 0:
                                inventory_item = InventoryItem.query.get(int(item_id))
                                if inventory_item and inventory_item.company_id == company_id:
                                    item_total = quantity * price
                                    
                                    po_item = PurchaseOrderItem(
                                        purchase_order_id=purchase_order.id, # type: ignore
                                        inventory_item_id=int(item_id), # type: ignore
                                        name=inventory_item.name, # type: ignore
                                        item_code=code, # type: ignore
                                        quantity=quantity, # type: ignore
                                        price=price, # type: ignore
                                        total=item_total # type: ignore
                                    )
                                    
                                    db.session.add(po_item)
                                    total_amount += item_total
                                    item_count += 1
                                    current_app.logger.debug(f"item counter: {item_count}")
                        except (ValueError, TypeError):
                            continue
            
            if item_count == 0:
                flash(_('At least one item is required'), 'error')
                db.session.rollback()
                return render_template('orders/form.html', 
                                     company_id=company_id, 
                                     suppliers=suppliers,
                                     inventory_items=inventory_items,
                                     purchase_order=None, 
                                     form_data=request.form)
            
            purchase_order.total_amount = total_amount
            db.session.commit()
            
            flash(_('Purchase order created successfully'), 'success')
            return redirect(url_for('orders.view', company_id=company_id, id=purchase_order.id))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(_('An error occurred while creating the purchase order'), 'error')
            current_app.logger.error(f"Database error: {str(e)}")
            return render_template('orders/form.html', 
                                 company_id=company_id, 
                                 suppliers=suppliers,
                                 inventory_items=inventory_items,
                                 purchase_order=None, 
                                 form_data=request.form)
    
    return render_template('orders/form.html', 
                          company_id=company_id, 
                          suppliers=suppliers,
                          inventory_items=inventory_items,
                          purchase_order=None, 
                          form_data=None)

@orders.route('/<int:company_id>/purchase-orders/<int:id>')
@login_required
def view(company_id, id):
    purchase_order = PurchaseOrder.query.filter_by(id=id, company_id=company_id).first_or_404()
    return render_template('orders/view.html', company_id=company_id, order=purchase_order)

@orders.route('/<int:company_id>/purchase-orders/<int:id>/edit', methods=['GET'])
@login_required
def edit(company_id, id):
    purchase_order = PurchaseOrder.query.filter_by(id=id, company_id=company_id).first_or_404()
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).order_by(InventoryItem.name).all()
    
    return render_template('orders/form.html', 
                          company_id=company_id, 
                          suppliers=suppliers,
                          inventory_items=inventory_items,
                          order=purchase_order, 
                          form_data=None)

@orders.route('/<int:company_id>/purchase-orders/<int:id>/update', methods=['POST'])
@login_required
def update(company_id, id):
    purchase_order = PurchaseOrder.query.filter_by(id=id, company_id=company_id).first_or_404()
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).order_by(InventoryItem.name).all()
    
    try:
        supplier_id = request.form.get('supplier_id')
        
        # Validation
        if not supplier_id or not supplier_id.isdigit():
            flash(_('Supplier is required'), 'error')
            return render_template('orders/form.html', 
                                 company_id=company_id, 
                                 suppliers=suppliers,
                                 inventory_items=inventory_items,
                                 purchase_order=purchase_order, 
                                 form_data=request.form)
        
        purchase_order.supplier_id = int(supplier_id)
        
        # Delete existing items
        PurchaseOrderItem.query.filter_by(purchase_order_id=purchase_order.id).delete()
        
        # Process new items
        total_amount = 0.0
        item_count = 0
        
        for key in request.form.keys():
            if key.startswith('item_') and key.endswith('_id'):
                index = key.split('_')[1]
                item_id = request.form.get(f'item_{index}_id')
                code = request.form.get(f'item_{index}_code')
                quantity = request.form.get(f'item_{index}_quantity')
                price = request.form.get(f'item_{index}_price')
                
                if item_id and quantity and price:
                    try:
                        quantity = int(quantity)
                        price = float(price)
                        
                        if quantity > 0 and price >= 0:
                            inventory_item = InventoryItem.query.get(int(item_id))
                            if inventory_item and inventory_item.company_id == company_id:
                                item_total = quantity * price
                                
                                po_item = PurchaseOrderItem(
                                    purchase_order_id=purchase_order.id, # type: ignore
                                    inventory_item_id=int(item_id), # type: ignore
                                    name=inventory_item.name, # type: ignore
                                    item_code=code, # type: ignore
                                    quantity=quantity, # type: ignore
                                    price=price, # type: ignore
                                    total=item_total # type: ignore
                                )
                                
                                db.session.add(po_item)
                                total_amount += item_total
                                item_count += 1
                    except (ValueError, TypeError):
                        continue
        
        if item_count == 0:
            flash(_('At least one item is required'), 'error')
            return render_template('orders/form.html', 
                                 company_id=company_id, 
                                 suppliers=suppliers,
                                 inventory_items=inventory_items,
                                 purchase_order=purchase_order, 
                                 form_data=request.form)
        
        purchase_order.total_amount = total_amount
        db.session.commit()
        
        flash(_('Purchase order updated successfully'), 'success')
        return redirect(url_for('orders.view', company_id=company_id, id=purchase_order.id))
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(_('An error occurred while updating the purchase order'), 'error')
        current_app.logger.error(f"Database error: {str(e)}")
        return render_template('orders/form.html', 
                             company_id=company_id, 
                             suppliers=suppliers,
                             inventory_items=inventory_items,
                             purchase_order=purchase_order, 
                             form_data=request.form)

@orders.route('/<int:company_id>/purchase-orders/<int:id>/delete', methods=['POST'])
@login_required
def delete(company_id, id):
    purchase_order = PurchaseOrder.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    try:
        db.session.delete(purchase_order)
        db.session.commit()
        flash(_('Purchase order deleted successfully'), 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(_('An error occurred while deleting the purchase order'), 'error')
        current_app.logger.error(f"Database error: {str(e)}")
    
    return redirect(url_for('orders.index', company_id=company_id))

@orders.route('/<int:company_id>/purchase-orders/export')
@login_required
def export(company_id):
    orders = PurchaseOrder.query.filter_by(company_id=company_id).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        _('Order Number'), _('Supplier'), _('Total Amount'), _('Items Count'), _('Created Date')
    ])
    
    # Write data
    for order in orders:
        writer.writerow([
            order.order_number,
            order.supplier.name if order.supplier else '',
            order.total_amount,
            len(order.items),
            order.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    output.seek(0)
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=purchase_orders_{company_id}_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

# API Routes
@orders.route('/api/<int:company_id>/purchase-orders', methods=['GET'])
@login_required
def api_get_orders(company_id):
    """Get all purchase orders with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '')
    supplier_id = request.args.get('supplier_id', type=int)
    
    query = PurchaseOrder.query.filter_by(company_id=company_id)
    
    if search:
        query = query.filter(
            or_(
                PurchaseOrder.order_number.ilike(f'%{search}%'),
                PurchaseOrder.supplier.has(Supplier.name.ilike(f'%{search}%'))
            )
        )
    
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items
    
    return jsonify({
        'orders': [{
            'id': order.id,
            'order_number': order.order_number,
            'supplier_id': order.supplier_id,
            'supplier_name': order.supplier.name if order.supplier else None,
            'total_amount': order.total_amount,
            'items_count': len(order.items),
            'created_at': order.created_at.isoformat()
        } for order in orders],
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@orders.route('/api/<int:company_id>/purchase-orders/<int:id>/receive', methods=['POST'])
@login_required
def api_receive_order(company_id, id):
    """Receive purchase order items and update inventory"""
    purchase_order = PurchaseOrder.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    try:
        for item in purchase_order.items:
            inventory_item = item.inventory_item
            if inventory_item:
                inventory_item.quantity += item.quantity
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': _('Purchase order received and inventory updated')
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Receive order error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500