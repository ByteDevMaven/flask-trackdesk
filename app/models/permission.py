from .base import db, BaseModel
from .associations import role_permissions

class Permission(BaseModel):
    __tablename__ = 'permissions'
    
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.String(512), nullable=True)
    roles = db.relationship(
        'Role', secondary=role_permissions, back_populates='permissions', lazy='select'
    )

    def __repr__(self) -> str:
        return f'<Permission {self.id} {self.name} ({len(self.roles)} roles)>'

