from .base import db, BaseModel
from .enums import PaymentMethod

class Payment(BaseModel):
    __tablename__ = 'payments'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), index=True)
    
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, index=True)
    method = db.Column(db.Enum(PaymentMethod), nullable=False, default=PaymentMethod.cash)
    notes = db.Column(db.String(1024))
    
    __table_args__ = (
        db.CheckConstraint("amount > 0", name='check_payment_amount_positive'),
    )

    def __repr__(self) -> str:
        return f'<Payment {self.id} amount={self.amount} ({self.method.value})'
