from .base import db, BaseModel

class WarehouseItem(BaseModel):
    __tablename__ = 'warehouse_items'
    
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    
    warehouse = db.relationship('Warehouse', backref=db.backref('items', cascade='all, delete-orphan', lazy='dynamic'))
    inventory_item = db.relationship('InventoryItem', backref=db.backref('warehouse_items', cascade='all, delete-orphan', lazy='dynamic'))
    
    __table_args__ = (
        db.UniqueConstraint('warehouse_id', 'inventory_item_id', name='uq_warehouse_inventory_item'),
        db.CheckConstraint("quantity >= 0", name='check_warehouse_quantity_non_negative'),
    )

    def __repr__(self) -> str:
        return f'<WarehouseItem WH:{self.warehouse_id} Item:{self.inventory_item_id} Qty:{self.quantity}>'
