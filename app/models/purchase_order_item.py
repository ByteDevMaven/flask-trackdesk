from .base import db, BaseModel

class PurchaseOrderItem(BaseModel):
    __tablename__ = 'purchase_order_items'
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False, index=True)

    item_code = db.Column(db.String, nullable=False, default='', index=True)
    name = db.Column(db.String, nullable=False, default='')
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.00)
    total = db.Column(db.Float, nullable=False, default=0.00)

    inventory_item = db.relationship('InventoryItem', backref='purchase_order_items')
