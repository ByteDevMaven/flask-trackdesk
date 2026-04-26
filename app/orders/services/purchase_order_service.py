from datetime import datetime, UTC
from models import db, PurchaseOrder, PurchaseOrderItem, InventoryItem, StockMovement, StockMovementType
from sqlalchemy import func
from flask_babel import _
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError


def create_purchase_order(company_id, form_data):
    try:
        supplier_id = form_data.get('supplier_id')
        if not supplier_id or not supplier_id.isdigit():
            return {'success': False, 'error': _('Supplier is required')}
        
        last_id = db.session.query(func.max(PurchaseOrder.id))\
            .filter_by(company_id=company_id).scalar() or 0
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

        po = PurchaseOrder(company_id=company_id,
                           order_number=order_number,
                           supplier_id=int(supplier_id),
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
                    
                    # Log movement
                    movement = StockMovement(
                        company_id=company_id,
                        inventory_item_id=int(item_id),
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
            return {'success': False, 'error': _('Supplier is required')}

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

        PurchaseOrderItem.query.filter_by(
            purchase_order_id=purchase_order.id
        ).delete()

        total_amount = 0.0
        item_count = 0

        indices = []
        for key in form_data.keys():
            if key.startswith('items[') and key.endswith('][inventory_item_id]'):
                idx = key.split('[', 1)[1].split(']', 1)[0]
                if idx not in indices:
                    indices.append(idx)

        indices.sort(key=lambda x: int(x))

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

            inventory_item = InventoryItem.query.get(int(item_id))
            if not inventory_item or inventory_item.company_id != company_id:
                continue

            item_total = quantity * price

            po_item = PurchaseOrderItem(
                purchase_order_id=purchase_order.id,
                inventory_item_id=int(item_id),
                name=inventory_item.name,
                item_code=code or '',
                quantity=quantity,
                price=price,
                total=item_total
            )

            db.session.add(po_item)
            total_amount += item_total
            item_count += 1

        if item_count == 0:
            db.session.rollback()
            return {'success': False, 'error': _('At least one item is required')}

        purchase_order.total_amount = total_amount
        db.session.commit()

        return {'success': True, 'order': purchase_order}

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating purchase order: {str(e)}")
        return {'success': False, 'error': _('An error occurred while updating the purchase order')}
