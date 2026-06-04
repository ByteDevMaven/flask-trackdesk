from .base import db, BaseModel

class Company(BaseModel):
    __tablename__ = 'companies'
    
    name = db.Column(db.String(255), nullable=False, index=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(20), index=True)
    address = db.Column(db.String(512))
    #TODO: Timezone
    
    currency = db.Column(db.String(3), default='USD', nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0.0, nullable=False)
    
    __table_args__ = (
        db.CheckConstraint("tax_rate >= 0 AND tax_rate <= 100", name='check_tax_rate_range'),
        db.CheckConstraint("length(currency) = 3", name='check_currency_code_length'),
    )

    def __repr__(self) -> str:
        return f'<Company {self.id} {self.name}>'
