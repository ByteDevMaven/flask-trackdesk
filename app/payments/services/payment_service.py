from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy import desc, or_
from sqlalchemy.orm import joinedload

from app.models import Contact, Document, DocumentType, Payment, PaymentMethod, db
from app.models.enums import DocumentStatus

_METHOD_ALIASES = {
    'credit card': PaymentMethod.credit_card,
    'credit_card': PaymentMethod.credit_card,
    'bank transfer': PaymentMethod.bank_transfer,
    'bank_transfer': PaymentMethod.bank_transfer,
    'cash': PaymentMethod.cash,
    'cheque': PaymentMethod.cheque,
    'other': PaymentMethod.other,
}


def _parse_amount(value) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError('Enter a valid payment amount') from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError('Payment amount must be greater than zero')
    return amount.quantize(Decimal('0.01'))


def _parse_method(value) -> PaymentMethod:
    method = _METHOD_ALIASES.get(str(value or '').strip().lower())
    if method is None:
        raise ValueError('Select a valid payment method')
    return method


def _parse_payment_date(value, fallback=None) -> datetime:
    if not value:
        return fallback or datetime.now(UTC)
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except ValueError as exc:
        raise ValueError('Enter a valid payment date') from exc


def _company_invoice(company_id: int, invoice_id: int | None, required=False):
    if not invoice_id:
        if required:
            raise ValueError('Select an invoice')
        return None
    invoice = Document.query.filter_by(
        id=invoice_id,
        company_id=company_id,
        type=DocumentType.invoice,
    ).first()
    if not invoice:
        raise ValueError('The selected invoice is not available')
    return invoice


def _recalculate_invoice_status(invoice_id: int, company_id: int) -> None:
    invoice = Document.query.filter_by(id=invoice_id, company_id=company_id).first()
    if not invoice:
        return
    total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.document_id == invoice_id,
        Payment.company_id == company_id,
        Payment.is_deleted.is_(False) if hasattr(Payment, 'is_deleted') else True,
    ).scalar() or 0
    if total_paid >= (invoice.total_amount or 0):
        invoice.status = DocumentStatus.paid
    elif total_paid > 0:
        invoice.status = DocumentStatus.partial
    else:
        invoice.status = DocumentStatus.sent


