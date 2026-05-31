from flask_login import UserMixin
from .base import db, BaseModel
from .associations import user_companies
from .enums import UserStatus
import re

class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    
    name = db.Column(db.String(255), nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.active, nullable=False)
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), index=True)
    role = db.relationship('Role', lazy='select')
    companies = db.relationship('Company', secondary=user_companies, backref='users', lazy='select')
    
    last_login = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='check_user_status'),
    )

    @property
    def is_active(self):
        return self.status == UserStatus.active

    def has_permission(self, permission_name: str) -> bool:
        """Return True if the user's role carries *permission_name*.
        Superadmins (role name == 'superadmin') bypass all checks automatically.
        """
        if not self.role:
            return False
        if self.role.name == 'superadmin':
            return True
        return self.role.has_permission(permission_name)

    @property
    def is_admin(self) -> bool:
        """Shortcut — True when the user's role is 'superadmin' (platform admin)."""
        return bool(self.role and self.role.name == 'superadmin')

    @property
    def is_superadmin(self) -> bool:
        """Alias for is_admin."""
        return self.is_admin

    @property
    def is_owner(self) -> bool:
        """True when the user's role is 'owner' (company-level admin)."""
        return bool(self.role and self.role.name == 'owner')

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def __repr__(self) -> str:
        return f'<User {self.id} {self.email} ({self.role.name if self.role else "no-role"})'

