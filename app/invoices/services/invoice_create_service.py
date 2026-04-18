from datetime import datetime, date
from flask import session
from flask_babel import _
from models import (
    db, Document, DocumentItem, InventoryItem, DocumentSequence,
    DocumentType, Payment, PaymentMethod, StockMovement, StockMovementType
)


def _generate_document_number(company_id, doc_type):
    if doc_type == DocumentType.invoice:
        # Honduras SAR Compliance Implementation
        # We use with_for_update() to lock the sequence record and prevent race conditions
        seq = db.session.query(DocumentSequence).filter(
            DocumentSequence.company_id == company_id
        ).with_for_update().first()

        if not seq:
            raise Exception(_("No active CAI configuration found for this company."))
        
        if seq.expiration_date < date.today():
            raise Exception(_("The CAI sequence has expired (Limit date: %(date)s).", date=seq.expiration_date))

        if seq.current >= seq.range_end:
            raise Exception(_("The CAI sequence range has been exhausted."))

        # Increment and save inside the transaction
        seq.current += 1
        db.session.add(seq)
        
        # Format: 000-001-01-XXXXXXXX
        # 000 = establishment, 001 = emission point, 01 = invoice type
        return f"000-001-01-{seq.current:08d}"
    
    # Fallback to legacy logic for non-invoice document types (e.g. quotes)
    company_id_str = str(company_id)
    type_letter = 'Q' if doc_type == DocumentType.quote else 'X'
    prefix = f"{type_letter}-{company_id_str}-"

    last_doc = Document.query.filter(
        Document.company_id == company_id,
        Document.document_number.like(f"%-{company_id_str}-%")
    ).order_by(Document.id.desc()).first()

    try:
        last_seq = int(last_doc.document_number.split('-')[-1]) if last_doc else 0
    except ValueError:
        last_seq = 0

    return f"{prefix}{last_seq + 1:06d}"


def create_invoice_or_quote(company_id, form, user_id):
    doc_type = DocumentType[form.get("type", "invoice")]

    document_number = form.get("document_number")
    if not document_number:
        document_number = _generate_document_number(company_id, doc_type)

    document = Document(
        company_id=company_id,
        document_number=document_number,
        type=doc_type,
        client_id=int(form.get("client_id")) if form.get("client_id") else None,
        user_id=user_id,
        status=form.get("status", "draft"),
        issued_date=datetime.strptime(form.get("issued_date"), "%Y-%m-%d")
        if form.get("issued_date") else datetime.now(),
        due_date=datetime.strptime(form.get("due_date"), "%Y-%m-%d")
        if form.get("due_date") else None
    )

    db.session.add(document)
    db.session.flush()

    # ---- Parse items ----
    items_data = {}
    for key, value in form.items():
        if key.startswith("items[") and "][" in key:
            idx = key.split("[")[1].split("]")[0]
            field = key.split("][")[1][:-1]
            items_data.setdefault(idx, {})[field] = value

    total = 0

    for item in items_data.values():
        if not (item.get("inventory_item_id") or item.get("description")):
            continue

        try:
            qty = int(float(item.get("quantity", 1)))
        except (TypeError, ValueError):
            qty = 1

        qty = max(qty, 1)
        price = float(item.get("unit_price") or 0)
        discount = float(item.get("discount") or 0)
        inv_id = item.get("inventory_item_id")

        if inv_id and doc_type == DocumentType.invoice:
            inv = InventoryItem.query.get(int(inv_id))
            if inv:
                inv.quantity = max((inv.quantity or 0) - qty, 0)
                
                # Log movement
                movement = StockMovement(
                    company_id=company_id,
                    inventory_item_id=int(inv_id),
                    user_id=user_id,
                    type=StockMovementType.outgoing,
                    quantity=-qty,
                    reference=f"INV {document_number}",
                    date=document.issued_date or datetime.now()
                )
                db.session.add(movement)

        db.session.add(DocumentItem(
            document_id=document.id,
            inventory_item_id=int(inv_id) if inv_id else None,
            description=item.get("description", ""),
            quantity=qty,
            unit_price=price,
            discount=discount
        ))

        total += qty * price * (1 - discount / 100)

    tax_rate = session.get("tax_rate", 0) / 100
    document.total_amount = round(total * (1 + tax_rate), 2)

    if document.status == "paid":
        db.session.add(Payment(
            company_id=company_id,
            document_id=document.id,
            amount=document.total_amount,
            payment_date=datetime.now(),
            method=PaymentMethod.cash,
            notes=form.get("notes", "")
        ))

    db.session.commit()
    return document
