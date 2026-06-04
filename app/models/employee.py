from .base import db, BaseModel
from .enums import EmployeeClass, PayPeriod, PTOAccrualPeriod


class Employee(BaseModel):
    __tablename__ = 'employees'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    # user_id is nullable — an employee can exist without a system user account
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, unique=True, index=True)

    # Personal info (used when no User is linked)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=True, index=True)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(512), nullable=True)

    # Employment
    employee_class = db.Column(db.Enum(EmployeeClass), nullable=False, default=EmployeeClass.full_time)
    hire_date = db.Column(db.Date, nullable=False)
    termination_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Compensation
    pay_rate = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    pay_period = db.Column(db.Enum(PayPeriod), nullable=False, default=PayPeriod.month)

    # Standard Work Schedule
    standard_start_time = db.Column(db.Time, nullable=True)
    standard_end_time = db.Column(db.Time, nullable=True)
    working_days = db.Column(db.String(32), nullable=True, default="0,1,2,3,4")  # 0=Mon, 6=Sun

    # PTO tracking
    pto_balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    pto_accrual_rate = db.Column(db.Numeric(10, 2), nullable=True)       # e.g. 1.5 (days)
    pto_accrual_period = db.Column(db.Enum(PTOAccrualPeriod), nullable=True)  # per day/month/year

    notes = db.Column(db.String(1024), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────────
    company = db.relationship('Company', backref='employees', lazy='select')
    user = db.relationship('User', backref=db.backref('employee_profile', uselist=False), lazy='select')
    leave_requests = db.relationship('LeaveRequest', backref='employee', cascade='all, delete-orphan', lazy='dynamic')
    work_schedules = db.relationship('WorkSchedule', backref='employee', cascade='all, delete-orphan', lazy='dynamic')

    # ── Helpers ──────────────────────────────────────────────────────────────
    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def display_name(self) -> str:
        """Prefer the linked user's name when available."""
        if self.user:
            return self.user.name
        return self.full_name

    def approve_pto(self, days: float) -> bool:
        """Deduct *days* from pto_balance if balance is sufficient. Returns True on success."""
        if float(self.pto_balance) >= days:
            self.pto_balance = float(self.pto_balance) - days
            return True
        return False

    def __repr__(self) -> str:
        return f'<Employee {self.id} {self.full_name} ({self.employee_class.value})>'
