import csv
from io import StringIO, BytesIO
from datetime import datetime

import barcode
from flask import render_template, request, redirect, session, url_for, flash, current_app, jsonify
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, and_, desc, asc, func
from flask_babel import _
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

from models import db, InventoryItem, Supplier

from . import inventory

@inventory.route('/<int:company_id>/inventory')
@login_required
def index(company_id):
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 15))
    
    query = InventoryItem.query.filter_by(company_id=company_id)
    
    # Apply search filter
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            or_(
                InventoryItem.name.ilike(f'%{search}%'),
                InventoryItem.description.ilike(f'%{search}%')
            )
        )
    
    # Apply supplier filter
    supplier_id = request.args.get('supplier_id', '')
    if supplier_id and supplier_id.isdigit():
        query = query.filter_by(supplier_id=int(supplier_id))
    
    # Apply sorting
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    
    if sort_by == 'name':
        query = query.order_by(asc(InventoryItem.name) if sort_order == 'asc' else desc(InventoryItem.name))
    elif sort_by == 'quantity':
        query = query.order_by(asc(InventoryItem.quantity) if sort_order == 'asc' else desc(InventoryItem.quantity))
    elif sort_by == 'price':
        query = query.order_by(asc(InventoryItem.price) if sort_order == 'asc' else desc(InventoryItem.price))
    else:
        query = query.order_by(InventoryItem.name)
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    inventory_items = pagination.items
    
    # Filter options
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    
    # Stats
    total_items = InventoryItem.query.filter_by(company_id=company_id).count()
    low_stock_items = InventoryItem.query.filter(
        and_(InventoryItem.company_id == company_id, InventoryItem.quantity <= 10)
    ).count()
    out_of_stock_items = InventoryItem.query.filter(
        and_(InventoryItem.company_id == company_id, InventoryItem.quantity == 0)
    ).count()
    total_value = db.session.query(func.sum(InventoryItem.quantity * InventoryItem.price))\
        .filter_by(company_id=company_id).scalar() or 0
    
    stats = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'total_value': total_value
    }

    # Remove conflicting query parameters (sort/order)
    from werkzeug.datastructures import MultiDict
    filtered_args = MultiDict(request.args)
    filtered_args.pop('sort', None)
    filtered_args.pop('order', None)

    return render_template('inventory/index.html', 
                          company_id=company_id,
                          inventory_items=inventory_items, 
                          pagination=pagination,
                          suppliers=suppliers,
                          stats=stats,
                          search=search,
                          supplier_id=supplier_id,
                          sort_by=sort_by,
                          sort_order=sort_order,
                          filtered_args=filtered_args)

@inventory.route('/<int:company_id>/inventory/create_item', methods=['GET', 'POST'])
@login_required
def create(company_id):
    # Get suppliers for dropdown
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    selected_id = request.args.get('supplier_id', type=int)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            quantity = int(request.form.get('quantity', 0))
            price = float(request.form.get('price', 0.0))
            supplier_id = request.form.get('supplier_id')
            
            # Validation
            if not name:
                flash(_('Name is required'), 'error')
                return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=None, form_data=request.form)
            
            if quantity < 0:
                flash(_('Quantity cannot be negative'), 'error')
                return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=None, form_data=request.form)
            
            if price < 0:
                flash(_('Price cannot be negative'), 'error')
                return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=None, form_data=request.form)
            
            item = InventoryItem(
                company_id=company_id,
                name=name,
                description=description if description else None,
                quantity=quantity,
                price=price,
                supplier_id=int(supplier_id) if supplier_id and supplier_id.isdigit() else None
            )
            
            db.session.add(item)
            db.session.commit()
            
            flash(_('Inventory item created successfully'), 'success')
            return redirect(url_for('inventory.index', company_id=company_id))
            
        except (ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            flash(_('An error occurred while creating the inventory item'), 'error')
            current_app.logger.error(f"Database error: {str(e)}")
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=None, form_data=request.form)
    
    return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=None, form_data=None)

@inventory.route('/<int:company_id>/inventory/<int:id>')
@login_required
def view(company_id, id):
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    return render_template('inventory/view.html', company_id=company_id, item=item)

@inventory.route('/<int:company_id>/inventory/<int:id>/edit_item', methods=['GET'])
@login_required
def edit(company_id, id):
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    selected_id = request.args.get('supplier_id', type=int)
    
    return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, selected_id=selected_id, item=item, form_data=None)

