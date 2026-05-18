from .base import db, BaseModel

class DocumentSequence(BaseModel):
    __tablename__ = 'document_sequences'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)

    cai = db.Column(db.String, nullable=False)
    range_start = db.Column(db.Integer, nullable=False)
    range_end = db.Column(db.Integer, nullable=False)
    current = db.Column(db.Integer, nullable=False) # Should be initialized to range_start - 1
    expiration_date = db.Column(db.Date, nullable=False)

    company = db.relationship('Company', backref='document_sequences')
