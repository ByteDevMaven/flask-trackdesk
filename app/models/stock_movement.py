from .base import db, BaseModel
from .enums import StockMovementType
from datetime import datetime, UTC

class StockMovement(BaseModel):
    __tablename__ = 'stock_movements'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True, index=True)
    destination_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True, index=True)
    
    type = db.Column(db.Enum(StockMovementType), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(100), index=True)
    notes = db.Column(db.String(1024))
    date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), index=True)

    inventory_item = db.relationship('InventoryItem', backref='movements', lazy='select')
    company = db.relationship('Company', backref='stock_movements', lazy='select')
    user = db.relationship('User', backref='stock_movements', lazy='select')
    warehouse = db.relationship('Warehouse', foreign_keys=[warehouse_id], backref='stock_movements', lazy='select')
    destination_warehouse = db.relationship('Warehouse', foreign_keys=[destination_warehouse_id], backref='incoming_transfers', lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name='check_movement_quantity_positive'),
    )

    @property
    def qty_change(self) -> int:
        """Return signed quantity: negative for outgoing, positive for incoming/adjustment."""
        if self.type == StockMovementType.outgoing:
            return -abs(self.quantity)
        return abs(self.quantity)

    def __repr__(self) -> str:
        return f'<StockMovement {self.id} {self.type.value} qty={self.quantity}>'