@inventory.route('/<int:company_id>/inventory/<int:id>/update_item', methods=['POST'])
@login_required
def update(company_id, id):
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    suppliers = Supplier.query.filter_by(company_id=company_id).order_by(Supplier.name).all()
    
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        quantity = int(request.form.get('quantity', 0))
        price = float(request.form.get('price', 0.0))
        supplier_id = request.form.get('supplier_id')
        
        # Validation
        if not name:
            flash(_('Name is required'), 'error')
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, item=item, form_data=request.form)
        
        if quantity < 0:
            flash(_('Quantity cannot be negative'), 'error')
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, item=item, form_data=request.form)
        
        if price < 0:
            flash(_('Price cannot be negative'), 'error')
            return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, item=item, form_data=request.form)
        
        item.name = name
        item.description = description if description else None
        item.quantity = quantity
        item.price = price
        item.supplier_id = int(supplier_id) if supplier_id and supplier_id.isdigit() else None
        
        db.session.commit()
        
        flash(_('Inventory item updated successfully'), 'success')
        return redirect(url_for('inventory.index', company_id=company_id))
        
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        flash(_('An error occurred while updating the inventory item'), 'error')
        current_app.logger.error(f"Database error: {str(e)}")
        return render_template('inventory/form.html', company_id=company_id, suppliers=suppliers, item=item, form_data=request.form)

