from datetime import UTC, date, datetime
from decimal import Decimal, ROUND_HALF_UP

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import MultiDict

from app.invoices.services import add_invoice_payment, create_invoice_or_quote
from app.models import Contact, ContactType, DocumentSequence, InventoryItem, PosCashMovement, PosRegisterSession, Warehouse, db
from app.utils import resolve_company

from . import pos
from .services.pos_service import (
    PAYMENT_METHODS,
    _available_stock,
    _build_invoice_form,
    _company_payload,
    _company_route_id,
    _current_register_session,
    _customer_payload,
    _load_receipt,
    _money,
    _parse_cart_payload,
    _receipt_payload,
    _register_payload,
    _register_totals,
    _required_decimal,
    _sequence_payload,
    _warehouse_for_company,
)


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
        amount_received = _required_decimal(
            request.form.get("amount_received"), "El monto recibido"
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if amount_received < 0:
            raise ValueError("El monto recibido no puede ser negativo.")
        payment_method = request.form.get("payment_method") or "cash"
        if payment_method not in {method["value"] for method in PAYMENT_METHODS}:
            raise ValueError("El metodo de pago no es valido.")

        document = create_invoice_or_quote(
            company.id, invoice_form, current_user.id, commit=False
        )
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
        else:
            db.session.commit()

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
