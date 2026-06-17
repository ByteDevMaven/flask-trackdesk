"""Accounting integration helpers for invoice payments."""

from app.accounting.services._balance import _create_balanced_transaction
from app.models import Account, LedgerEntry
from app.models.enums import AccountType, TransactionType


def _resolve_cash_account(company_id: int) -> Account:
    """Return the preferred cash/bank asset account for a company."""
    account = (
        Account.query
        .filter(
            Account.company_id == company_id,
            Account.is_active.is_(True),
            Account.type == AccountType.asset,
            (
                Account.name.ilike('%caja%') |
                Account.name.ilike('%banco%') |
                Account.name.ilike('%cash%')
            ),
        )
        .order_by(Account.is_default.desc(), Account.code, Account.name)
        .first()
    )
    if not account:
        account = (
            Account.query
            .filter_by(company_id=company_id, is_active=True, type=AccountType.asset)
            .order_by(Account.is_default.desc(), Account.code, Account.name)
            .first()
        )
    if not account:
        raise ValueError(
            'No se encontró una cuenta de efectivo (Caja/Bancos). '
            'Por favor genere las cuentas base primero.'
        )
    return account


def _resolve_revenue_account(company_id: int) -> Account:
    """Return the preferred revenue account for invoice-payment income."""
    account = (
        Account.query
        .filter_by(
            company_id=company_id,
            is_active=True,
            type=AccountType.revenue,
            default_purpose='invoice_payment_revenue',
        )
        .first()
    )
    if account:
        return account

    account = (
        Account.query
        .filter_by(company_id=company_id, is_active=True, type=AccountType.revenue)
        .order_by(
            Account.name.ilike('%productos%').desc(),
            Account.is_default.desc(),
            Account.code,
            Account.name,
        )
        .first()
    )
    if not account:
        raise ValueError(
            'No se encontró una cuenta de ingresos activa. '
            'Por favor genere las cuentas base primero.'
        )
    return account


def post_invoice_payment_income(payment, document):
    """
    Post a balanced income transaction for an invoice payment.

    The transaction reference is the invoice number so journal exports show the
    associated invoice. Ledger rows are tied to the Payment to avoid duplicate
    postings when the same payment is processed more than once.
    """
    if not payment or not document:
        return None

    existing_entry = LedgerEntry.query.filter_by(
        company_id=payment.company_id,
        reference_type='Payment',
        reference_id=payment.id,
    ).first()
    if existing_entry:
        return existing_entry.transaction

    amount = round(float(payment.amount or 0), 2)
    if amount <= 0:
        return None

    cash_account = _resolve_cash_account(payment.company_id)
    revenue_account = _resolve_revenue_account(payment.company_id)

    invoice_number = document.document_number or f'Factura #{document.id}'
    memo = f'Pago de factura {invoice_number}'
    client = getattr(document, 'client', None)
    if client and getattr(client, 'name', None):
        memo = f'{memo} ({client.name})'

    return _create_balanced_transaction(
        company_id=payment.company_id,
        date=payment.payment_date,
        memo=memo,
        transaction_type=TransactionType.income,
        entries=[
            {
                'account_id': cash_account.id,
                'debit': amount,
                'credit': 0.0,
                'description': memo,
                'project_id': document.project_id,
                'tags': [],
            },
            {
                'account_id': revenue_account.id,
                'debit': 0.0,
                'credit': amount,
                'description': memo,
                'project_id': document.project_id,
                'tags': [],
            },
        ],
        reference=invoice_number,
        reference_type='Payment',
        reference_id=payment.id,
    )
