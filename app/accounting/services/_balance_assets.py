from datetime import datetime

from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models import Account, Document, Expense, LedgerEntry, Payment, Transaction, db
from app.models.enums import AccountType, DocumentStatus, DocumentType, TransactionType

from ._helpers import _make_naive

from ._balance_predicates import _active_expense_conditions


def _is_receivable_account(account: Account) -> bool:
    if not account or account.type != AccountType.asset:
        return False
    name = (account.name or '').lower()
    return 'cobrar' in name or 'receivable' in name


def _receivable_accounts(company_id: int) -> list[Account]:
    return (
        Account.query
        .filter_by(company_id=company_id, is_active=True, type=AccountType.asset)
        .filter(
            or_(
                Account.name.ilike('%cobrar%'),
                Account.name.ilike('%receivable%'),
            )
        )
        .order_by(Account.is_default.desc(), Account.code, Account.name)
        .all()
    )


def _preferred_receivable_account(company_id: int) -> Account | None:
    accounts = _receivable_accounts(company_id)
    return accounts[0] if accounts else None


def _open_invoice_receivable_balance(company_id: int, as_of: datetime = None) -> float:
    """
    AR is the unpaid balance of invoices that are still collectible.

    It is intentionally derived from invoices/payments instead of ledger rows so
    Cuentas por Cobrar follows pending and partially paid invoices even when the
    sales/payment postings use cash-basis revenue entries.
    """
    payment_totals = (
        db.session.query(
            Payment.document_id.label('document_id'),
            func.coalesce(func.sum(Payment.amount), 0).label('paid'),
        )
        .filter(
            Payment.company_id == company_id,
            Payment.document_id.isnot(None),
        )
    )
    if as_of:
        payment_totals = payment_totals.filter(Payment.payment_date <= _make_naive(as_of))

    payment_totals = payment_totals.group_by(Payment.document_id).subquery()

    excluded_statuses = (
        DocumentStatus.draft,
        DocumentStatus.cancelled,
        DocumentStatus.credit_note,
        DocumentStatus.exchange,
    )

    query = (
        db.session.query(
            Document.total_amount,
            func.coalesce(payment_totals.c.paid, 0).label('paid'),
        )
        .outerjoin(payment_totals, payment_totals.c.document_id == Document.id)
        .filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice,
            Document.status.notin_(excluded_statuses),
        )
    )
    if as_of:
        as_of_naive = _make_naive(as_of)
        query = query.filter(
            or_(
                Document.issued_date.is_(None),
                Document.issued_date <= as_of_naive,
            )
        )

    total = 0.0
    for invoice_total, paid in query.all():
        balance_due = round(float(invoice_total or 0) - float(paid or 0), 2)
        if balance_due > 0:
            total += balance_due
    return round(total, 2)


def _replace_receivable_asset_balance(
    company_id: int,
    asset_balances_by_name: dict[str, float],
    as_of: datetime = None,
) -> dict[str, float]:
    """Return asset balances with AR replaced by open invoice balance."""
    result = dict(asset_balances_by_name or {})
    receivable_accounts = _receivable_accounts(company_id)
    if not receivable_accounts:
        return result

    for account in receivable_accounts:
        result.pop(account.name, None)

    receivable_balance = _open_invoice_receivable_balance(company_id, as_of=as_of)
    result[receivable_accounts[0].name] = receivable_balance
    return result


def _inventory_balance(company_id: int) -> float:
    from app.models.inventory_item import InventoryItem
    q = db.session.query(
        func.coalesce(func.sum(InventoryItem.quantity * InventoryItem.cost_price), 0)
    ).filter(
        InventoryItem.company_id == company_id,
        InventoryItem.is_service.is_(False)
    )
    return round(float(q.scalar()), 2)


def _replace_inventory_asset_balance(
    company_id: int,
    asset_balances_by_name: dict[str, float],
) -> dict[str, float]:
    """Return asset balances with Inventory replaced by calculated inventory value."""
    result = dict(asset_balances_by_name or {})
    inventory_accounts = (
        Account.query
        .filter_by(company_id=company_id, is_active=True, type=AccountType.asset, default_purpose='inventory_asset')
        .order_by(Account.is_default.desc(), Account.code, Account.name)
        .all()
    )
    if not inventory_accounts:
        return result

    for account in inventory_accounts:
        result.pop(account.name, None)

    inventory_val = _inventory_balance(company_id)
    result[inventory_accounts[0].name] = inventory_val
    return result


def _recent_active_expenses(company_id: int, limit: int = 10) -> list[Expense]:
    return (
        db.session.execute(
            select(Expense)
            .options(joinedload(Expense.account))
            .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
            .where(
                Expense.company_id == company_id,
                _active_expense_conditions(),
            )
            .order_by(Expense.date.desc())
            .limit(limit)
        )
        .unique()
        .scalars()
        .all()
    )
