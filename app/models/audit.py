from .base import db, BaseModel


class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    action = db.Column(db.String(100), nullable=False, index=True)
    table_name = db.Column(db.String(100), nullable=False, index=True)
    record_id = db.Column(db.Integer)

    old_data = db.Column(db.JSON)
    new_data = db.Column(db.JSON)

    user = db.relationship('User', backref='audit_logs', lazy='select')
    company = db.relationship('Company', backref='audit_logs', lazy='select')

    def __repr__(self) -> str:
        return f'<AuditLog {self.id} {self.action} on {self.table_name}>'