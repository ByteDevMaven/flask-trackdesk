from .base import db, BaseModel
from datetime import datetime, UTC

class LedgerEntry(BaseModel):
    __tablename__ = 'ledger_entries'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), index=True)
    
    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)
    description = db.Column(db.String(1024))
    debit = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    credit = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    
    reference_type = db.Column(db.String(100))
    reference_id = db.Column(db.Integer)
    
    account = db.relationship('Account', backref=db.backref('ledger_entries', lazy='select'), lazy='select')
    project = db.relationship('Project', backref='ledger_entries', lazy='select')
    company = db.relationship('Company', backref=db.backref('ledger_entries', lazy='select'), lazy='select')
    tags = db.relationship('Tag', secondary='ledger_entry_tags', backref=db.backref('ledger_entries', lazy='select'), lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("debit >= 0 AND credit >= 0 AND (debit > 0 OR credit > 0)", name='check_ledger_entry_amounts'),
    )

    def __repr__(self) -> str:
        return f'<LedgerEntry {self.id} D={self.debit} C={self.credit}>'
