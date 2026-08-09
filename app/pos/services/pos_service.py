import json
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask_login import current_user
from werkzeug.datastructures import MultiDict

from app.models import Contact, Document, DocumentSequence, DocumentType, InventoryItem, Payment, PaymentMethod, PosCashMovement, PosRegisterSession, Warehouse, WarehouseItem

PAYMENT_METHODS = [
    {"value": "cash", "label": "Efectivo"},
    {"value": "credit_card", "label": "POS bancario"},
    {"value": "bank_transfer", "label": "Transferencia"},
    {"value": "cheque", "label": "Cheque"},
    {"value": "other", "label": "Otro"},
]


def _decimal(value, default="0") -> Decimal:
    try:
        return Decimal(str(value if value not in (None, "") else default))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _money(value) -> Decimal:
    return _decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _required_decimal(value, field_name: str) -> Decimal:
    """Parse user input without silently turning malformed values into zero."""
    if value in (None, ""):
        raise ValueError(f"{field_name} es obligatorio.")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} no es un numero valido.") from exc
    if not parsed.is_finite():
        raise ValueError(f"{field_name} no es un numero valido.")
    return parsed


def _company_route_id(company):
    return company.slug or str(company.id)


def _warehouse_for_company(company_id: int, warehouse_id: int | None):
    if not warehouse_id:
        return None

    return Warehouse.query.filter_by(
        id=warehouse_id,
        company_id=company_id,
        is_active=True,
    ).first()


def _available_stock(item: InventoryItem, warehouse_id: int | None) -> int:
    if warehouse_id:
        warehouse_item = WarehouseItem.query.filter_by(
            warehouse_id=warehouse_id,
            inventory_item_id=item.id,
        ).first()
        if warehouse_item is not None:
            return int(warehouse_item.quantity or 0)

    return int(item.quantity or 0)


def _product_payload(item: InventoryItem, warehouse_id: int | None):
    stock = _available_stock(item, warehouse_id)
    barcode = item.generated_tag
    return {
        "id": item.id,
        "sku": item.sku or "",
        "barcode": barcode,
        "name": item.name,
        "description": item.description or item.name,
        "price": float(_money(item.price)),
        "discount": float(_money(item.discount)),
        "stock": stock,
        "search_terms": [
            item.sku or "",
            barcode,
            str(item.id),
            f"{item.id:06d}",
            item.name,
            item.description or "",
        ],
    }


def _format_hn_number(sequence_value):
    if sequence_value in (None, ""):
        return ""

    try:
        numeric = int(sequence_value)
    except (TypeError, ValueError):
        return str(sequence_value)

    return f"000-001-01-{numeric:08d}"


def _document_sequence_for_receipt(document: Document | None):
    if not document:
        return None

    sequence_number = None
    try:
        sequence_number = int(str(document.document_number).split("-")[-1])
    except (TypeError, ValueError):
        sequence_number = None

    query = DocumentSequence.query.filter_by(company_id=document.company_id)
    if sequence_number is not None:
        sequence = query.filter(
            DocumentSequence.range_start <= sequence_number,
            DocumentSequence.range_end >= sequence_number,
        ).order_by(DocumentSequence.expiration_date.desc()).first()
        if sequence:
            return sequence

    return query.order_by(DocumentSequence.expiration_date.desc()).first()


def _sequence_payload(sequence: DocumentSequence | None):
    if not sequence:
        return {
            "cai": "",
            "range_start": "",
            "range_end": "",
            "range_label": "",
            "expiration_date": "",
        }

    range_start = _format_hn_number(sequence.range_start)
    range_end = _format_hn_number(sequence.range_end)
    return {
        "cai": sequence.cai or "",
        "range_start": range_start,
        "range_end": range_end,
        "range_label": f"{range_start} al {range_end}" if range_start and range_end else "",
        "expiration_date": sequence.expiration_date.strftime("%Y-%m-%d")
        if sequence.expiration_date else "",
    }


def _company_payload(company):
    return {
        "name": company.name or "",
        "rtn": company.identifier or "",
        "address": company.address or "",
        "phone": company.phone or "",
        "email": company.email or "",
    }


def _customer_payload(contact: Contact):
    return {
        "id": contact.id,
        "name": contact.name or "",
        "identifier": contact.identifier or "",
        "phone": contact.phone or "",
        "email": contact.email or "",
    }


def _current_register_session(company_id: int):
    return PosRegisterSession.query.filter_by(
        company_id=company_id,
        user_id=current_user.id,
        status="open",
    ).order_by(PosRegisterSession.opened_at.desc()).first()


def _register_totals(session: PosRegisterSession | None):
    if not session:
        return {
            "cash_sales": Decimal("0"),
            "cash_in": Decimal("0"),
            "cash_out": Decimal("0"),
            "expected_cash": Decimal("0"),
            "transactions": 0,
        }

    cash_payments = Payment.query.filter_by(
        company_id=session.company_id,
        pos_register_session_id=session.id,
        method=PaymentMethod.cash,
    ).all()
    cash_sales = sum((_money(payment.amount) for payment in cash_payments), Decimal("0"))

    movements = PosCashMovement.query.filter_by(
        company_id=session.company_id,
        register_session_id=session.id,
    ).all()
    cash_in = sum(
        (_money(movement.amount) for movement in movements if movement.movement_type == "cash_in"),
        Decimal("0"),
    )
    cash_out = sum(
        (_money(movement.amount) for movement in movements if movement.movement_type == "cash_out"),
        Decimal("0"),
    )
    expected_cash = _money(session.opening_amount) + cash_sales + cash_in - cash_out
    return {
        "cash_sales": _money(cash_sales),
        "cash_in": _money(cash_in),
        "cash_out": _money(cash_out),
        "expected_cash": _money(expected_cash),
        "transactions": len(cash_payments),
    }


