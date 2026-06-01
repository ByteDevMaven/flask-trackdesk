import enum
from .base import db, BaseModel

class DocumentTemplateType(enum.Enum):
    pdf_overlay = 'pdf_overlay'
    html = 'html'

class DocumentTemplate(BaseModel):
    __tablename__ = 'document_templates'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(DocumentTemplateType), nullable=False, default=DocumentTemplateType.pdf_overlay)
    
    # For pdf_overlay type
    pdf_background_path = db.Column(db.String(255), nullable=True) 
    pdf_coordinates = db.Column(db.JSON, nullable=True)
    
    # For html type
    html_template_path = db.Column(db.String(255), nullable=True)
    
    is_default = db.Column(db.Boolean, default=False)

    company = db.relationship('Company', backref='document_templates', lazy='select')

    def __repr__(self) -> str:
        return f'<DocumentTemplate {self.id} {self.name} ({self.type.value})>'
