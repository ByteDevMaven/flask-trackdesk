import json
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import MultiDict

from app.invoices.services import add_invoice_payment, create_invoice_or_quote
from app.models import (
    Contact,
    ContactType,
    Document,
    DocumentSequence,
    DocumentType,
    InventoryItem,
    Payment,
    PaymentMethod,
    PosCashMovement,
    PosRegisterSession,
    Warehouse,
    WarehouseItem,
    db,
)
from app.utils import resolve_company

from . import pos


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
    return {
        "id": item.id,
        "sku": item.sku or "",
        "name": item.name,
        "description": item.description or item.name,
        "price": float(_money(item.price)),
        "discount": float(_money(item.discount)),
        "stock": stock,
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

        quantity = int(_decimal(row.get("quantity"), "1"))
        if quantity <= 0:
            raise ValueError(f"La cantidad de {item.name} debe ser mayor que cero.")

        available = _available_stock(item, warehouse_id)
        if quantity > available:
            raise ValueError(f"No hay stock suficiente para {item.name}. Disponible: {available}.")

        unit_price = _money(row.get("unit_price", item.price))
        if unit_price < 0:
            raise ValueError(f"El precio de {item.name} no puede ser negativo.")

        discount = _money(row.get("discount", item.discount))
        if discount < 0 or discount > 100:
            raise ValueError(f"El descuento de {item.name} debe estar entre 0 y 100.")

        form.add(f"items[{idx}][inventory_item_id]", str(item.id))
        form.add(f"items[{idx}][description]", row.get("description") or item.name)
        form.add(f"items[{idx}][quantity]", str(quantity))
        form.add(f"items[{idx}][unit_price]", str(unit_price))
        form.add(f"items[{idx}][discount]", str(discount))

    return form


@pos.route("/<string:company_id>/pos", methods=["GET"])
@login_required
def index(company_id):
    company = resolve_company(company_id)
    warehouses = Warehouse.query.filter_by(
        company_id=company.id,
        is_active=True,
    ).order_by(Warehouse.name.asc()).all()

    selected_warehouse_id = request.args.get("warehouse_id", type=int)
    if selected_warehouse_id and not _warehouse_for_company(company.id, selected_warehouse_id):
        selected_warehouse_id = None
    if not selected_warehouse_id and warehouses:
        selected_warehouse_id = warehouses[0].id

    inventory_items = InventoryItem.query.filter_by(company_id=company.id).order_by(
        InventoryItem.name.asc()
    ).limit(800).all()
    products = [
        _product_payload(item, selected_warehouse_id)
        for item in inventory_items
        if _available_stock(item, selected_warehouse_id) > 0
    ]

    customers = Contact.query.filter(
        Contact.company_id == company.id,
        Contact.type.in_([
            ContactType.customer,
            ContactType.customer_supplier,
        ]),
    ).order_by(Contact.name.asc()).limit(300).all()

    receipt = _load_receipt(company.id, request.args.get("receipt_id", type=int))

    company_route_id = _company_route_id(company)
    receipt_payload = _receipt_payload(receipt)
    register_session = _current_register_session(company.id)
    active_sequence = DocumentSequence.query.filter_by(company_id=company.id).order_by(
        DocumentSequence.expiration_date.desc()
    ).first()
    pos_config = {
        "company": _company_payload(company),
        "products": products,
        "customers": [_customer_payload(customer) for customer in customers],
        "receipt": receipt_payload,
        "currency": company.currency or "USD",
        "taxRate": float(_money(company.tax_rate or 0)),
        "sequence": _sequence_payload(active_sequence),
        "cashierName": current_user.name or current_user.email,
        "register": _register_payload(register_session),
        "companyRouteId": company_route_id,
        "newSaleUrl": url_for(
            "pos.index",
            company_id=company_route_id,
            warehouse_id=selected_warehouse_id,
        ),
    }

    return render_template(
        "pos/index.html",
        company=company,
        company_route_id=company_route_id,
        products=products,
        customers=customers,
        warehouses=warehouses,
        selected_warehouse_id=selected_warehouse_id,
        payment_methods=PAYMENT_METHODS,
        receipt=receipt_payload,
        pos_config=pos_config,
        today=date.today().isoformat(),
    )


@pos.route("/<string:company_id>/pos/checkout", methods=["POST"])
@login_required
def checkout(company_id):
    company = resolve_company(company_id)
    warehouse_id = request.form.get("warehouse_id", type=int)

    try:
        register_session = _current_register_session(company.id)
        if not register_session:
            raise ValueError("Debe abrir caja antes de cobrar una venta POS.")

        cart_payload = _parse_cart_payload(request.form.get("cart_payload", "[]"))
        invoice_form = _build_invoice_form(
            company.id,
            current_user.id,
            request.form,
            cart_payload,
        )
        document = create_invoice_or_quote(company.id, invoice_form, current_user.id)

        amount_received = _money(request.form.get("amount_received"))
        payment_method = request.form.get("payment_method") or "cash"
        if payment_method not in {method["value"] for method in PAYMENT_METHODS}:
            raise ValueError("El metodo de pago no es valido.")

        total_amount = _money(document.total_amount)
        payment_amount = min(amount_received, total_amount)
        if payment_amount > 0:
            reference_parts = [
                request.form.get("reference", "").strip(),
                request.form.get("terminal_id", "").strip(),
                request.form.get("authorization_code", "").strip(),
                request.form.get("card_last4", "").strip(),
            ]
            reference = " | ".join(part for part in reference_parts if part)
            payment_form = MultiDict([
                ("amount", str(payment_amount)),
                ("payment_date", request.form.get("payment_date") or date.today().isoformat()),
                ("payment_method", payment_method),
                ("register_session_id", str(register_session.id)),
                ("reference", reference),
            ])
            add_invoice_payment(document, payment_form)

        flash("Venta registrada correctamente.", "success")
        return redirect(url_for(
            "pos.index",
            company_id=_company_route_id(company),
            warehouse_id=warehouse_id,
            receipt_id=document.id,
        ))
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "error")
        return redirect(url_for(
            "pos.index",
            company_id=_company_route_id(company),
            warehouse_id=warehouse_id,
        ))


