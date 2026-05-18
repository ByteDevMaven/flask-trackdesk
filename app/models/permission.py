from .base import db, BaseModel
from .associations import role_permissions

class Permission(BaseModel):
    __tablename__ = 'permissions'
    name = db.Column(db.String, nullable=False, unique=True, index=True)
    roles = db.relationship('Role', secondary=role_permissions, back_populates='permissions')
