from datetime import datetime

from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models import Account, Document, Expense, LedgerEntry, Payment, Transaction, db
from app.models.enums import AccountType, DocumentStatus, DocumentType, TransactionType

from ._helpers import _make_naive



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
