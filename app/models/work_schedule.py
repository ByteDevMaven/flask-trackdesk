from .base import db, BaseModel


class WorkSchedule(BaseModel):
    __tablename__ = 'work_schedules'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)

    # Date of this shift / working day
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    notes = db.Column(db.String(512), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────────
    company = db.relationship('Company', lazy='select')

    # ── Helpers ──────────────────────────────────────────────────────────────
    @property
    def hours_worked(self) -> float:
        """Total hours for this schedule entry."""
        if self.start_time and self.end_time:
            from datetime import datetime
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            delta = end - start
            return round(delta.total_seconds() / 3600, 2)
        return 0.0

    def __repr__(self) -> str:
        return f'<WorkSchedule {self.id} emp={self.employee_id} {self.date} {self.start_time}–{self.end_time}>'
