from .base import db, BaseModel
from .associations import role_permissions

class Role(BaseModel):
    __tablename__ = 'roles'
    name = db.Column(db.String, nullable=False, unique=True, index=True)
    permissions = db.relationship('Permission', secondary=role_permissions, back_populates='roles')
