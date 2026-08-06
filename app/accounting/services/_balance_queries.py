from datetime import datetime

from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models import Account, Document, Expense, LedgerEntry, Payment, Transaction, db
from app.models.enums import AccountType, DocumentStatus, DocumentType, TransactionType

from ._helpers import _make_naive

from ._balance_predicates import _active_expense_conditions, _active_ledger_conditions


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
