from .base import db, BaseModel
from .enums import PaymentMethod

class Payment(BaseModel):
    __tablename__ = 'payments'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), index=True)
    amount = db.Column(db.Float)
    payment_date = db.Column(db.DateTime)
    method = db.Column(db.Enum(PaymentMethod), nullable=False, default=PaymentMethod.cash)
    notes = db.Column(db.String)
