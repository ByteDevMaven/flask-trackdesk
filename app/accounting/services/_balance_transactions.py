from datetime import datetime

from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models import Account, Document, Expense, LedgerEntry, Payment, Transaction, db
from app.models.enums import AccountType, DocumentStatus, DocumentType, TransactionType

from ._helpers import _make_naive



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
