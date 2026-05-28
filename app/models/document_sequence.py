from .base import db, BaseModel

class DocumentSequence(BaseModel):
    __tablename__ = 'document_sequences'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)

    cai = db.Column(db.String(50), nullable=False, index=True)
    range_start = db.Column(db.Integer, nullable=False)
    range_end = db.Column(db.Integer, nullable=False)
    current = db.Column(db.Integer, nullable=False)
    expiration_date = db.Column(db.Date, nullable=False, index=True)

    company = db.relationship('Company', backref='document_sequences', lazy='select')
    
    __table_args__ = (
        db.CheckConstraint("range_start > 0 AND range_end > 0 AND current >= range_start", name='check_doc_sequence_range'),
    )
    
    def __repr__(self) -> str:
        return f'<DocumentSequence {self.id} {self.cai} ({self.current}/{self.range_end})>'
