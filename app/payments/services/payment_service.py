from datetime import datetime, UTC

from flask import current_app
from flask_babel import _
from sqlalchemy import or_, desc

from app.models import db, Payment, Document, DocumentType, Contact


def _recalculate_invoice_status(invoice_id: int) -> None:
    """Recalculate and update the status of the invoice based on total payments."""
    invoice = Document.query.get(invoice_id)
    if not invoice:
        return
    total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.document_id == invoice_id,
        Payment.is_deleted.is_(False) if hasattr(Payment, 'is_deleted') else True
    ).scalar() or 0

    if total_paid >= (invoice.total_amount or 0):
        invoice.status = 'paid'
    elif total_paid > 0:
        invoice.status = 'partial'
    else:
        invoice.status = 'sent'


class PaymentService:
    @staticmethod
    def get_paginated_payments(company_id, page, per_page, search, method, date_from, date_to):
        query = db.session.query(Payment).filter(
            Payment.company_id == company_id
        ).join(Document, Payment.document_id == Document.id, isouter=True)\
         .join(Contact, Document.client_id == Contact.id, isouter=True)

        if search:
            query = query.filter(
                or_(
                    Document.document_number.ilike(f'%{search}%'),
                    Contact.name.ilike(f'%{search}%'),
                    Payment.notes.ilike(f'%{search}%')
                )
            )

        if method:
            query = query.filter(Payment.method == method)

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Payment.payment_date >= date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(Payment.payment_date <= date_to_obj)
            except ValueError:
                pass

        query = query.order_by(desc(Payment.payment_date))

        return query.paginate(  # type: ignore
            page=page,
            per_page=per_page,
            error_out=False
        )

    @staticmethod
    def get_total_payments(company_id):
        return db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.company_id == company_id
        ).scalar() or 0

    @staticmethod
    def get_payment(company_id, payment_id):
        payment = Payment.query.filter(
            Payment.id == payment_id,
            Payment.company_id == company_id
        ).first_or_404()

        if payment.document_id:
            payment.document = Document.query.get(payment.document_id)
            if payment.document and payment.document.client_id:
                payment.document.client = Contact.query.get(payment.document.client_id)

        return payment

    @staticmethod
    def get_selected_invoice(company_id, invoice_id):
        if not invoice_id:
            return None
        invoice = Document.query.filter(
            Document.id == invoice_id,
            Document.company_id == company_id,
            Document.type == DocumentType.invoice
        ).first()
        if invoice and invoice.client_id:
            invoice.client = Contact.query.get(invoice.client_id)
        return invoice

    @staticmethod
    def search_invoices(company_id, search, limit=10):
        query = db.session.query(Document).filter(
            Document.company_id == company_id,
            or_(
                Document.status == 'sent',
                Document.status == 'overdue',
                Document.status == 'pending'
            )
        ).join(Contact, Document.client_id == Contact.id, isouter=True)

        if search:
            query = query.filter(
                or_(
                    Document.document_number.ilike(f'%{search}%'),
                    Contact.name.ilike(f'%{search}%')
                )
            )

        invoices = query.limit(limit).all()
        results = []
        for invoice in invoices:
            total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.document_id == invoice.id
            ).scalar() or 0

            remaining_balance = (invoice.total_amount or 0) - total_paid

            client_name = ''
            if invoice.client_id:
                client = Contact.query.get(invoice.client_id)
                client_name = client.name if client else ''

            results.append({
                'id': invoice.id,
                'document_number': invoice.document_number,
                'client_name': client_name,
                'total_amount': invoice.total_amount or 0,
                'remaining_balance': remaining_balance,
                'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
                'status': invoice.status
            })

        return results

    @staticmethod
    def create_payment(company_id, data):
        payment = Payment(
            company_id=company_id,  # type: ignore
            document_id=int(data.get('document_id')) if data.get('document_id') else None,  # type: ignore
            amount=float(data.get('amount', 0)),  # type: ignore
            payment_date=datetime.strptime(data.get('payment_date'), '%Y-%m-%d') if data.get('payment_date') else datetime.now(UTC),  # type: ignore
            method=data.get('method', ''),  # type: ignore
            notes=data.get('notes', '')  # type: ignore
        )

        db.session.add(payment)
        db.session.flush()

        # Update invoice status and post accounting entry after adding payment
        if payment.document_id:
            invoice = Document.query.get(payment.document_id)
            if invoice:
                from app.invoices.services.accounting_integration import post_invoice_payment_income
                post_invoice_payment_income(payment, invoice)

                total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
                    Payment.document_id == invoice.id
                ).scalar() or 0

                if total_paid >= (invoice.total_amount or 0):
                    invoice.status = 'paid'
                elif total_paid > 0:
                    invoice.status = 'pending'

        db.session.commit()
        return payment

    @staticmethod
    def update_payment(company_id, payment_id, data):
        payment = Payment.query.filter(
            Payment.id == payment_id,
            Payment.company_id == company_id
        ).first_or_404()

        old_document_id = payment.document_id

        payment.document_id = int(data.get('document_id')) if data.get('document_id') else None  # type: ignore
        payment.amount = float(data.get('amount', 0))
        payment.payment_date = datetime.strptime(data.get('payment_date'), '%Y-%m-%d') if data.get('payment_date') else payment.payment_date  # type: ignore
        payment.method = data.get('method', payment.method)
        payment.notes = data.get('notes', payment.notes)

        invoices_to_update = set()
        if old_document_id:
            invoices_to_update.add(old_document_id)
        if payment.document_id:
            invoices_to_update.add(payment.document_id)

        for invoice_id in invoices_to_update:
            _recalculate_invoice_status(invoice_id)

        db.session.commit()
        return payment

    @staticmethod
    def delete_payment(company_id, payment_id):
        payment = Payment.query.filter(
            Payment.id == payment_id,
            Payment.company_id == company_id
        ).first_or_404()

        document_id = payment.document_id

        payment.is_deleted = True
        payment.deleted_at = datetime.now(UTC)

        if document_id:
            _recalculate_invoice_status(document_id)

        db.session.commit()
        return True
