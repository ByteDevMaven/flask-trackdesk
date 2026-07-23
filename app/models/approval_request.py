from .base import db, BaseModel
from .enums import ApprovalStatus
from datetime import datetime, UTC

class ApprovalRequest(BaseModel):
    __tablename__ = 'approval_requests'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    action_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    status = db.Column(db.Enum(ApprovalStatus), default=ApprovalStatus.pending, nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    company = db.relationship('Company', backref='approval_requests', lazy='select')
    requester = db.relationship('User', foreign_keys=[requester_id], backref='approval_requests_made', lazy='select')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approval_requests_resolved', lazy='select')

    def __repr__(self) -> str:
        return f'<ApprovalRequest {self.id} {self.action_type} {self.status.value}>'
