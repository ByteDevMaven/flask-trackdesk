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
        if is_ajax: return jsonify({'success': False, 'error': 'All fields are required for transfer'})
        flash('All fields are required for transfer', 'error')
        return redirect(url_for('inventory.view', company_id=company_id, sku=sku))
        
    if from_warehouse_id == to_warehouse_id:
        if is_ajax: return jsonify({'success': False, 'error': 'Source and destination warehouses must be different'})
        flash('Source and destination warehouses must be different', 'error')
        return redirect(url_for('inventory.view', company_id=company_id, sku=sku))
        
    try:
        InventoryService.transfer_stock(
            company_id=company_id,
            item_id=item.id,
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id,
            quantity=quantity
        )
        if is_ajax: return jsonify({'success': True, 'message': 'Stock transferred successfully'})
        flash('Stock transferred successfully', 'success')
    except ValueError as e:
        if is_ajax: return jsonify({'success': False, 'error': str(e)})
        flash(str(e), 'error')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Transfer error: {str(e)}")
        if is_ajax: return jsonify({'success': False, 'error': 'An error occurred during transfer'})
        flash('An error occurred during transfer', 'error')
        
    if is_ajax: return jsonify({'success': False, 'error': 'Unknown error'})
    return redirect(url_for('inventory.view', company_id=company_id, sku=sku))
