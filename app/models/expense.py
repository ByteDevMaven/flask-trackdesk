from .base import db, BaseModel
from datetime import datetime, UTC

class Expense(BaseModel):
    __tablename__ = 'expenses'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), index=True)
    description = db.Column(db.String(1024))
    receipt_url = db.Column(db.String(512))
    
    account = db.relationship('Account', backref='expenses', lazy='select')
    project = db.relationship('Project', backref='expenses', lazy='select')
    supplier = db.relationship('Contact', backref='expenses', lazy='select')
    company = db.relationship('Company', backref=db.backref('expenses', lazy='select'), lazy='select')
    tags = db.relationship('Tag', secondary='expense_tags', backref=db.backref('expenses', lazy='select'), lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("amount > 0", name='check_expense_amount_positive'),
    )

    def __repr__(self) -> str:
        return f'<Expense {self.id} {self.amount}>'
