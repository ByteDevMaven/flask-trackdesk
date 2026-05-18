from .base import db, BaseModel

class Company(BaseModel):
    __tablename__ = 'companies'
    name = db.Column(db.String, nullable=False, index=True)
    currency = db.Column(db.String, default='$')
    tax_rate = db.Column(db.Float, default=0.0)
    address = db.Column(db.String)
    phone = db.Column(db.String, index=True)
    email = db.Column(db.String, index=True)
    identifier = db.Column(db.String(50), index=True)
