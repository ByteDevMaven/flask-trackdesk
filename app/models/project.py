from .base import db, BaseModel

class Project(BaseModel):
    __tablename__ = 'projects'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String, default='active')
    
    company = db.relationship('Company', backref=db.backref('projects', lazy='dynamic'))

    def __repr__(self):
        return f'<Project {self.name}>'