@pos.route("/<string:company_id>/pos/register/open", methods=["POST"])
@login_required
def open_register(company_id):
    company = resolve_company(company_id)
    warehouse_id = request.form.get("warehouse_id", type=int)

    try:
        if _current_register_session(company.id):
            raise ValueError("Ya hay una caja abierta para este usuario.")

        if warehouse_id and not _warehouse_for_company(company.id, warehouse_id):
            raise ValueError("La bodega seleccionada no esta disponible.")

        opening_amount = _money(request.form.get("opening_amount"))
        if opening_amount < 0:
            raise ValueError("El monto inicial no puede ser negativo.")

        register_name = (request.form.get("register_name") or "Caja principal").strip()
        session = PosRegisterSession(
            company_id=company.id,
            user_id=current_user.id,
            warehouse_id=warehouse_id,
            register_name=register_name[:100] or "Caja principal",
            status="open",
            opening_amount=opening_amount,
            opened_at=datetime.now(UTC),
            notes=(request.form.get("notes") or "").strip(),
        )
        db.session.add(session)
        db.session.commit()
        flash("Caja abierta correctamente.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "error")

    return redirect(url_for(
        "pos.index",
        company_id=_company_route_id(company),
        warehouse_id=warehouse_id,
    ))


@pos.route("/<string:company_id>/pos/register/close", methods=["POST"])
@login_required
def close_register(company_id):
    company = resolve_company(company_id)
    warehouse_id = request.form.get("warehouse_id", type=int)

    try:
        session = _current_register_session(company.id)
        if not session:
            raise ValueError("No hay una caja abierta para cerrar.")

        closing_amount = _money(request.form.get("closing_amount"))
        if closing_amount < 0:
            raise ValueError("El monto contado no puede ser negativo.")

        totals = _register_totals(session)
        session.expected_cash_amount = totals["expected_cash"]
        session.closing_amount = closing_amount
        session.status = "closed"
        session.closed_at = datetime.now(UTC)
        session.closing_notes = (request.form.get("closing_notes") or "").strip()
        db.session.commit()
        flash("Caja cerrada correctamente.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "error")

    return redirect(url_for(
        "pos.index",
        company_id=_company_route_id(company),
        warehouse_id=warehouse_id,
    ))


@pos.route("/<string:company_id>/pos/register/cash-movement", methods=["POST"])
@login_required
def cash_movement(company_id):
    company = resolve_company(company_id)
    warehouse_id = request.form.get("warehouse_id", type=int)

    try:
        session = _current_register_session(company.id)
        if not session:
            raise ValueError("Debe abrir caja antes de registrar movimientos.")

        movement_type = request.form.get("movement_type")
        if movement_type not in {"cash_in", "cash_out"}:
            raise ValueError("El tipo de movimiento no es valido.")

        amount = _money(request.form.get("amount"))
        if amount <= 0:
            raise ValueError("El monto debe ser mayor que cero.")

        movement = PosCashMovement(
            company_id=company.id,
            register_session_id=session.id,
            user_id=current_user.id,
            movement_type=movement_type,
            amount=amount,
            reason=(request.form.get("reason") or "").strip()[:255],
        )
        db.session.add(movement)
        db.session.commit()
        flash("Movimiento de caja registrado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "error")

    return redirect(url_for(
        "pos.index",
        company_id=_company_route_id(company),
        warehouse_id=warehouse_id,
    ))
