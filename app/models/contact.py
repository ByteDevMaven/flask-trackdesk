from .base import db, BaseModel
from .enums import ContactType
import re

class Contact(BaseModel):
    __tablename__ = 'contacts'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.Enum(ContactType), nullable=False, default=ContactType.customer)
    identifier = db.Column(db.String(50), nullable=False, default='', index=True)
    
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(20), index=True)
    address = db.Column(db.String(512))
    
    company = db.relationship('Company', backref='contacts', lazy='select')

    # ── Validation ──────────────────────────────────────────────────────────
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return True  # Optional field
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone format (basic: digits, +, -, spaces)."""
        if not phone:
            return True  # Optional field
        return bool(re.match(r'^[\d+\-\s()]{7,}$', phone))

    def __repr__(self) -> str:
        return f'<Contact {self.id} {self.name} ({self.type.name})'
