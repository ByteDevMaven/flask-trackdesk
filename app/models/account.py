from .base import db, BaseModel
from .enums import AccountType

class Account(BaseModel):
    __tablename__ = 'accounts'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum(AccountType), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    description = db.Column(db.String)
    is_default = db.Column(db.Boolean, default=False)
    
    company = db.relationship('Company', backref=db.backref('accounts', lazy='dynamic'))

    def __repr__(self):
        return f'<Account {self.name}>'
