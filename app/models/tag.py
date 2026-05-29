from .base import db, BaseModel

class Tag(BaseModel):
    __tablename__ = 'tags'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    color_code = db.Column(db.String(50), default='bg-slate-100 text-slate-700')
    
    company = db.relationship('Company', backref=db.backref('tags', lazy='select'), lazy='select')

    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='uq_company_tag_name'),
    )

    def __repr__(self) -> str:
        return f'<Tag {self.id} {self.name}>'