class PaymentService:
    @staticmethod
    def get_paginated_payments(company_id, page, per_page, search, method, date_from, date_to):
        query = Payment.query.options(
            joinedload(Payment.document).joinedload(Document.client)
        ).filter(Payment.company_id == company_id)
        if search:
            query = query.join(Document, Payment.document_id == Document.id, isouter=True).join(
                Contact, Document.client_id == Contact.id, isouter=True
            ).filter(or_(
                Document.document_number.ilike(f'%{search}%'),
                Contact.name.ilike(f'%{search}%'),
                Payment.notes.ilike(f'%{search}%'),
            ))
        if method:
            normalized = _METHOD_ALIASES.get(method.strip().lower())
            if normalized:
                query = query.filter(Payment.method == normalized)
        if date_from:
            try:
                query = query.filter(Payment.payment_date >= datetime.strptime(date_from, '%Y-%m-%d'))
            except ValueError:
                pass
        if date_to:
            try:
                exclusive_end = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Payment.payment_date < exclusive_end)
            except ValueError:
                pass
        return query.order_by(desc(Payment.payment_date)).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_total_payments(company_id):
        return db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.company_id == company_id
        ).scalar() or 0

    @staticmethod
    def get_payment(company_id, payment_id):
        return Payment.query.options(
            joinedload(Payment.document).joinedload(Document.client)
        ).filter_by(id=payment_id, company_id=company_id).first_or_404()

    @staticmethod
    def get_selected_invoice(company_id, invoice_id):
        if not invoice_id:
            return None
        return Document.query.options(joinedload(Document.client)).filter_by(
            id=invoice_id, company_id=company_id, type=DocumentType.invoice
        ).first()

    @staticmethod
    def search_invoices(company_id, search, limit=10):
        query = Document.query.options(joinedload(Document.client)).filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice,
            Document.status.in_([
                DocumentStatus.sent,
                DocumentStatus.overdue,
                DocumentStatus.pending,
                DocumentStatus.partial,
            ]),
        )
        if search:
            query = query.join(Contact, Document.client_id == Contact.id, isouter=True).filter(or_(
                Document.document_number.ilike(f'%{search}%'),
                Contact.name.ilike(f'%{search}%'),
            ))
        results = []
        for invoice in query.limit(limit).all():
            total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.company_id == company_id,
                Payment.document_id == invoice.id,
            ).scalar() or 0
            results.append({
                'id': invoice.id,
                'document_number': invoice.document_number,
                'client_name': invoice.client.name if invoice.client else '',
                'total_amount': float(invoice.total_amount or 0),
                'remaining_balance': float((invoice.total_amount or 0) - total_paid),
                'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
                'status': invoice.status.value if hasattr(invoice.status, 'value') else invoice.status,
            })
        return results

    @staticmethod
    def create_payment(company_id, data):
        try:
            document_id = int(data.get('document_id')) if data.get('document_id') else None
            invoice = _company_invoice(company_id, document_id)
            payment = Payment(
                company_id=company_id,
                document_id=document_id,
                amount=_parse_amount(data.get('amount')),
                payment_date=_parse_payment_date(data.get('payment_date')),
                method=_parse_method(data.get('method')),
                notes=(data.get('notes') or '').strip(),
            )
            db.session.add(payment)
            db.session.flush()
            if invoice:
                from app.invoices.services.accounting_integration import post_invoice_payment_income
                post_invoice_payment_income(payment, invoice)
                _recalculate_invoice_status(invoice.id, company_id)
            db.session.commit()
            return payment
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_payment(company_id, payment_id, data):
        try:
            payment = Payment.query.filter_by(id=payment_id, company_id=company_id).first_or_404()
            old_document_id = payment.document_id
            from app.models import LedgerEntry, Transaction
            old_txn = Transaction.query.join(LedgerEntry).filter(
                LedgerEntry.company_id == company_id,
                LedgerEntry.reference_type == 'Payment',
                LedgerEntry.reference_id == payment.id,
                Transaction.is_voided.is_(False),
            ).first()
            if old_txn:
                old_txn.is_voided = True
                old_txn.voided_reason = f'Replaced by edit of Payment #{payment.id}'

            new_document_id = int(data.get('document_id')) if data.get('document_id') else None
            new_invoice = _company_invoice(company_id, new_document_id)
            payment.document_id = new_document_id
            payment.amount = _parse_amount(data.get('amount'))
            payment.payment_date = _parse_payment_date(data.get('payment_date'), payment.payment_date)
            payment.method = _parse_method(data.get('method'))
            payment.notes = (data.get('notes') or '').strip()
            if new_invoice:
                from app.invoices.services.accounting_integration import post_invoice_payment_income
                post_invoice_payment_income(payment, new_invoice)
            for invoice_id in {old_document_id, new_document_id} - {None}:
                _recalculate_invoice_status(invoice_id, company_id)
            db.session.commit()
            return payment
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_payment(company_id, payment_id):
        try:
            payment = Payment.query.filter_by(id=payment_id, company_id=company_id).first_or_404()
            document_id = payment.document_id
            from app.models import LedgerEntry, Transaction
            old_txn = Transaction.query.join(LedgerEntry).filter(
                LedgerEntry.company_id == company_id,
                LedgerEntry.reference_type == 'Payment',
                LedgerEntry.reference_id == payment.id,
                Transaction.is_voided.is_(False),
            ).first()
            if old_txn:
                old_txn.is_voided = True
                old_txn.voided_reason = f'Payment #{payment.id} deleted'
            payment.is_deleted = True
            payment.deleted_at = datetime.now(UTC)
            if document_id:
                _recalculate_invoice_status(document_id, company_id)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise