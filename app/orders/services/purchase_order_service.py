from datetime import datetime, UTC
from app.models import db, PurchaseOrder, PurchaseOrderItem, InventoryItem, StockMovement, StockMovementType
from sqlalchemy import func
from flask_babel import _
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError


def create_purchase_order(company_id, form_data):
    try:
        supplier_id = form_data.get('supplier_id')
        if not supplier_id or not supplier_id.isdigit():
            return {'success': False, 'error': _('Contact is required')}
        
        last_id = db.session.query(func.max(PurchaseOrder.id)).filter_by(company_id=company_id).scalar() or 0
        next_seq = int(last_id) + 1
        order_number = f"PO-{company_id}-{next_seq:06d}"
        
        buy_date_str = form_data.get('buy_date')
        buy_date = None
        if buy_date_str:
            try:
                buy_date = datetime.strptime(buy_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        created_at_str = form_data.get('created_at')
        created_at = None
        if created_at_str:
            try:
                created_at = datetime.strptime(created_at_str, '%Y-%m-%d').replace(tzinfo=UTC)
            except ValueError:
                pass

        warehouse_id = form_data.get('warehouse_id')
        if warehouse_id:
            warehouse_id = int(warehouse_id)
        else:
            warehouse_id = None

        po = PurchaseOrder(company_id=company_id,
                           order_number=order_number,
                           supplier_id=int(supplier_id),
                           warehouse_id=warehouse_id,
                           total_amount=0.0,
                           buy_date=buy_date or (created_at.date() if created_at else datetime.now(UTC).date()),
                           created_at=created_at or datetime.now(UTC))
        db.session.add(po)
        db.session.flush()
        
        total_amount = 0.0
        item_count = 0
        indices = [k.split('[')[1].split(']')[0] for k in form_data.keys()
                   if k.startswith('items[') and k.endswith('][inventory_item_id]')]
        indices.sort(key=int)
        
        for idx in indices:
            item_id = form_data.get(f'items[{idx}][inventory_item_id]')
            code = form_data.get(f'items[{idx}][code]')
            quantity = form_data.get(f'items[{idx}][quantity]')
            price = form_data.get(f'items[{idx}][price]')
            
            if item_id and quantity and price:
                try:
                    quantity = int(quantity)
                    price = float(price)
                    if quantity <= 0 or price < 0:
                        continue
                    
                    inventory_item = InventoryItem.query.get(int(item_id))
                    if not inventory_item or inventory_item.company_id != company_id:
                        continue
                    
                    item_total = quantity * price
                    inventory_item.quantity = (inventory_item.quantity or 0) + quantity
                    db.session.add(inventory_item)
                    
                    if warehouse_id:
                        from app.models import WarehouseItem
                        wh_item = WarehouseItem.query.filter_by(warehouse_id=warehouse_id, inventory_item_id=int(item_id)).first()
                        if not wh_item:
                            wh_item = WarehouseItem(warehouse_id=warehouse_id, inventory_item_id=int(item_id), quantity=0)
                            db.session.add(wh_item)
                        wh_item.quantity = (wh_item.quantity or 0) + quantity
                    
                    # Create stock movement
                    movement = StockMovement(
                        company_id=company_id,
                        inventory_item_id=int(item_id),
                        warehouse_id=warehouse_id,
                        type=StockMovementType.incoming,
                        quantity=quantity,
                        reference=f"PO {order_number}",
                        date=created_at or datetime.now(UTC)
                    )
                    db.session.add(movement)
                    
                    po_item = PurchaseOrderItem(inventory_item_id=int(item_id),
                                                name=inventory_item.name,
                                                item_code=code or '',
                                                quantity=quantity,
                                                price=price,
                                                total=item_total)
                    po.items.append(po_item)
                    
                    total_amount += item_total
                    item_count += 1
                except (ValueError, TypeError):
                    continue
        
        if item_count == 0:
            db.session.rollback()
            return {'success': False, 'error': _('At least one item is required')}
        
        po.total_amount = total_amount
        db.session.commit()
        return {'success': True, 'order': po}
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating purchase order: {str(e)}")
        return {'success': False, 'error': _('An error occurred while creating the purchase order')}
    
def update_purchase_order(company_id, order_id, form_data):
    try:
        purchase_order = PurchaseOrder.query.filter_by(
            id=order_id,
            company_id=company_id
        ).first()

        if not purchase_order:
            return {'success': False, 'error': _('Purchase order not found')}

        supplier_id = form_data.get('supplier_id')
        if not supplier_id or not supplier_id.isdigit():
            return {'success': False, 'error': _('Contact is required')}

        # Parse new items first
        indices = []
        for key in form_data.keys():
            if key.startswith('items[') and key.endswith('][inventory_item_id]'):
                idx = key.split('[', 1)[1].split(']', 1)[0]
                if idx not in indices:
                    indices.append(idx)

        indices.sort(key=lambda x: int(x))
        parsed_items = []
        for idx in indices:
            item_id = form_data.get(f'items[{idx}][inventory_item_id]')
            code = form_data.get(f'items[{idx}][code]')
            quantity = form_data.get(f'items[{idx}][quantity]')
            price = form_data.get(f'items[{idx}][price]')

            if not item_id or not quantity or not price:
                continue

            try:
                quantity = int(quantity)
                price = float(price)
            except (ValueError, TypeError):
                continue

            if quantity <= 0 or price < 0:
                continue

            parsed_items.append({
                'inventory_item_id': int(item_id),
                'code': code or '',
                'quantity': quantity,
                'price': price
            })

        if not parsed_items:
            return {'success': False, 'error': _('At least one item is required')}

        # Collect existing movements to calculate net stock deltas
        movements = StockMovement.query.filter_by(
            company_id=company_id,
            reference=f"PO {purchase_order.order_number}",
            type=StockMovementType.incoming
        ).all()
        
        inventory_deltas = {}  # inventory_item_id -> delta
        warehouse_deltas = {}  # (warehouse_id, inventory_item_id) -> delta
        
        for m in movements:
            inventory_deltas[m.inventory_item_id] = inventory_deltas.get(m.inventory_item_id, 0) - m.quantity
            if m.warehouse_id:
                key = (m.warehouse_id, m.inventory_item_id)
                warehouse_deltas[key] = warehouse_deltas.get(key, 0) - m.quantity

        # Update purchase order fields
        purchase_order.supplier_id = int(supplier_id)

        buy_date_str = form_data.get('buy_date')
        if buy_date_str:
            try:
                purchase_order.buy_date = datetime.strptime(buy_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        created_at_str = form_data.get('created_at')
        if created_at_str:
            try:
                purchase_order.created_at = datetime.strptime(created_at_str, '%Y-%m-%d').replace(tzinfo=UTC)
            except ValueError:
                pass

        warehouse_id = form_data.get('warehouse_id')
        if warehouse_id:
            purchase_order.warehouse_id = int(warehouse_id)
        else:
            purchase_order.warehouse_id = None

        new_warehouse_id = purchase_order.warehouse_id
        total_amount = 0.0
        item_count = 0

        available_po_items = list(purchase_order.items)
        existing_movements = list(movements)

        for data in parsed_items:
            item_id = data['inventory_item_id']
            quantity = data['quantity']
            price = data['price']
            code = data['code']
            item_total = quantity * price

            inventory_item = InventoryItem.query.get(item_id)
            if not inventory_item or inventory_item.company_id != company_id:
                continue

            # Add positive deltas
            inventory_deltas[item_id] = inventory_deltas.get(item_id, 0) + quantity
            if new_warehouse_id:
                key = (new_warehouse_id, item_id)
                warehouse_deltas[key] = warehouse_deltas.get(key, 0) + quantity

            # Update or create PO item
            po_item = next((item for item in available_po_items if item.inventory_item_id == item_id), None)
            if po_item:
                available_po_items.remove(po_item)
                po_item.item_code = code
                po_item.quantity = quantity
                po_item.price = price
                po_item.total = item_total
            else:
                po_item = PurchaseOrderItem(
                    inventory_item_id=item_id,
                    name=inventory_item.name,
                    item_code=code,
                    quantity=quantity,
                    price=price,
                    total=item_total
                )
                purchase_order.items.append(po_item)

            # Update or create StockMovement
            movement = next((m for m in existing_movements if m.inventory_item_id == item_id), None)
            if movement:
                existing_movements.remove(movement)
                movement.warehouse_id = purchase_order.warehouse_id
                movement.quantity = quantity
                movement.date = purchase_order.created_at or datetime.now(UTC)
            else:
                movement = StockMovement(
                    company_id=company_id,
                    inventory_item_id=item_id,
                    warehouse_id=purchase_order.warehouse_id,
                    type=StockMovementType.incoming,
                    quantity=quantity,
                    reference=f"PO {purchase_order.order_number}",
                    date=purchase_order.created_at or datetime.now(UTC)
                )
                db.session.add(movement)

            total_amount += item_total
            item_count += 1

        if item_count == 0:
            db.session.rollback()
            return {'success': False, 'error': _('At least one valid item is required')}

        # Remove unused items and movements
        for po_item in available_po_items:
            purchase_order.items.remove(po_item)

        for m in existing_movements:
            db.session.delete(m)

        # Apply net stock deltas
        from app.models import WarehouseItem
        
        for item_id, delta in inventory_deltas.items():
            if delta != 0:
                inv = InventoryItem.query.get(item_id)
                if inv:
                    inv.quantity = (inv.quantity or 0) + delta
                    db.session.add(inv)
                    
        for (wh_id, item_id), delta in warehouse_deltas.items():
            if delta != 0:
                wh_item = WarehouseItem.query.filter_by(warehouse_id=wh_id, inventory_item_id=item_id).first()
                if not wh_item:
                    wh_item = WarehouseItem(warehouse_id=wh_id, inventory_item_id=item_id, quantity=0)
                    db.session.add(wh_item)
                wh_item.quantity = (wh_item.quantity or 0) + delta

        purchase_order.total_amount = total_amount
        db.session.commit()

        return {'success': True, 'order': purchase_order}

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating purchase order: {str(e)}")
        return {'success': False, 'error': _('An error occurred while updating the purchase order')}


def delete_purchase_order(company_id: int, order_id: int) -> None:
    """Soft-delete a purchase order."""
    purchase_order = PurchaseOrder.query.filter_by(id=order_id, company_id=company_id).first_or_404()
    purchase_order.is_deleted = True
    purchase_order.deleted_at = datetime.now(UTC)
    db.session.commit()


def export_purchase_orders_xlsx(company_id: int, search: str = None, supplier_id: str = None):
    """Return (workbook, filename) tuple for all purchase orders matching criteria."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from flask_babel import _
    from app.orders.services.purchase_order_query_service import get_purchase_orders

    pagination = get_purchase_orders(
        company_id=company_id,
        page=1,
        per_page=1000000,
        search=search,
        supplier_id=supplier_id
    )
    orders = pagination.items

    wb = Workbook()
    ws = wb.active
    ws.title = _('Ordenes de Compra')

    headers = [_('Número de Orden'), _('Proveedor'), _('Monto Total'), _('Cantidad de Productos'), _('Fecha de Creación')]
    ws.append(headers)

    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    for order in orders:
        ws.append([
            order.order_number,
            order.supplier.name if order.supplier else '',
            float(order.total_amount),
            len(order.items),
            order.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    filename = f"ordenes_de_compra_{company_id}_{datetime.now(UTC).strftime('%Y%m%d')}.xlsx"
    return wb, filename

