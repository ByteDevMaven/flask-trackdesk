from .base import db, BaseModel
from .enums import ContactType

class Contact(BaseModel):
    __tablename__ = 'contacts'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False, index=True)
    type = db.Column(db.Enum(ContactType), nullable=False, default=ContactType.customer)
    identifier = db.Column(db.String(50), default='', index=True) # RTN etc
    email = db.Column(db.String, index=True)
    phone = db.Column(db.String, index=True)
    address = db.Column(db.String)
