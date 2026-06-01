import math
from datetime import datetime, UTC
from flask import abort
from sqlalchemy import exc

from app.models import db, Contact, Document, InventoryItem
from app.models.enums import ContactType

class ContactService:
    @staticmethod
    def get_paginated_contacts(company_id, page, per_page, search_term, contact_type_filter):
        query = Contact.query.filter_by(company_id=company_id)

        valid_types = [e.name for e in ContactType]
        if contact_type_filter in valid_types:
            query = query.filter_by(type=ContactType[contact_type_filter])

        if search_term:
            term = f"%{search_term}%"
            query = query.filter(
                (Contact.name.ilike(term)) |
                (Contact.legal_name.ilike(term)) |
                (Contact.email.ilike(term)) |
                (Contact.identifier.ilike(term)) |
                (Contact.phone.ilike(term))
            )
        
        total_contacts = query.count()
        total_pages = math.ceil(total_contacts / per_page) if per_page else 1
        
        paginated = query.order_by(Contact.name).paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated, total_pages

    @staticmethod
    def create_contact(company_id, data):
        if not data.get('name'):
            raise ValueError("Contact name is required")

        contact_type_str = data.get('type', 'customer')
        valid_types = [e.name for e in ContactType]
        contact_type = ContactType[contact_type_str] if contact_type_str in valid_types else ContactType.customer

        contact = Contact(
            company_id=company_id,
            name=data.get('name'),
            legal_name=data.get('legal_name', ''),
            type=contact_type,
            identifier=data.get('identifier', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            payment_terms_days=int(data.get('payment_terms_days', 0) or 0),
            credit_limit=float(data.get('credit_limit', 0) or 0),
            notes=data.get('notes', '')
        )
        
        try:
            db.session.add(contact)
            db.session.commit()
            return contact
        except exc.IntegrityError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_contact_with_stats(company_id, contact_id, page, per_page):
        contact = Contact.query.filter_by(id=contact_id, company_id=company_id).first()
        if not contact:
            abort(404)
        
        stats = {}
        items = None

        if contact.type.name in ['customer', 'customer_supplier', 'lead']:
            items = Document.query.filter_by(client_id=contact.id).order_by(Document.issued_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
            all_docs = Document.query.filter_by(client_id=contact.id).all()
            
            total_revenue = sum(doc.calculate_paid_amount() for doc in all_docs)
            pending_payments = sum(doc.calculate_balance_due() for doc in all_docs)
            total_invoices = len(all_docs)
            
            stats = {
                'total_revenue': total_revenue,
                'pending_payments': pending_payments,
                'total_invoices': total_invoices
            }
        elif contact.type.name == 'supplier':
            items = InventoryItem.query.filter_by(supplier_id=contact.id).order_by(InventoryItem.name).paginate(page=page, per_page=per_page, error_out=False)
            all_items = InventoryItem.query.filter_by(supplier_id=contact.id).all()
            
            total_inventory_value = sum((item.price or 0) * (item.quantity or 0) for item in all_items)
            total_products = len(all_items)
            low_stock_products = sum(1 for item in all_items if (item.quantity or 0) <= 5)
            
            stats = {
                'total_value': total_inventory_value,
                'total_products': total_products,
                'low_stock': low_stock_products
            }
            
        return contact, items, stats

    @staticmethod
    def update_contact(company_id, contact_id, data):
        contact = Contact.query.filter_by(id=contact_id, company_id=company_id).first()
        if not contact:
            abort(404)

        if not data.get('name'):
            raise ValueError("Contact name is required")

        contact_type_str = data.get('type')
        valid_types = [e.name for e in ContactType]
        if contact_type_str in valid_types:
            contact.type = ContactType[contact_type_str]
            
        contact.name = data.get('name')
        contact.legal_name = data.get('legal_name', '')
        contact.identifier = data.get('identifier', '')
        contact.email = data.get('email', '')
        contact.phone = data.get('phone', '')
        contact.address = data.get('address', '')
        contact.payment_terms_days = int(data.get('payment_terms_days', 0) or 0)
        contact.credit_limit = float(data.get('credit_limit', 0) or 0)
        contact.notes = data.get('notes', '')
        
        try:
            db.session.commit()
            return contact
        except exc.IntegrityError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_contact(company_id, contact_id):
        contact = Contact.query.filter_by(id=contact_id, company_id=company_id).first()
        if not contact:
            abort(404)
            
        try:
            contact.is_deleted = True
            contact.deleted_at = datetime.now(UTC)
            db.session.commit()
            return True
        except exc.IntegrityError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def search_contacts(company_id, search_term, contact_type, limit=10):
        query = Contact.query.filter_by(company_id=company_id)
        valid_types = [e.name for e in ContactType]
        if contact_type in valid_types:
            query = query.filter_by(type=ContactType[contact_type])
            
        if search_term:
            term = f"%{search_term}%"
            query = query.filter(
                (Contact.name.ilike(term)) |
                (Contact.legal_name.ilike(term)) |
                (Contact.identifier.ilike(term))
            )
            
        contacts = query.order_by(Contact.name).limit(limit).all()
        return contacts
