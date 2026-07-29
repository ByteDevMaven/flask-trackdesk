from .base import db, BaseModel
from .enums import DocumentType, DocumentStatus
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal('0.01')

def _money(value):
    return Decimal(str(value or 0)).quantize(_CENT, rounding=ROUND_HALF_UP)

def calculate_document_totals(items, general_discount=0, tax_rate=0):
    """Calculate invoice totals consistently using decimal, cent-rounded arithmetic."""
    gross = Decimal('0')
    item_discount = Decimal('0')
    for item in items or []:
        get = item.get if isinstance(item, dict) else lambda key, default=0: getattr(item, key, default)
        quantity = _money(get('quantity', 0))
        unit_price = _money(get('unit_price', 0))
        discount_rate = _money(get('discount', 0))
        line_gross = quantity * unit_price
        gross += line_gross
        item_discount += line_gross * discount_rate / Decimal('100')
    gross = _money(gross)
    item_discount = _money(item_discount)
    available = max(Decimal('0'), gross - item_discount)
    additional_discount = min(max(Decimal('0'), _money(general_discount)), available)
    subtotal = _money(available - additional_discount)
    tax = _money(subtotal * _money(tax_rate) / Decimal('100'))
    return {'gross_subtotal': gross, 'item_discount': item_discount, 'discount_amount': additional_discount, 'subtotal': subtotal, 'tax': tax, 'total': _money(subtotal + tax)}


class Document(BaseModel):
    __tablename__ = 'documents'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    document_number = db.Column(db.String(50), nullable=False, index=True)
    type = db.Column(db.Enum(DocumentType), nullable=False)
    
    client_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, index=True)
    
    status = db.Column(db.Enum(DocumentStatus), nullable=False, default=DocumentStatus.draft)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    
    issued_date = db.Column(db.DateTime, index=True)
    due_date = db.Column(db.DateTime, index=True)
    
    # Cache subtotal to avoid N+1 queries
    subtotal_cache = db.Column(db.Numeric(12, 2), nullable=True)
    discount_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    tax_cache = db.Column(db.Numeric(12, 2), nullable=True)

    client = db.relationship('Contact', backref='documents', lazy='select')
    company = db.relationship('Company', backref='documents', lazy='select')
    warehouse = db.relationship('Warehouse', backref='documents', lazy='select')
    project = db.relationship('Project', backref='documents', lazy='select')
    payments = db.relationship('Payment', backref='document', cascade='all, delete-orphan', lazy='dynamic')
    items = db.relationship('DocumentItem', backref='document', cascade='all, delete-orphan', lazy='select')
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'document_number', name='uq_document_per_company'),
        db.CheckConstraint("total_amount >= 0", name='check_total_amount_non_negative'),
    )

    @property
    def subtotal(self) -> float:
        """Return the net subtotal before tax using the current line items."""
        company = self.company
        totals = calculate_document_totals(self.items or [], self.discount_amount or 0, company.tax_rate if company else 0)
        return float(totals['subtotal'])
    
    @property
    def tax_amount(self) -> float:
        """Return tax calculated from the current subtotal and company rate."""
        company = self.company
        totals = calculate_document_totals(self.items or [], self.discount_amount or 0, company.tax_rate if company else 0)
        return float(totals['tax'])
    def calculate_paid_amount(self) -> float:
        """Calculate total amount paid via payments"""
        paid = sum(float(p.amount or 0) for p in self.payments)
        return round(float(paid), 2)

    def calculate_balance_due(self) -> float:
        """Calculate remaining balance to be paid"""
        paid = self.calculate_paid_amount()
        return round(float(self.total_amount or 0) - paid, 2)

    @property
    def item_discount_amount(self) -> float:
        """Return the total of percentage discounts applied to individual lines."""
        totals = calculate_document_totals(self.items or [], 0, 0)
        return float(totals['item_discount'])

    def refresh_cache(self):
        """Refresh all persisted total caches from current items."""
        company = self.company
        totals = calculate_document_totals(self.items or [], self.discount_amount or 0, company.tax_rate if company else 0)
        self.subtotal_cache = totals['subtotal']
        self.tax_cache = totals['tax']
        self.total_amount = totals['total']
    def __repr__(self) -> str:
        return f'<Document {self.id} {self.document_number} ({self.type.value}, {self.status.value})'
