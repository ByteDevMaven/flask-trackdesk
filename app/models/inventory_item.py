from .base import db, BaseModel

class InventoryItem(BaseModel):
    __tablename__ = 'inventory_items'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.String(1024))
    
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    cost_price = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=0.0, nullable=False)
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)
    supplier = db.relationship('Contact', backref='inventory_items', lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("quantity >= 0", name='check_quantity_non_negative'),
        db.CheckConstraint("price >= 0", name='check_price_non_negative'),
        db.CheckConstraint("cost_price >= 0", name='check_cost_price_non_negative'),
        db.CheckConstraint("discount >= 0 AND discount <= 100", name='check_discount_range'),
    )

    def __repr__(self) -> str:
        return f'<InventoryItem {self.id} {self.name} (qty={self.quantity})'
