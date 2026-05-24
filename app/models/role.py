from .base import db, BaseModel
from .associations import role_permissions

class Role(BaseModel):
    __tablename__ = 'roles'
    name = db.Column(db.String, nullable=False, unique=True, index=True)
    description = db.Column(db.String, nullable=True)
    permissions = db.relationship(
        'Permission', secondary=role_permissions, back_populates='roles', lazy='subquery'
    )

    def has_permission(self, permission_name: str) -> bool:
        """Return True if this role carries *permission_name*."""
        return any(p.name == permission_name for p in self.permissions)

    def __repr__(self) -> str:
        return f'<Role {self.name}>'

