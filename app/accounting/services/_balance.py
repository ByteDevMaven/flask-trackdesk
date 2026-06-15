"""
Core double-entry balance computation and transaction factory.

Design rules:
  1. Every financial event creates exactly ONE Transaction row.
  2. Every Transaction contains >= 2 LedgerEntry rows whose
     total debits == total credits (balanced).
  3. Account balances are NEVER stored — always computed from LedgerEntry.
  4. Normal balance: Asset/Expense → debit; Liability/Equity/Revenue → credit.
"""
from datetime import datetime

from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models import db, Account, Document, Expense, LedgerEntry, Payment, Transaction
from app.models.enums import AccountType, DocumentStatus, DocumentType, TransactionType

from ._helpers import _make_naive


# ── Active-row predicates ──────────────────────────────────────────────────

def _active_ledger_conditions():
    """Ledger rows count only when unlinked or tied to a non-voided transaction."""
    return or_(
        LedgerEntry.transaction_id.is_(None),
        Transaction.is_voided.is_(False),
    )


def _active_expense_conditions():
    """Expense rows count only when unlinked or tied to a non-voided transaction."""
    return or_(
        Expense.transaction_id.is_(None),
        Transaction.is_voided.is_(False),
    )


# ── Revenue helpers ────────────────────────────────────────────────────────

def _ledger_revenue_by_account(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> dict[str, float]:
    q = (
        LedgerEntry.query
        .join(Account, LedgerEntry.account_id == Account.id)
        .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .filter(
            LedgerEntry.company_id == company_id,
            Account.type == AccountType.revenue,
            _active_ledger_conditions(),
        )
    )
    if project_id is not None:
        q = q.filter(LedgerEntry.project_id == project_id)
    if start_dt is not None:
        q = q.filter(LedgerEntry.date >= _make_naive(start_dt))
    if end_dt is not None:
        q = q.filter(LedgerEntry.date <= _make_naive(end_dt))

    result: dict[str, float] = {}
    for entry in q.all():
        acc_name = entry.account.name
        net = float(entry.credit) - float(entry.debit)
        result[acc_name] = round(result.get(acc_name, 0.0) + net, 2)
    return result


def _merge_account_amounts(*parts: dict[str, float]) -> dict[str, float]:
    merged: dict[str, float] = {}
    for part in parts:
        for name, amount in part.items():
            merged[name] = round(merged.get(name, 0.0) + float(amount), 2)
    return {name: amount for name, amount in merged.items() if round(amount, 2) != 0}


# ── Expense helpers ────────────────────────────────────────────────────────

def _registered_expenses_by_account(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> dict[str, float]:
    """Gastos registrados en el módulo Gastos (tabla expenses)."""
    account_label = func.coalesce(Account.name, 'Sin cuenta')
    q = (
        db.session.query(
            account_label,
            func.coalesce(func.sum(Expense.amount), 0),
        )
        .select_from(Expense)
        .outerjoin(Account, Expense.account_id == Account.id)
        .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
        .filter(
            Expense.company_id == company_id,
            _active_expense_conditions(),
        )
    )
    if project_id is not None:
        q = q.filter(Expense.project_id == project_id)
    if start_dt is not None:
        q = q.filter(Expense.date >= _make_naive(start_dt))
    if end_dt is not None:
        q = q.filter(Expense.date <= _make_naive(end_dt))

    return {
        name: round(float(amount), 2)
        for name, amount in q.group_by(account_label).all()
        if float(amount) > 0
    }


def _ledger_manual_expenses_by_account(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> dict[str, float]:
    """
    Débitos/créditos en cuentas de gasto desde asientos manuales u otros
    movimientos que no son gastos registrados (reference_type != 'Expense').
    """
    q = (
        LedgerEntry.query
        .join(Account, LedgerEntry.account_id == Account.id)
        .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .filter(
            LedgerEntry.company_id == company_id,
            Account.type == AccountType.expense,
            _active_ledger_conditions(),
            or_(
                LedgerEntry.reference_type.is_(None),
                LedgerEntry.reference_type != 'Expense',
            ),
        )
    )
    if project_id is not None:
        q = q.filter(LedgerEntry.project_id == project_id)
    if start_dt is not None:
        q = q.filter(LedgerEntry.date >= _make_naive(start_dt))
    if end_dt is not None:
        q = q.filter(LedgerEntry.date <= _make_naive(end_dt))

    result: dict[str, float] = {}
    for entry in q.all():
        acc_name = entry.account.name
        net = float(entry.debit) - float(entry.credit)
        result[acc_name] = round(result.get(acc_name, 0.0) + net, 2)
    return result


def _expenses_by_account(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> dict[str, float]:
    """Registered gastos + manual journal activity on expense accounts."""
    return _merge_account_amounts(
        _registered_expenses_by_account(company_id, start_dt, end_dt, project_id),
        _ledger_manual_expenses_by_account(company_id, start_dt, end_dt, project_id),
    )


def _period_expense_total(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> float:
    return round(
        sum(_expenses_by_account(company_id, start_dt, end_dt, project_id).values()),
        2,
    )


def _period_revenue_total(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> float:
    return round(
        sum(_ledger_revenue_by_account(company_id, start_dt, end_dt, project_id).values()),
        2,
    )


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


# ── Account balance computation ────────────────────────────────────────────

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
    return result


# ── Transaction factory ────────────────────────────────────────────────────

def _create_balanced_transaction(
    company_id: int,
    date: datetime,
    memo: str,
    transaction_type: TransactionType,
    entries: list[dict],
    reference: str = None,
    reference_type: str = None,
    reference_id: int = None,
) -> Transaction:
    """
    Create a Transaction + LedgerEntry rows atomically.
    Raises ValueError if entries do not balance (total debit ≠ total credit).
    """
    total_debit = round(sum(float(e.get('debit', 0)) for e in entries), 2)
    total_credit = round(sum(float(e.get('credit', 0)) for e in entries), 2)
    if total_debit != total_credit:
        raise ValueError(
            f"Journal entry is not balanced: total debit {total_debit} ≠ total credit {total_credit}"
        )

    created_by_id = None
    try:
        created_by_id = current_user.id if current_user.is_authenticated else None
    except Exception:
        pass

    txn = Transaction(
        company_id=company_id,
        date=_make_naive(date),
        memo=memo,
        reference=reference,
        transaction_type=transaction_type,
        created_by=created_by_id,
    )
    db.session.add(txn)
    db.session.flush()

    for e in entries:
        entry = LedgerEntry(
            company_id=company_id,
            account_id=e['account_id'],
            transaction_id=txn.id,
            project_id=e.get('project_id'),
            date=_make_naive(date),
            description=e.get('description', memo),
            debit=round(float(e.get('debit', 0)), 2),
            credit=round(float(e.get('credit', 0)), 2),
            reference_type=reference_type,
            reference_id=reference_id,
            tags=e.get('tags', []),
        )
        db.session.add(entry)

    return txn
