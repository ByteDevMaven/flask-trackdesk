from .base import db, BaseModel
from datetime import datetime, UTC


class LedgerEntry(BaseModel):
    """
    A single line in the accounting ledger.  Every entry MUST belong to a
    Transaction so that the paired debit/credit can be traced, voided, or
    audited together.

    Normal balance rules:
      - Asset / Expense accounts: debit increases, credit decreases
      - Liability / Equity / Revenue accounts: credit increases, debit decreases
    """
    __tablename__ = 'ledger_entries'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), index=True)

    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    description = db.Column(db.String(1024))

    # Exactly one of debit or credit must be non-zero per row
    debit = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    credit = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)

    # Polymorphic back-reference (e.g. 'Expense', 'Income', 'Payment')
    reference_type = db.Column(db.String(100), index=True)
    reference_id = db.Column(db.Integer, index=True)

    # Relationships
    account = db.relationship('Account', backref=db.backref('ledger_entries', lazy='dynamic'), lazy='select')
    project = db.relationship('Project', backref='ledger_entries', lazy='select')
    company = db.relationship('Company', backref=db.backref('ledger_entries', lazy='dynamic'), lazy='select')
    tags = db.relationship('Tag', secondary='ledger_entry_tags', backref=db.backref('ledger_entries', lazy='select'), lazy='select')

    __table_args__ = (
        # Exactly one side must be positive; both cannot be zero
        db.CheckConstraint(
            "debit >= 0 AND credit >= 0 AND (debit > 0 OR credit > 0)",
            name='check_ledger_entry_amounts'
        ),
    )

    @property
    def net_effect(self) -> float:
        """Positive = debit effect, negative = credit effect."""
        return float(self.debit or 0) - float(self.credit or 0)

    def __repr__(self) -> str:
        return f'<LedgerEntry {self.id} D={self.debit} C={self.credit} acct={self.account_id}>'
