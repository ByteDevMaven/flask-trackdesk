from .base import db, BaseModel

class DocumentItem(BaseModel):
    __tablename__ = 'document_items'
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), index=True)
    description = db.Column(db.String)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    discount = db.Column(db.Float, default=0.0)
