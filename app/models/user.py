from flask_login import UserMixin
from datetime import datetime, UTC
from .base import db, BaseModel
from .associations import user_companies

class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    active = db.Column(db.Boolean, default=True)
    name = db.Column(db.String, nullable=False, index=True)
    email = db.Column(db.String, unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), index=True)
    role = db.relationship('Role', lazy='subquery')
    companies = db.relationship('Company', secondary=user_companies, backref='users')
    last_login = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    # ── Flask-Login ────────────────────────────────────────────────────────
    @property
    def is_active(self):
        return self.active

    # ── RBAC helpers ───────────────────────────────────────────────────────
    def has_permission(self, permission_name: str) -> bool:
        """Return True if the user's role carries *permission_name*.

        Admins (role name == 'admin') bypass all checks automatically.
        """
        if not self.role:
            return False
        if self.role.name == 'admin':
            return True
        return self.role.has_permission(permission_name)

    @property
    def is_admin(self) -> bool:
        """Shortcut — True when the user's role is 'admin'."""
        return bool(self.role and self.role.name == 'admin')

    def __repr__(self) -> str:
        return f'<User {self.email}>'