def _register_payload(session: PosRegisterSession | None):
    if not session:
        return {
            "isOpen": False,
            "id": None,
            "registerName": "",
            "openedAt": "",
            "openingAmount": 0,
            "cashSales": 0,
            "cashIn": 0,
            "cashOut": 0,
            "expectedCash": 0,
            "transactions": 0,
        }

    totals = _register_totals(session)
    return {
        "isOpen": True,
        "id": session.id,
        "registerName": session.register_name,
        "openedAt": session.opened_at.strftime("%Y-%m-%d %H:%M") if session.opened_at else "",
        "openingAmount": float(_money(session.opening_amount)),
        "cashSales": float(totals["cash_sales"]),
        "cashIn": float(totals["cash_in"]),
        "cashOut": float(totals["cash_out"]),
        "expectedCash": float(totals["expected_cash"]),
        "transactions": totals["transactions"],
    }


def _receipt_payload(document: Document | None):
    if not document:
        return None

    sequence = _document_sequence_for_receipt(document)
    payment = (
        document.payments.order_by(Payment.id.desc()).first()
        if hasattr(document.payments, "order_by")
        else None
    )
    lines = []
    for item in document.items:
        quantity = int(item.quantity or 0)
        unit_price = _money(item.unit_price)
        discount = _money(item.discount)
        line_subtotal = unit_price * Decimal(quantity)
        line_total = line_subtotal * (Decimal("1") - (discount / Decimal("100")))
        lines.append({
            "description": item.description,
            "quantity": quantity,
            "unit_price": float(unit_price),
            "discount": float(discount),
            "line_total": float(_money(line_total)),
        })

    return {
        "id": document.id,
        "number": document.document_number,
        "status": document.status.value if hasattr(document.status, "value") else document.status,
        "client_name": document.client.name if document.client else "Consumidor final",
        "client_identifier": document.client.identifier if document.client else "",
        "issued_date": document.issued_date.strftime("%Y-%m-%d") if document.issued_date else "",
        "issued_time": document.issued_date.strftime("%H:%M") if document.issued_date else "",
        "subtotal": float(_money(document.subtotal_cache or document.subtotal)),
        "tax": float(_money(document.tax_cache or 0)),
        "total": float(_money(document.total_amount)),
        "paid": float(_money(document.calculate_paid_amount())),
        "balance": float(_money(document.calculate_balance_due())),
        "payment_method": payment.method.name if payment else "",
        "payment_notes": payment.notes if payment else "",
        "sequence": _sequence_payload(sequence),
        "lines": lines,
    }


def _load_receipt(company_id: int, receipt_id: int | None):
    if not receipt_id:
        return None

    return Document.query.filter_by(
        id=receipt_id,
        company_id=company_id,
        type=DocumentType.invoice,
    ).first()


def _parse_cart_payload(raw_payload: str):
    try:
        payload = json.loads(raw_payload or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError("El carrito no tiene un formato valido.") from exc

    if not isinstance(payload, list) or not payload:
        raise ValueError("Agrega al menos un producto al carrito.")

    return payload


def _build_invoice_form(company_id: int, user_id: int, source_form, cart_payload):
    form = MultiDict()
    today = date.today().isoformat()
    warehouse_id = source_form.get("warehouse_id", type=int)
    client_id = source_form.get("client_id", type=int)

    if warehouse_id and not _warehouse_for_company(company_id, warehouse_id):
        raise ValueError("La bodega seleccionada no esta disponible.")

    if client_id:
        client = Contact.query.filter_by(id=client_id, company_id=company_id).first()
        if not client:
            raise ValueError("El cliente seleccionado no esta disponible.")

    form.add("type", "invoice")
    form.add("status", "pending")
    form.add("issued_date", today)
    form.add("due_date", today)
    form.add("warehouse_id", str(warehouse_id or ""))
    form.add("client_id", str(client_id or ""))
    form.add("project_id", "")

    for idx, row in enumerate(cart_payload):
        item_id = row.get("id") or row.get("inventory_item_id")
        if not item_id:
            raise ValueError("Cada linea del carrito debe tener un producto.")

        item = InventoryItem.query.filter_by(id=int(item_id), company_id=company_id).first()
        if not item:
            raise ValueError("Uno de los productos ya no existe o no pertenece a la empresa.")

        quantity_value = _required_decimal(row.get("quantity"), f"La cantidad de {item.name}")
        if quantity_value != quantity_value.to_integral_value():
            raise ValueError(f"La cantidad de {item.name} debe ser un numero entero.")
        quantity = int(quantity_value)
        if quantity <= 0:
            raise ValueError(f"La cantidad de {item.name} debe ser mayor que cero.")

        available = _available_stock(item, warehouse_id)
        if quantity > available:
            raise ValueError(f"No hay stock suficiente para {item.name}. Disponible: {available}.")

        # Browser cart data is untrusted; pricing remains authoritative here.
        unit_price = _money(item.price)
        if unit_price < 0:
            raise ValueError(f"El precio de {item.name} no puede ser negativo.")

        discount = _money(item.discount)
        if discount < 0 or discount > 100:
            raise ValueError(f"El descuento de {item.name} debe estar entre 0 y 100.")

        form.add(f"items[{idx}][inventory_item_id]", str(item.id))
        form.add(f"items[{idx}][description]", row.get("description") or item.name)
        form.add(f"items[{idx}][quantity]", str(quantity))
        form.add(f"items[{idx}][unit_price]", str(unit_price))
        form.add(f"items[{idx}][discount]", str(discount))

    return form
