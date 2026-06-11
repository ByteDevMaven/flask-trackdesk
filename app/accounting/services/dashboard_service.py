"""Dashboard aggregation service."""
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models import db, Account, Company, Expense, Project, Transaction
from app.models.enums import AccountType

from ._helpers import _make_naive
from ._balance import (
    _active_expense_conditions,
    _compute_balances_bulk,
    _period_expense_total,
    _period_revenue_total,
    _recent_active_expenses,
)


class DashboardService:

    @staticmethod
    def get_dashboard_data(company_id: int) -> dict:
        company = Company.query.get_or_404(company_id)

        accounts = (
            Account.query
            .filter_by(company_id=company_id, is_active=True)
            .order_by(Account.type, Account.name)
            .all()
        )
        projects = Project.query.filter_by(company_id=company_id).all()
        expenses = _recent_active_expenses(company_id, limit=10)
        recent_transactions = (
            Transaction.query
            .filter_by(company_id=company_id, is_voided=False)
            .order_by(Transaction.date.desc())
            .limit(15)
            .all()
        )

        balances = _compute_balances_bulk(company_id)

        now = _make_naive(datetime.now(UTC))
        month_start = now.replace(day=1, hour=0, minute=0, second=0)

        revenue_month = _period_revenue_total(company_id, month_start, now)
        expenses_month = _period_expense_total(company_id, start_dt=month_start, end_dt=now)
        net_income_month = round(revenue_month - expenses_month, 2)

        total_revenue = _period_revenue_total(company_id)
        total_expenses = _period_expense_total(company_id)
        net_income_all = round(total_revenue - total_expenses, 2)

        account_map = {acc.id: acc for acc in accounts}

        cash_balance = sum(
            balances.get(acc.id, 0.0) for acc in accounts
            if 'caja' in acc.name.lower() or 'banco' in acc.name.lower() or 'cash' in acc.name.lower()
        )
        ar_balance = sum(
            balances.get(acc.id, 0.0) for acc in accounts
            if 'cobrar' in acc.name.lower() or 'receivable' in acc.name.lower()
        )
        ap_balance = sum(
            balances.get(acc.id, 0.0) for acc in accounts
            if 'pagar' in acc.name.lower() or 'payable' in acc.name.lower()
        )

        expense_stats = (
            db.session.query(Expense.project_id, func.sum(Expense.amount))
            .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
            .filter(
                Expense.company_id == company_id,
                Expense.project_id.isnot(None),
                _active_expense_conditions(),
            )
            .group_by(Expense.project_id)
            .all()
        )
        project_spent = {row[0]: float(row[1] or 0) for row in expense_stats}

        tag_totals: dict[str, float] = {}
        active_expense_rows = (
            db.session.execute(
                select(Expense)
                .options(joinedload(Expense.tags))
                .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
                .where(
                    Expense.company_id == company_id,
                    _active_expense_conditions(),
                )
            )
            .unique()
            .scalars()
            .all()
        )
        for e in active_expense_rows:
            if not e.tags:
                tag_totals['Sin Etiqueta'] = tag_totals.get('Sin Etiqueta', 0.0) + float(e.amount)
            for t in e.tags:
                tag_totals[t.name] = tag_totals.get(t.name, 0.0) + float(e.amount)

        return {
            'company': company,
            'accounts': accounts,
            'expenses': expenses,
            'recent_transactions': recent_transactions,
            'projects': projects,
            'balances': balances,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_income_all': net_income_all,
            'revenue_month': revenue_month,
            'expenses_month': expenses_month,
            'net_income_month': net_income_month,
            'cash_balance': cash_balance,
            'ar_balance': ar_balance,
            'ap_balance': ap_balance,
            'type_totals': {
                'revenue': total_revenue,
                'expense': total_expenses,
                'asset': sum(
                    v for aid, v in balances.items()
                    if aid in account_map and account_map[aid].type == AccountType.asset
                ),
            },
            'tag_totals': tag_totals,
            'project_spent': project_spent,
            'expense_counts': {row[0]: row[1] for row in (
                db.session.query(Expense.project_id, func.count(Expense.id))
                .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
                .filter(
                    Expense.company_id == company_id,
                    Expense.project_id.isnot(None),
                    _active_expense_conditions(),
                )
                .group_by(Expense.project_id)
                .all()
            )},
        }
