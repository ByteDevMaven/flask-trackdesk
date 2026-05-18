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
    companies = db.relationship('Company', secondary=user_companies, backref='users')
    last_login = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
