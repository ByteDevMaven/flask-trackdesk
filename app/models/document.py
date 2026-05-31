from .base import db, BaseModel
from .enums import DocumentType, DocumentStatus
from functools import cached_property

class Document(BaseModel):
    __tablename__ = 'documents'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    document_number = db.Column(db.String(50), nullable=False, index=True)
    type = db.Column(db.Enum(DocumentType), nullable=False)
    
    client_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True, index=True)
    
    status = db.Column(db.Enum(DocumentStatus), nullable=False, default=DocumentStatus.draft)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    
    issued_date = db.Column(db.DateTime, index=True)
    due_date = db.Column(db.DateTime, index=True)
    
    # Cache subtotal to avoid N+1 queries
    subtotal_cache = db.Column(db.Numeric(12, 2), nullable=True)
    tax_cache = db.Column(db.Numeric(12, 2), nullable=True)

    client = db.relationship('Contact', backref='documents', lazy='select')
    warehouse = db.relationship('Warehouse', backref='documents', lazy='select')
    payments = db.relationship('Payment', backref='document', cascade='all, delete-orphan', lazy='dynamic')
    items = db.relationship('DocumentItem', backref='document', cascade='all, delete-orphan', lazy='select')
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'document_number', name='uq_document_per_company'),
        db.CheckConstraint("total_amount >= 0", name='check_total_amount_non_negative'),
    )

    @cached_property
    def subtotal(self) -> float:
        """Calculate subtotal from document items (before tax). Cached."""
        if self.subtotal_cache is not None:
            return float(self.subtotal_cache)
        
        from .document_item import DocumentItem
        items = self.items or []
        total = 0
        for item in items:
            item_total = float(item.quantity or 0) * float(item.unit_price or 0)
            item_total -= item_total * (float(item.discount or 0) / 100.0)
            total += item_total
        return round(total, 2)
    
    @cached_property
    def tax_amount(self) -> float:
        """Calculate tax amount based on subtotal and company tax rate. Cached."""
        if self.tax_cache is not None:
            return float(self.tax_cache)
        
        from .company import Company
        company = Company.query.get(self.company_id)
        if company and company.tax_rate:
            return round(self.subtotal * (float(company.tax_rate) / 100.0), 2)
        return 0.0

    def calculate_paid_amount(self) -> float:
        """Calculate total amount paid via payments"""
        paid = sum(float(p.amount or 0) for p in self.payments)
        return round(float(paid), 2)

    def calculate_balance_due(self) -> float:
        """Calculate remaining balance to be paid"""
        paid = self.calculate_paid_amount()
        return round(float(self.total_amount or 0) - paid, 2)

    def refresh_cache(self):
        """Refresh subtotal and tax caches"""
        subtotal = 0
        for item in self.items:
            item_total = float(item.quantity or 0) * float(item.unit_price or 0)
            item_total -= item_total * (float(item.discount or 0) / 100.0)
            subtotal += item_total
        self.subtotal_cache = round(subtotal, 2)
        
        from .company import Company
        company = Company.query.get(self.company_id)
        if company and company.tax_rate:
            self.tax_cache = round(float(self.subtotal_cache) * (float(company.tax_rate) / 100.0), 2)
        else:
            self.tax_cache = 0.0

    def __repr__(self) -> str:
        return f'<Document {self.id} {self.document_number} ({self.type.value}, {self.status.value})'
