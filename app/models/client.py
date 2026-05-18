from .base import db, BaseModel

class Client(BaseModel):
    __tablename__ = 'clients'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False, index=True)
    identifier = db.Column(db.String(50), default='', nullable=False, index=True)
    email = db.Column(db.String, index=True)
    phone = db.Column(db.String, index=True)
    address = db.Column(db.String)