@inventory.route('/<int:company_id>/inventory/<int:id>/delete_item', methods=['POST'])
@login_required
def delete(company_id, id):
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    try:
        db.session.delete(item)
        db.session.commit()
        flash(_('Inventory item deleted successfully'), 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(_('An error occurred while deleting the inventory item'), 'error')
        current_app.logger.error(f"Database error: {str(e)}")
    
    return redirect(url_for('inventory.index', company_id=company_id))

@inventory.route('/<int:company_id>/inventory/export')
@login_required
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
def api_get_items(company_id):
    """Get all inventory items with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '')
    supplier_id = request.args.get('supplier_id', type=int)
    
    query = InventoryItem.query.filter_by(company_id=company_id)
    
    if search:
        query = query.filter(
            or_(
                InventoryItem.name.ilike(f'%{search}%'),
                InventoryItem.description.ilike(f'%{search}%')
            )
        )
    
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
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
def api_create_item(company_id):
    """Create a new inventory item"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Validation
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        quantity = data.get('quantity', 0)
        price = data.get('price', 0.0)
        
        if quantity < 0:
            return jsonify({'error': 'Quantity cannot be negative'}), 400
        
        if price < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
        
        item = InventoryItem(
            company_id=company_id,
            name=data['name'],
            description=data.get('description'),
            quantity=quantity,
            price=price,
            supplier_id=data.get('supplier_id')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'quantity': item.quantity,
            'price': item.price,
            'supplier_id': item.supplier_id
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"API create error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<int:company_id>/inventory/items/<int:id>', methods=['PUT'])
@login_required
def api_update_item(company_id, id):
    """Update an inventory item"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Validation
        if 'name' in data and not data['name']:
            return jsonify({'error': 'Name is required'}), 400
        
        if 'quantity' in data and data['quantity'] < 0:
            return jsonify({'error': 'Quantity cannot be negative'}), 400
        
        if 'price' in data and data['price'] < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
        
        # Update fields
        for field in ['name', 'description', 'quantity', 'price', 'supplier_id']:
            if field in data:
                setattr(item, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'quantity': item.quantity,
            'price': item.price,
            'supplier_id': item.supplier_id
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"API update error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@inventory.route('/api/<int:company_id>/inventory/items/<int:id>', methods=['DELETE'])
@login_required
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
def api_bulk_delete(company_id):
    """Bulk delete inventory items"""
    data = request.get_json()
    item_ids = data.get('item_ids', []) if data else []
    
    if not item_ids:
        return jsonify({'error': 'No items selected'}), 400
    
    try:
        deleted_count = InventoryItem.query.filter(
            and_(InventoryItem.id.in_(item_ids), InventoryItem.company_id == company_id)
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
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
def api_adjust_stock(company_id, id):
    """Adjust stock quantity for an item"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    data = request.get_json()
    adjustment = data.get('adjustment', 0) if data else 0
    
    try:
        new_quantity = max(0, item.quantity + adjustment)
        item.quantity = new_quantity
        
        db.session.commit()

        return jsonify({
            'success': True,
            'id': item.id,
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
def api_search(company_id):
    """Search inventory items"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    items = InventoryItem.query.filter(
        and_(
            InventoryItem.company_id == company_id,
            or_(
                InventoryItem.name.ilike(f'%{query}%'),
                InventoryItem.description.ilike(f'%{query}%')
            )
        )
    ).limit(10).all()
    
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
def api_stats(company_id):
    """Get inventory statistics"""
    total_items = InventoryItem.query.filter_by(company_id=company_id).count()
    low_stock_items = InventoryItem.query.filter(
        and_(InventoryItem.company_id == company_id, InventoryItem.quantity <= 10)
    ).count()
    out_of_stock_items = InventoryItem.query.filter(
        and_(InventoryItem.company_id == company_id, InventoryItem.quantity == 0)
    ).count()
    total_value = db.session.query(func.sum(InventoryItem.quantity * InventoryItem.price)).filter_by(company_id=company_id).scalar() or 0
    
    return jsonify({
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'total_value': float(total_value),
        'in_stock_items': total_items - out_of_stock_items
    })

@inventory.route('/<int:company_id>/inventory/<int:id>/barcode')
@login_required
def view_barcode(company_id, id):
    """Generate and return barcode image for an inventory item"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    try:
        # Generate barcode data (company_id + zero-padded item_id)
        barcode_data = f"{company_id}{id:06d}"
        
        # Create barcode
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_data, writer=ImageWriter())
        
        # Generate barcode image in memory
        buffer = BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        
        # Open with PIL to add item information
        barcode_img = Image.open(buffer)
        
        # Create a new image with extra space for text
        img_width, img_height = barcode_img.size
        new_height = img_height + 80  # Add space for text
        final_img = Image.new('RGB', (img_width, new_height), 'white')
        
        # Paste barcode
        final_img.paste(barcode_img, (0, 0))
        
        # Add text information
        draw = ImageDraw.Draw(final_img)
        
        try:
            # Try to use a better font
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Add item name
        text_y = img_height + 10
        draw.text((10, text_y), item.name[:40], fill='black', font=font_large)
        
        # Add price and code
        text_y += 25
        draw.text((10, text_y), f"{session['currency']}{item.price:.2f}", fill='black', font=font_small)
        draw.text((img_width - 100, text_y), f"Code: {barcode_data}", fill='black', font=font_small)
        
        # Save to buffer
        output_buffer = BytesIO()
        final_img.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        from flask import Response
        return Response(
            output_buffer.getvalue(),
            mimetype='image/png',
            headers={'Content-Disposition': f'inline; filename=barcode_{barcode_data}.png'}
        )
        
    except Exception as e:
        current_app.logger.error(f"Barcode generation error: {str(e)}")
        # Return a simple error image
        error_img = Image.new('RGB', (300, 100), 'white')
        draw = ImageDraw.Draw(error_img)
        draw.text((10, 40), "Barcode generation failed", fill='red')
        
        error_buffer = BytesIO()
        error_img.save(error_buffer, format='PNG')
        error_buffer.seek(0)
        
        from flask import Response
        return Response(
            error_buffer.getvalue(),
            mimetype='image/png'
        )

@inventory.route('/<int:company_id>/inventory/<int:id>/barcode/download')
@login_required
def download_barcode(company_id, id):
    """Download barcode as PNG file"""
    item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
    
    try:
        # Generate barcode data
        barcode_data = f"{company_id}{id:06d}"
        
        # Create barcode
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_data, writer=ImageWriter())
        
        # Generate barcode image in memory
        buffer = BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        
        # Open with PIL to add item information
        barcode_img = Image.open(buffer)
        
        # Create a new image with extra space for text
        img_width, img_height = barcode_img.size
        new_height = img_height + 60 # Add more space for download version
        final_img = Image.new('RGB', (img_width, new_height), 'white')
        
        # Paste barcode
        final_img.paste(barcode_img, (0, 0))
        
        # Add text information
        draw = ImageDraw.Draw(final_img)
        
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            #font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            #font_small = ImageFont.load_default()
        
        # Add item information
        text_y = img_height + 10
        draw.text((10, text_y), item.name[:50], fill='black', font=font_large)
        
        text_y += 25
        draw.text((10, text_y), f"{_('Price')} {session['currency']}{item.price:,.2f}", fill='black', font=font_medium)
        #draw.text((img_width - 150, text_y), f"Qty: {item.quantity}", fill='black', font=font_medium)
        
        #text_y += 20
        #draw.text((10, text_y), f"Code: {barcode_data}", fill='black', font=font_small)
        
        #if item.supplier:
        #    draw.text((img_width - 200, text_y), f"Supplier: {item.supplier.name[:20]}", fill='black', font=font_small)
        
        # Save to buffer
        output_buffer = BytesIO()
        final_img.save(output_buffer, format='PNG', dpi=(300, 300))  # High DPI for printing
        output_buffer.seek(0)
        
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