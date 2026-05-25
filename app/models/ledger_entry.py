from .base import db, BaseModel
from datetime import datetime, UTC

class LedgerEntry(BaseModel):
    __tablename__ = 'ledger_entries'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), index=True)
    
    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    description = db.Column(db.String)
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    
    reference_type = db.Column(db.String)
    reference_id = db.Column(db.Integer)
    
    account = db.relationship('Account', backref=db.backref('ledger_entries', lazy='dynamic'))
    project = db.relationship('Project', backref='ledger_entries')
    company = db.relationship('Company', backref=db.backref('ledger_entries', lazy='dynamic'))

    def __repr__(self):
        return f'<LedgerEntry {self.id}: Debit {self.debit}, Credit {self.credit}>'
