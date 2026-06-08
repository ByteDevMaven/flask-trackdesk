import re
from .base import db, BaseModel

class Company(BaseModel):
    __tablename__ = 'companies'
    
    name = db.Column(db.String(255), nullable=False, index=True)
    slug = db.Column(db.String(64), unique=True, nullable=True, index=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(20), index=True)
    address = db.Column(db.String(512))
    #TODO: Timezone
    
    currency = db.Column(db.String(3), default='USD', nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0.0, nullable=False)
    
    __table_args__ = (
        db.CheckConstraint("tax_rate >= 0 AND tax_rate <= 100", name='check_tax_rate_range'),
        db.CheckConstraint("length(currency) = 3", name='check_currency_code_length'),
    )

    @staticmethod
    def build_slug(name: str) -> str:
        """Auto-generate a URL-safe slug from the company name."""
        import random
        import string
        
        # Suffixes to strip
        suffixes = [
            'llc', 'sa de cv', 's a de c v', 's.a.', 'inc', 'ltd', 'de c.v.', 'corp',
            's.r.l.', 's. de r.l.', 'srl'
        ]
        
        # Lowercase and replace non-alphanumeric with spaces temporarily to easily remove suffixes
        clean_name = name.lower()
        clean_name = re.sub(r'[^a-z0-9]', ' ', clean_name)
        
        # Remove suffixes
        words = clean_name.split()
        filtered_words = []
        for word in words:
            if word not in suffixes:
                filtered_words.append(word)
                
        # Join and re-apply regex to ensure strict alphanumeric (no spaces)
        slug = "".join(filtered_words)
        slug = re.sub(r'[^a-z0-9]', '', slug)
        
        # Trim to 30 chars
        slug = slug[:30]
        
        if not slug:
            # Fallback if name was completely stripped
            slug = "company"
            
        return slug

    def __repr__(self) -> str:
        return f'<Company {self.id} {self.name}>'
