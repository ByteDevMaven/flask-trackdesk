from .base import db, BaseModel

class PurchaseOrder(BaseModel):
    __tablename__ = 'purchase_orders'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    order_number = db.Column(db.String(50), nullable=False, index=True)
    order_document = db.Column(db.String(50), default='document-000000', nullable=False)
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    buy_date = db.Column(db.Date, index=True)

    supplier = db.relationship('Contact', backref='purchase_orders', lazy='select')
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan', lazy='select')
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'order_number', name='uq_purchase_order_per_company'),
        db.CheckConstraint("total_amount >= 0", name='check_po_total_amount_non_negative'),
    )

    def __repr__(self) -> str:
        return f'<PurchaseOrder {self.id} {self.order_number}>'
