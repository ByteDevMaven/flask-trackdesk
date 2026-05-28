from .base import db, BaseModel

class Report(BaseModel):
    __tablename__ = 'reports'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    report_type = db.Column(db.String(100), index=True)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    file_url = db.Column(db.String(512))
    
    def __repr__(self) -> str:
        return f'<Report {self.id} {self.title}({self.report_type})>'
