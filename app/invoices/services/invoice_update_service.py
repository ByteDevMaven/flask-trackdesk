from flask import session
from app.models import db, DocumentItem, InventoryItem, DocumentType, StockMovement, StockMovementType
from datetime import datetime, UTC

def update_invoice_or_quote(document, form):
    # Restore stock from existing movements
    movements = StockMovement.query.filter_by(
        company_id=document.company_id,
        reference=f"INV {document.document_number}",
        type=StockMovementType.outgoing
    ).all()
    
    for m in movements:
        inv = InventoryItem.query.get(m.inventory_item_id)
        if inv:
            inv.quantity -= m.quantity # m.quantity is negative, so subtracting adds it back
            
        if m.warehouse_id:
            from app.models import WarehouseItem
            wh_item = WarehouseItem.query.filter_by(warehouse_id=m.warehouse_id, inventory_item_id=m.inventory_item_id).first()
            if wh_item:
                wh_item.quantity -= m.quantity

    StockMovement.query.filter_by(
        company_id=document.company_id,
        reference=f"INV {document.document_number}",
        type=StockMovementType.outgoing
    ).delete()

    DocumentItem.query.filter_by(document_id=document.id).delete()

    items_data = {}
    for key, value in form.items():
        if key.startswith("items[") and "][" in key:
            idx = key.split("[")[1].split("]")[0]
            field = key.split("][")[1][:-1]
            items_data.setdefault(idx, {})[field] = value

    total = 0
    has_items = False

    for item in items_data.values():
        if not (item.get("inventory_item_id") or item.get("description")):
            continue

        has_items = True

        quantity = int(item.get("quantity", 0)) if item.get("quantity") else 0
        unit_price = float(item.get("unit_price", 0)) if item.get("unit_price") else 0
        discount = float(item.get("discount", 0)) if item.get("discount") else 0
        inv_id = (
            int(item.get("inventory_item_id"))
            if item.get("inventory_item_id") else None
        )

        db.session.add(DocumentItem(
            document_id=document.id,
            inventory_item_id=inv_id,
            description=item.get("description", ""),
            quantity=quantity,
            unit_price=unit_price,
            discount=discount
        ))

        if inv_id and document.type == DocumentType.invoice:
            inv = InventoryItem.query.get(inv_id)
            if inv:
                if inv.quantity < quantity:
                    raise ValueError(f"Not enough stock for: {inv.name}")
                inv.quantity -= quantity
                
                warehouse_id = document.warehouse_id
                if warehouse_id:
                    from app.models import WarehouseItem
                    wh_item = WarehouseItem.query.filter_by(warehouse_id=warehouse_id, inventory_item_id=inv_id).first()
                    if not wh_item:
                        wh_item = WarehouseItem(warehouse_id=warehouse_id, inventory_item_id=inv_id, quantity=0)
                        db.session.add(wh_item)
                    wh_item.quantity -= quantity
                
                # Create new stock movement
                movement = StockMovement(
                    company_id=document.company_id,
                    inventory_item_id=inv_id,
                    warehouse_id=warehouse_id,
                    user_id=document.user_id,
                    type=StockMovementType.outgoing,
                    quantity=-quantity,
                    reference=f"INV {document.document_number}",
                    date=document.issued_date or datetime.now(UTC)
                )
                db.session.add(movement)

        item_total = quantity * unit_price
        item_discount = item_total * (discount / 100)
        total += item_total - item_discount

    if not has_items:
        raise ValueError("At least one item is required")

    try:
        tax_rate = float(session.get("tax_rate", 0)) / 100
    except (TypeError, ValueError):
        tax_rate = 0.0
    document.total_amount = round(total * (1 + tax_rate), 2)
