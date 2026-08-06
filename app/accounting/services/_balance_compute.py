from datetime import datetime

from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models import Account, Document, Expense, LedgerEntry, Payment, Transaction, db
from app.models.enums import AccountType, DocumentStatus, DocumentType, TransactionType

from ._helpers import _make_naive

from ._balance_assets import (_inventory_balance, _is_receivable_account, _open_invoice_receivable_balance, _preferred_receivable_account, _receivable_accounts)
from ._balance_predicates import _active_ledger_conditions


def _compute_account_balance(account: Account, as_of: datetime = None) -> float:
    """
    Compute the current balance of an account from LedgerEntry rows.

    Normal balance rules:
      - Asset / Expense:               balance = SUM(debit) - SUM(credit)
      - Liability / Equity / Revenue:  balance = SUM(credit) - SUM(debit)
    """
    if _is_receivable_account(account):
        preferred = _preferred_receivable_account(account.company_id)
        if preferred and preferred.id != account.id:
            return 0.0
        return _open_invoice_receivable_balance(account.company_id, as_of=as_of)

    if account.default_purpose == 'inventory_asset':
        inventory_accounts = (
            Account.query
            .filter_by(company_id=account.company_id, is_active=True, type=AccountType.asset, default_purpose='inventory_asset')
            .order_by(Account.is_default.desc(), Account.code, Account.name)
            .all()
        )
        if inventory_accounts and inventory_accounts[0].id != account.id:
            return 0.0
        if account.type == AccountType.asset:
            return _inventory_balance(account.company_id)

    q = (
        db.session.query(
            func.coalesce(func.sum(LedgerEntry.debit), 0).label('total_debit'),
            func.coalesce(func.sum(LedgerEntry.credit), 0).label('total_credit'),
        )
        .select_from(LedgerEntry)
        .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.company_id == account.company_id,
            _active_ledger_conditions(),
        )
    )
    if as_of:
        q = q.filter(LedgerEntry.date <= _make_naive(as_of))

    row = q.one()
    total_debit = float(row.total_debit)
    total_credit = float(row.total_credit)

    if account.type in (AccountType.asset, AccountType.expense):
        return round(total_debit - total_credit, 2)
    else:
        return round(total_credit - total_debit, 2)


def _compute_balances_bulk(
    company_id: int,
    account_type_filter=None,
    as_of: datetime = None,
) -> dict[int, float]:
    """
    Compute balances for ALL accounts of a company in one query.
    Returns {account_id: balance}.
    """
    q = (
        db.session.query(
            LedgerEntry.account_id,
            Account.type,
            func.coalesce(func.sum(LedgerEntry.debit), 0).label('d'),
            func.coalesce(func.sum(LedgerEntry.credit), 0).label('c'),
        )
        .select_from(LedgerEntry)
        .join(Account, LedgerEntry.account_id == Account.id)
        .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .filter(
            LedgerEntry.company_id == company_id,
            _active_ledger_conditions(),
        )
    )
    if account_type_filter:
        if isinstance(account_type_filter, (list, tuple)):
            q = q.filter(Account.type.in_(account_type_filter))
        else:
            q = q.filter(Account.type == account_type_filter)
    if as_of:
        q = q.filter(LedgerEntry.date <= _make_naive(as_of))

    result: dict[int, float] = {}
    for account_id, acct_type, d, c in q.group_by(LedgerEntry.account_id, Account.type).all():
        d, c = float(d), float(c)
        if acct_type in (AccountType.asset, AccountType.expense):
            result[account_id] = round(d - c, 2)
        else:
            result[account_id] = round(c - d, 2)

    receivable_accounts = _receivable_accounts(company_id)
    if receivable_accounts and (
        account_type_filter is None
        or account_type_filter == AccountType.asset
        or (isinstance(account_type_filter, (list, tuple)) and AccountType.asset in account_type_filter)
    ):
        receivable_balance = _open_invoice_receivable_balance(company_id, as_of=as_of)
        preferred = receivable_accounts[0]
        result[preferred.id] = receivable_balance
        for account in receivable_accounts[1:]:
            result[account.id] = 0.0

    inventory_accounts = (
        Account.query
        .filter_by(company_id=company_id, is_active=True, type=AccountType.asset, default_purpose='inventory_asset')
        .order_by(Account.is_default.desc(), Account.code, Account.name)
        .all()
    )
    if inventory_accounts and (
        account_type_filter is None
        or account_type_filter == AccountType.asset
        or (isinstance(account_type_filter, (list, tuple)) and AccountType.asset in account_type_filter)
    ):
        inventory_val = _inventory_balance(company_id)
        preferred_inv = inventory_accounts[0]
        result[preferred_inv.id] = inventory_val
        for account in inventory_accounts[1:]:
            result[account.id] = 0.0

    return result
