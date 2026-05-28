from .base import db, BaseModel

class Project(BaseModel):
    __tablename__ = 'projects'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.String(1024))
    budget = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    status = db.Column(db.String(50), default='active', index=True)
    
    company = db.relationship('Company', backref=db.backref('projects', lazy='select'))
    
    __table_args__ = (
        db.CheckConstraint("budget >= 0", name='check_project_budget_non_negative'),
    )

    def __repr__(self) -> str:
        return f'<Project {self.id} {self.name} ({self.status})>'
