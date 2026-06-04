import os
from .base import db, BaseModel
from .enums import LeaveType, LeaveStatus


class LeaveRequest(BaseModel):
    __tablename__ = 'leave_requests'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)

    leave_type = db.Column(db.Enum(LeaveType), nullable=False)
    status = db.Column(db.Enum(LeaveStatus), nullable=False, default=LeaveStatus.pending, index=True)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    reason = db.Column(db.String(1024), nullable=True)
    attachment_path = db.Column(db.String(512), nullable=True)  # relative path inside uploads/

    # Who acted on this request
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_note = db.Column(db.String(512), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────────
    company = db.relationship('Company', lazy='select')
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id], lazy='select')

    # ── Helpers ──────────────────────────────────────────────────────────────
    @property
    def total_days(self) -> int:
        """Calendar days of the leave (inclusive)."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def attachment_filename(self) -> str | None:
        if self.attachment_path:
            return os.path.basename(self.attachment_path)
        return None

    def __repr__(self) -> str:
        return f'<LeaveRequest {self.id} emp={self.employee_id} {self.leave_type.value} [{self.status.value}]>'
