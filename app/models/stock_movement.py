from .base import db, BaseModel
from .enums import StockMovementType
from datetime import datetime, UTC

class StockMovement(BaseModel):
    __tablename__ = 'stock_movements'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    
    type = db.Column(db.Enum(StockMovementType), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String, index=True) # Invoice #, PO #, or adjustment reason
    notes = db.Column(db.Text)
    
    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), index=True)

    inventory_item = db.relationship('InventoryItem', backref='movements')
    company = db.relationship('Company', backref='stock_movements')
    user = db.relationship('User', backref='stock_movements')

    @property
    def qty_change(self):
        if self.type == StockMovementType.outgoing:
            return -self.quantity
        return self.quantity

