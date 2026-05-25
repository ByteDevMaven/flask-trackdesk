from .base import db, BaseModel
from datetime import datetime, UTC

class Expense(BaseModel):
    __tablename__ = 'expenses'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    description = db.Column(db.String)
    receipt_url = db.Column(db.String)
    
    account = db.relationship('Account', backref='expenses')
    project = db.relationship('Project', backref='expenses')
    supplier = db.relationship('Contact', backref='expenses')
    company = db.relationship('Company', backref=db.backref('expenses', lazy='dynamic'))

    def __repr__(self):
        return f'<Expense {self.id}: {self.amount}>'
