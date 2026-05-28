from .base import db, BaseModel

class DocumentItem(BaseModel):
    __tablename__ = 'document_items'
    
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), index=True)
    
    description = db.Column(db.String(1024), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=0.0, nullable=False)
    
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name='check_quantity_positive'),
        db.CheckConstraint("unit_price >= 0", name='check_unit_price_non_negative'),
        db.CheckConstraint("discount >= 0 AND discount <= 100", name='check_item_discount_range'),
    )

    def __repr__(self) -> str:
        return f'<DocumentItem {self.id} qty={self.quantity} @{self.unit_price}'
