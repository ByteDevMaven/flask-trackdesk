from .base import db, BaseModel
from datetime import datetime, UTC
from .enums import TransactionType


class Transaction(BaseModel):
    """
    Groups one or more paired LedgerEntry rows into an atomic double-entry
    journal entry. Every set of balanced debits/credits MUST belong to a
    Transaction so they can be voided or audited as a unit.
    """
    __tablename__ = 'transactions'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)

    # Human-readable memo (e.g. "Office rent – June 2026")
    memo = db.Column(db.String(512), nullable=False, default='')

    # Optional external reference (invoice number, receipt number, etc.)
    reference = db.Column(db.String(128), index=True)

    # Categorisation for filtering / reporting
    transaction_type = db.Column(
        db.Enum(TransactionType),
        nullable=False,
        default=TransactionType.journal,
        index=True
    )

    # Who created this entry
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    # Soft-delete / void flag
    is_voided = db.Column(db.Boolean, default=False, nullable=False, index=True)
    voided_reason = db.Column(db.String(512))

    # Relationships
    company = db.relationship('Company', backref=db.backref('transactions', lazy='dynamic'))
    created_by_user = db.relationship('User', foreign_keys=[created_by])
    entries = db.relationship(
        'LedgerEntry',
        backref='transaction',
        cascade='all, delete-orphan',
        lazy='select'
    )

    # ── Validation helpers ──────────────────────────────────────────────────

    def is_balanced(self) -> bool:
        """Return True if total debits == total credits across all entries."""
        total_debit = sum(float(e.debit or 0) for e in self.entries)
        total_credit = sum(float(e.credit or 0) for e in self.entries)
        return round(total_debit, 2) == round(total_credit, 2)

    def total_amount(self) -> float:
        """Return the transaction amount (sum of debit side)."""
        return round(sum(float(e.debit or 0) for e in self.entries), 2)

    def __repr__(self) -> str:
        return f'<Transaction {self.id} {self.transaction_type.value} {self.memo[:40]}>'
