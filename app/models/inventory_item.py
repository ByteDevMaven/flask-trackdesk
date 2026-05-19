from .base import db, BaseModel

class InventoryItem(BaseModel):
    __tablename__ = 'inventory_items'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False, index=True)
    description = db.Column(db.String)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    discount = db.Column(db.Float, default=0.0)
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), index=True)

    supplier = db.relationship('Contact', backref='inventory_items')
