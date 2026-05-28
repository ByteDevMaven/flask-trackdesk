from .base import db, BaseModel
from .enums import AccountType

class Account(BaseModel):
    __tablename__ = 'accounts'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.Enum(AccountType), nullable=False)
    balance = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    description = db.Column(db.String(1024))
    is_default = db.Column(db.Boolean, default=False, index=True)
    
    company = db.relationship('Company', backref=db.backref('accounts', lazy='select'))
    
    __table_args__ = (
        db.CheckConstraint("balance >= 0", name='check_account_balance_non_negative'),
    )

    def __repr__(self) -> str:
        return f'<Account {self.id} {self.name} ({self.type.value})'
