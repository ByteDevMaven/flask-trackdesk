from .base import db, BaseModel

class PurchaseOrderItem(BaseModel):
    __tablename__ = 'purchase_order_items'
    
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False, index=True)

    item_code = db.Column(db.String(100), nullable=False, default='', index=True)
    name = db.Column(db.String(255), nullable=False, default='')
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)

    inventory_item = db.relationship('InventoryItem', backref='purchase_order_items', lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name='check_poi_quantity_positive'),
        db.CheckConstraint("price >= 0", name='check_poi_price_non_negative'),
        db.CheckConstraint("total >= 0", name='check_poi_total_non_negative'),
    )

    def __repr__(self) -> str:
        return f'<PurchaseOrderItem {self.id} {self.name} qty={self.quantity}>'
