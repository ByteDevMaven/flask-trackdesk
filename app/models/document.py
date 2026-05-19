from .base import db, BaseModel
from .enums import DocumentType, InvoiceType

class Document(BaseModel):
    __tablename__ = 'documents'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    document_number = db.Column(db.String, unique=True, nullable=False, index=True)
    type = db.Column(db.Enum(DocumentType), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    status = db.Column(db.Enum(InvoiceType), nullable=False, default=InvoiceType.draft)
    total_amount = db.Column(db.Float)
    issued_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)

    client = db.relationship('Contact', backref='documents')
    payments = db.relationship('Payment', backref='document', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def subtotal(self):
        """Calculate subtotal from document items (before tax)"""
        from .document_item import DocumentItem
        items = DocumentItem.query.filter_by(document_id=self.id).all()
        total = 0
        for item in items:
            item_total = (item.quantity or 0) * (item.unit_price or 0)
            item_total -= item_total * ((item.discount or 0) / 100)
            total += item_total
        return round(total, 2)
    
    @property
    def tax_amount(self):
        """Calculate tax amount based on subtotal and company tax rate"""
        from .company import Company
        company = Company.query.get(self.company_id)
        if company and company.tax_rate:
            return round(self.subtotal * (company.tax_rate / 100), 2)
        return 0.0

    def calculate_paid_amount(self):
        """Calculate total amount paid via payments"""
        paid = sum((p.amount or 0) for p in self.payments)
        return round(paid, 2)

    def calculate_balance_due(self):
        """Calculate remaining balance to be paid"""
        paid = self.calculate_paid_amount()
        return round((self.total_amount or 0) - paid, 2)

    def get_balance(self):
        paid = sum((p.amount or 0) for p in self.payments)
        return (self.total_amount or 0) - paid
