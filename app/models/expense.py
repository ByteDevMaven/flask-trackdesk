from .base import db, BaseModel
from datetime import datetime, UTC
from .enums import ExpenseStatus


class Expense(BaseModel):
    """
    Represents a business expense (outflow of money).

    Income / revenue is recorded separately via LedgerEntry with
    TransactionType.income — Expense is for outflows only.

    When an Expense is created, the service layer MUST also write a balanced
    Transaction + two LedgerEntry rows (debit expense account, credit cash/AP).
    """
    __tablename__ = 'expenses'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), index=True)

    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), index=True)
    description = db.Column(db.String(1024))

    # Quick vendor entry without requiring a full Contact record
    vendor_name = db.Column(db.String(255))

    # Optional user-defined category label (separate from account type)
    category = db.Column(db.String(100), index=True)

    # File attachment (e.g. receipt image or PDF)
    receipt_url = db.Column(db.String(512))

    # Approval workflow
    status = db.Column(
        db.Enum(ExpenseStatus),
        nullable=False,
        default=ExpenseStatus.draft,
        index=True
    )

    # Relationships
    account = db.relationship('Account', backref='expenses', lazy='select')
    project = db.relationship('Project', backref='expenses', lazy='select')
    supplier = db.relationship('Contact', backref='expenses', lazy='select')
    company = db.relationship('Company', backref=db.backref('expenses', lazy='select'), lazy='select')
    tags = db.relationship('Tag', secondary='expense_tags', backref=db.backref('expenses', lazy='select'), lazy='select')
    linked_transaction = db.relationship('Transaction', foreign_keys=[transaction_id], lazy='select')

    __table_args__ = (
        db.CheckConstraint("amount > 0", name='check_expense_amount_positive'),
    )

    @property
    def vendor_display(self) -> str:
        """Resolve vendor name from supplier relation or vendor_name field."""
        if self.supplier:
            return self.supplier.name
        return self.vendor_name or '—'

    def __repr__(self) -> str:
        return f'<Expense {self.id} {self.amount} [{self.status.value}]>'
