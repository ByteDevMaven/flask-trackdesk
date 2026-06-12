from flask import session
from app.models import db, DocumentItem, InventoryItem, DocumentType, StockMovement, StockMovementType
from datetime import datetime, UTC


def update_invoice_or_quote(document, form):
    # Parse incoming items
    items_data = {}
    for key, value in form.items():
        if key.startswith("items[") and "][" in key:
            idx = int(key.split("[")[1].split("]")[0])
            field = key.split("][")[1][:-1]
            items_data.setdefault(idx, {})[field] = value

    incoming_items = []
    for idx in sorted(items_data.keys()):
        item = items_data[idx]
        if not (item.get("inventory_item_id") or item.get("description")):
            continue
        incoming_items.append({
            "inventory_item_id": int(item["inventory_item_id"]) if item.get("inventory_item_id") else None,
            "description": item.get("description", ""),
            "quantity": int(item.get("quantity", 0)) if item.get("quantity") else 0,
            "unit_price": float(item.get("unit_price", 0)) if item.get("unit_price") else 0,
            "discount": float(item.get("discount", 0)) if item.get("discount") else 0
        })

    if not incoming_items:
        raise ValueError("At least one item is required")

    # Reconcile DocumentItems
    existing_items = DocumentItem.query.filter_by(document_id=document.id).order_by(DocumentItem.id).all()
    
    total = 0
    
    for i, item_data in enumerate(incoming_items):
        qty = item_data["quantity"]
        unit_price = item_data["unit_price"]
        discount = item_data["discount"]
        
        if i < len(existing_items):
            doc_item = existing_items[i]
            doc_item.inventory_item_id = item_data["inventory_item_id"]
            doc_item.description = item_data["description"]
            doc_item.quantity = qty
            doc_item.unit_price = unit_price
            doc_item.discount = discount
        else:
            doc_item = DocumentItem(
                document_id=document.id,
                inventory_item_id=item_data["inventory_item_id"],
                description=item_data["description"],
                quantity=qty,
                unit_price=unit_price,
                discount=discount
            )
            db.session.add(doc_item)
            
        item_total = qty * unit_price
        item_discount = item_total * (discount / 100)
        total += item_total - item_discount
        
    # Delete excess items
    for i in range(len(incoming_items), len(existing_items)):
        db.session.delete(existing_items[i])

    # Calculate target stock deductions
    target_deductions = {}  # (warehouse_id, inventory_item_id) -> quantity
    if document.type == DocumentType.invoice:
        for item in incoming_items:
            inv_id = item["inventory_item_id"]
            if inv_id and document.warehouse_id:
                key = (document.warehouse_id, inv_id)
                target_deductions[key] = target_deductions.get(key, 0) + item["quantity"]

    # Get current stock deductions from StockMovements
    movements = StockMovement.query.filter_by(
        company_id=document.company_id,
        reference=f"INV {document.document_number}",
        type=StockMovementType.outgoing
    ).all()
    
    current_deductions = {} # (warehouse_id, inventory_item_id) -> quantity
    movement_map = {}
    for m in movements:
        key = (m.warehouse_id, m.inventory_item_id)
        current_deductions[key] = current_deductions.get(key, 0) + abs(m.quantity)
        movement_map[key] = m

    # Apply differences to stock
    all_keys = set(target_deductions.keys()).union(set(current_deductions.keys()))
    
    for key in all_keys:
        warehouse_id, inv_id = key
        current_qty = current_deductions.get(key, 0)
        target_qty = target_deductions.get(key, 0)
        
        if current_qty != target_qty:
            delta = target_qty - current_qty # positive means we need to deduct more
            
            inv = InventoryItem.query.get(inv_id)
            if not inv:
                continue
                
            from app.models import WarehouseItem
            wh_item = WarehouseItem.query.filter_by(warehouse_id=warehouse_id, inventory_item_id=inv_id).first()
            
            if not wh_item:
                wh_item = WarehouseItem(warehouse_id=warehouse_id, inventory_item_id=inv_id, quantity=0)
                db.session.add(wh_item)
                
            if delta > 0:
                inv.quantity = max((inv.quantity or 0) - delta, 0)
                wh_item.quantity = max((wh_item.quantity or 0) - delta, 0)
            else:
                inv.quantity -= delta
                wh_item.quantity -= delta
            
            m = movement_map.get(key)
            if m:
                m.quantity = -target_qty
                if target_qty == 0:
                    db.session.delete(m)
            else:
                if target_qty > 0:
                    m = StockMovement(
                        company_id=document.company_id,
                        inventory_item_id=inv_id,
                        warehouse_id=warehouse_id,
                        user_id=document.user_id,
                        type=StockMovementType.outgoing,
                        quantity=-target_qty,
                        reference=f"INV {document.document_number}",
                        date=document.issued_date or datetime.now(UTC)
                    )
                    db.session.add(m)

    subtotal = total
    tax_rate = float(form.get("tax_rate", 0)) if form.get("tax_rate") else 0
    tax_amount = subtotal * (tax_rate / 100)
    total_amount = subtotal + tax_amount

    document.subtotal_cache = subtotal
    document.tax_cache = tax_amount
    document.total_amount = total_amount

    # Update project association
    project_id_raw = form.get("project_id")
    document.project_id = int(project_id_raw) if project_id_raw else None


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
    """Add a payment to an invoice, post accounting income, and update its status."""
    from app.models import Payment, PaymentMethod
    from app.models.enums import DocumentStatus
    from .accounting_integration import post_invoice_payment_income
    
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

    post_invoice_payment_income(payment, document)

    paid_amount = document.calculate_paid_amount()
    if paid_amount >= float(document.total_amount):
        document.status = DocumentStatus.paid
    elif paid_amount > 0:
        document.status = DocumentStatus.partial

    db.session.commit()
