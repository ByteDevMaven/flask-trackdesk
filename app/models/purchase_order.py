from .base import db, BaseModel

class PurchaseOrder(BaseModel):
    __tablename__ = 'purchase_orders'
    order_number = db.Column(db.String, nullable=False, unique=True, index=True)
    order_document = db.Column(db.String, default='document-000000', nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)

    total_amount = db.Column(db.Float, nullable=False)
    buy_date = db.Column(db.Date, index=True)

    supplier = db.relationship('Supplier', backref='purchase_orders')
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan')
