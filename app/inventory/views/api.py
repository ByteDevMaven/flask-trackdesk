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
    data = request.get_json(silent=True) or {}
    try:
        adjustment = int(data.get('adjustment', 0))
        warehouse_id = int(data.get('warehouse_id'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Adjustment and warehouse ID must be integers'}), 400
    
    if not warehouse_id:
        return jsonify({'error': 'Warehouse ID is required'}), 400
        
    try:
        if not current_user.has_permission('approvals.manage'):
            from app.services.approval_service import ApprovalService
            item = InventoryItem.query.filter_by(id=id, company_id=company_id).first_or_404()
            ApprovalService.create_request(
                company_id=company_id,
                requester_id=current_user.id,
                action_type='adjust_stock',
                payload={
                    'company_id': company_id,
                    'item_id': id,
                    'item_name': item.name if item else None,
                    'item_sku': item.sku if item else None,
                    'warehouse_id': warehouse_id,
                    'adjustment': adjustment
                }
            )
            return jsonify({
                'success': True,
                'pending_approval': True,
                'message': 'Ajuste enviado para aprobación'
            })

        new_quantity = InventoryService.adjust_stock(
            company_id=company_id,
            item_id=id,
            warehouse_id=warehouse_id,
            adjustment=adjustment
        )

        return jsonify({
            'success': True,
            'id': id,
            'new_quantity': new_quantity,
            'adjustment': adjustment,
            'message': 'Stock adjusted successfully'
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
