from .base import db, BaseModel

class Supplier(BaseModel):
    __tablename__ = 'suppliers'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False, index=True)
    contact_email = db.Column(db.String, index=True)
    phone = db.Column(db.String, index=True)
    address = db.Column(db.String)
