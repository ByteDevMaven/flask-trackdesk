"""
AccountingService — complete double-entry bookkeeping service.

This module re-exports the accounting service which is now split into multiple focused modules.
"""
from datetime import datetime
from app.models import Account

from ._balance import _compute_account_balance, _compute_balances_bulk
from .account_service import AccountService
from .dashboard_service import DashboardService
from .expense_service import ExpenseService
from .income_service import IncomeService
from .journal_service import JournalService
from .project_service import ProjectService


class AccountingService(
    AccountService,
    DashboardService,
    ExpenseService,
    IncomeService,
    JournalService,
    ProjectService
):
    """
    Main AccountingService facade.
    Inherits all @staticmethod methods from the domain-specific services.
    """

    # ── Account balance (convenience methods) ──────────────────────────────

    @staticmethod
    def get_account_balance(account: Account, as_of: datetime = None) -> float:
        return _compute_account_balance(account, as_of=as_of)

    @staticmethod
    def get_account_balances_bulk(company_id: int, as_of: datetime = None) -> dict[int, float]:
        return _compute_balances_bulk(company_id, as_of=as_of)
