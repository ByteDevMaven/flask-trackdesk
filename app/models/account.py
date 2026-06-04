from .base import db, BaseModel
from .enums import AccountType


class Account(BaseModel):
    """
    Chart of Accounts entry.

    IMPORTANT: Balance is NOT stored here — it is always computed from
    LedgerEntry rows to avoid dual-source drift.  Use
    AccountingService.get_account_balance(account_id) for a real-time figure.
    """
    __tablename__ = 'accounts'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)

    # Standard account code, e.g. "1100", "4000"
    code = db.Column(db.String(20), nullable=True, index=True)

    name = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.Enum(AccountType), nullable=False)
    description = db.Column(db.String(1024))
    is_default = db.Column(db.Boolean, default=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    company = db.relationship('Company', backref=db.backref('accounts', lazy='select'))

    # ── Normal balance helpers ──────────────────────────────────────────────

    @property
    def normal_balance(self) -> str:
        """Accounts that normally carry a debit balance vs credit balance."""
        if self.type in (AccountType.asset, AccountType.expense):
            return 'debit'
        return 'credit'

    def __repr__(self) -> str:
        code_str = f' [{self.code}]' if self.code else ''
        return f'<Account {self.id}{code_str} {self.name} ({self.type.value})>'
