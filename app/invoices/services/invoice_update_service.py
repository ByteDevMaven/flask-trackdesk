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

    subtotal = total
    tax_rate = float(form.get("tax_rate", 0)) if form.get("tax_rate") else 0
    tax_amount = subtotal * (tax_rate / 100)
    total_amount = subtotal + tax_amount

    document.subtotal = subtotal
    document.tax_rate = tax_rate
    document.tax_amount = tax_amount
    document.total_amount = total_amount

def delete_invoice_or_quote(document):
    """Soft delete an invoice or quote and its items."""
    items = DocumentItem.query.filter_by(document_id=document.id).all()
    for item in items:
        item.is_deleted = True
        item.deleted_at = datetime.now(UTC)
    
    document.is_deleted = True
    document.deleted_at = datetime.now(UTC)
    db.session.commit()

def add_invoice_payment(document, form):
    """Add a payment to an invoice and update its status."""
    from app.models import Payment, PaymentMethod
    from app.models.enums import DocumentStatus
    
    amount = float(form.get('amount', 0))
    payment_date_str = form.get('payment_date')
    payment_method = form.get('payment_method', 'cash')
    reference = form.get('reference', '')

    if amount <= 0:
        raise ValueError('Payment amount must be greater than 0')

    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d') if payment_date_str else datetime.now(UTC)

    payment = Payment(
        company_id=document.company_id,
        document_id=document.id,
        amount=amount,
        payment_date=payment_date,
        method=PaymentMethod[payment_method],
        notes=reference
    )

    db.session.add(payment)
    db.session.flush()

    paid_amount = document.calculate_paid_amount()
    if paid_amount >= float(document.total_amount):
        document.status = DocumentStatus.paid
    elif paid_amount > 0:
        document.status = DocumentStatus.partial

    db.session.commit()
