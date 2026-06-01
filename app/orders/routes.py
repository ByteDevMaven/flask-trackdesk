from datetime import datetime, UTC

from flask import render_template, request, redirect, url_for, flash, current_app, Response
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from flask_babel import _

from app.models import Contact, InventoryItem, PurchaseOrder
from app.models.enums import ContactType

from .services import (
    create_purchase_order, update_purchase_order,
    delete_purchase_order, export_purchase_orders_csv,
    get_purchase_orders, get_purchase_order_stats
)
from . import orders


@orders.route('/<int:company_id>/purchase-orders')
@login_required
def index(company_id):
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 15))

    search = request.args.get('search', '')
    supplier_id = request.args.get('supplier_id', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')

    pagination = get_purchase_orders(
        company_id=company_id,
        page=page,
        per_page=per_page,
        search=search,
        supplier_id=supplier_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    suppliers = Contact.query.filter_by(
        company_id=company_id, type=ContactType.supplier
    ).order_by(Contact.name).all()

    stats = get_purchase_order_stats(company_id)

    from werkzeug.datastructures import MultiDict
    filtered_args = MultiDict(request.args)
    filtered_args.pop('sort', None)
    filtered_args.pop('order', None)

    return render_template(
        'orders/index.html',
        company_id=company_id,
        orders=pagination.items,
        pagination=pagination,
        suppliers=suppliers,
        stats=stats,
        search=search,
        supplier_id=supplier_id,
        sort_by=sort_by,
        sort_order=sort_order,
        filtered_args=filtered_args
    )


@orders.route('/<int:company_id>/purchase-orders/create', methods=['GET', 'POST'])
@login_required
def create(company_id):
    from app.models import Warehouse
    suppliers = Contact.query.filter_by(company_id=company_id, type=ContactType.supplier).order_by(Contact.name).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).order_by(InventoryItem.name).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()

    if request.method == 'POST':
        result = create_purchase_order(company_id, request.form)
        if result['success']:
            flash(_('Purchase order created successfully'), 'success')
            return redirect(url_for('orders.view', company_id=company_id, id=result['order'].id))
        else:
            flash(result['error'], 'error')
            return render_template('orders/form.html',
                                   company_id=company_id,
                                   suppliers=suppliers,
                                   inventory_items=inventory_items,
                                   warehouses=warehouses,
                                   order=None,
                                   form_data=request.form,
                                   now=datetime.now(UTC))
    return render_template('orders/form.html',
                           company_id=company_id,
                           suppliers=suppliers,
                           inventory_items=inventory_items,
                           warehouses=warehouses,
                           order=None,
                           form_data=None,
                           now=datetime.now(UTC))


@orders.route('/<int:company_id>/purchase-orders/<int:id>')
@login_required
def view(company_id, id):
    purchase_order = PurchaseOrder.query.filter_by(id=id, company_id=company_id).first_or_404()
    return render_template('orders/view.html', company_id=company_id, order=purchase_order)


@orders.route('/<int:company_id>/purchase-orders/<int:id>/edit', methods=['GET'])
@login_required
def edit(company_id, id):
    from app.models import Warehouse
    purchase_order = PurchaseOrder.query.filter_by(id=id, company_id=company_id).first_or_404()
    suppliers = Contact.query.filter_by(company_id=company_id, type=ContactType.supplier).order_by(Contact.name).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).order_by(InventoryItem.name).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()

    return render_template('orders/form.html',
                          company_id=company_id,
                          suppliers=suppliers,
                          inventory_items=inventory_items,
                          warehouses=warehouses,
                          order=purchase_order,
                          form_data=None,
                          now=datetime.now(UTC))


@orders.route('/<int:company_id>/purchase-orders/<int:id>/update', methods=['POST'])
@login_required
def update(company_id, id):
    from app.models import Warehouse
    suppliers = Contact.query.filter_by(company_id=company_id, type=ContactType.supplier).order_by(Contact.name).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).order_by(InventoryItem.name).all()
    warehouses = Warehouse.query.filter_by(company_id=company_id, is_active=True).order_by(Warehouse.name).all()

    result = update_purchase_order(company_id, id, request.form)

    if result['success']:
        flash(_('Purchase order updated successfully'), 'success')
        return redirect(url_for('orders.view', company_id=company_id, id=id))
    else:
        flash(result['error'], 'error')
        purchase_order = PurchaseOrder.query.get(id)
        return render_template('orders/form.html',
                               company_id=company_id,
                               suppliers=suppliers,
                               inventory_items=inventory_items,
                               warehouses=warehouses,
                               order=purchase_order,
                               form_data=request.form,
                               now=datetime.now(UTC))


@orders.route('/<int:company_id>/purchase-orders/<int:id>/delete', methods=['POST'])
@login_required
def delete(company_id, id):
    try:
        delete_purchase_order(company_id, id)
        flash(_('Purchase order deleted successfully'), 'success')
    except SQLAlchemyError as e:
        flash(_('An error occurred while deleting the purchase order'), 'error')
        current_app.logger.error(f"Database error: {str(e)}")

    return redirect(url_for('orders.index', company_id=company_id))


@orders.route('/<int:company_id>/purchase-orders/export')
@login_required
def export(company_id):
    csv_content, filename = export_purchase_orders_csv(company_id)
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )