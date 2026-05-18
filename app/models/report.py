from .base import db, BaseModel

class Report(BaseModel):
    __tablename__ = 'reports'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String, nullable=False, index=True)
    report_type = db.Column(db.String, index=True)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    file_url = db.Column(db.String)
