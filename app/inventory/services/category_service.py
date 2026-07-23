from sqlalchemy.exc import IntegrityError
from app.models import db, Category

class CategoryService:
    @staticmethod
    def get_categories(company_id):
        return Category.query.filter_by(company_id=company_id).order_by(Category.name).all()

    @staticmethod
    def get_category(company_id, category_id):
        return Category.query.filter_by(id=category_id, company_id=company_id).first()

    @staticmethod
    def create_category(company_id, name, description=None):
        name = name.strip()
        if not name:
            raise ValueError("Name is required")
        
        existing = Category.query.filter_by(company_id=company_id, name=name).first()
        if existing:
            raise ValueError("A category with this name already exists")

        category = Category(
            company_id=company_id,
            name=name,
            description=description.strip() if description else None
        )
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def update_category(company_id, category_id, name, description=None):
        category = Category.query.filter_by(id=category_id, company_id=company_id).first_or_404()
        
        name = name.strip()
        if not name:
            raise ValueError("Name is required")
            
        existing = Category.query.filter_by(company_id=company_id, name=name).first()
        if existing and existing.id != category.id:
            raise ValueError("A category with this name already exists")
            
        category.name = name
        category.description = description.strip() if description else None
        
        db.session.commit()
        return category

    @staticmethod
    def delete_category(company_id, category_id):
        category = Category.query.filter_by(id=category_id, company_id=company_id).first_or_404()
        
        try:
            db.session.delete(category)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Cannot delete this category because it is being used by one or more inventory items.")
