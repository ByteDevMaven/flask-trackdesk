from .base import db, BaseModel

class Category(BaseModel):
    __tablename__ = 'categories'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1024))
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='uq_company_category_name'),
    )
    
    def __repr__(self) -> str:
        return f'<Category {self.id} {self.name}>'
