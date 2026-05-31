from .base import db, BaseModel

class Warehouse(BaseModel):
    __tablename__ = 'warehouses'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    company = db.relationship('Company', backref='warehouses', lazy='select')
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='uq_warehouse_name_per_company'),
    )

    def __repr__(self) -> str:
        return f'<Warehouse {self.id} {self.name}>'
