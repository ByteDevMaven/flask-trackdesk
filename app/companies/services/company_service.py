import os
import uuid
from datetime import datetime, UTC
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

from flask import abort
from flask import current_app

from app.models import db, Company, User, Contact, InventoryItem, Document, Payment, Report, DocumentSequence, Account
from app.models.enums import ContactType, AccountType


COMMON_TIMEZONES = [
    'America/Tegucigalpa',
    'America/Guatemala',
    'America/El_Salvador',
    'America/Managua',
    'America/Costa_Rica',
    'America/Panama',
    'America/Mexico_City',
    'America/Bogota',
    'America/New_York',
    'UTC',
]


class CompanyService:
    TIMEZONE_CHOICES = COMMON_TIMEZONES + [
        timezone_name
        for timezone_name in sorted(available_timezones())
        if timezone_name not in COMMON_TIMEZONES
    ]

    @staticmethod
    def _normalize_timezone(timezone_name):
        timezone_name = (timezone_name or 'UTC').strip()
        try:
            ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Zona horaria inválida.") from exc
        return timezone_name

    @staticmethod
    def _save_logo(file):
        if not file or not file.filename:
            return None

        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext != 'webp':
            raise ValueError("El logo debe ser una imagen en formato WebP.")

        upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', ''), 'company_logos')
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.webp"
        file.save(os.path.join(upload_dir, filename))
        return f"uploads/company_logos/{filename}"

    @staticmethod
    def get_company_for_user(company_id, current_user):
        company = Company.query.get_or_404(company_id)
        if not current_user.is_admin and company not in current_user.companies:
            abort(403)
        return company

    @staticmethod
    def get_company_by_slug(slug, current_user):
        """Find a company by its URL slug and check access permissions."""
        company = Company.query.filter_by(slug=slug).first_or_404()
        if not current_user.is_admin and company not in current_user.companies:
            abort(403)
        return company

    @staticmethod
    def get_paginated_companies(page, per_page, search, current_user):
        query = Company.query
        if not current_user.is_admin:
            query = query.filter(Company.users.any(id=current_user.id))
        
        if search:
            query = query.filter(Company.name.ilike(f'%{search}%'))
        
        return query.order_by(Company.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def create_company(data, current_user, files=None):
        name = data.get('name', '').strip()
        if not name:
            raise ValueError("El nombre de la empresa es obligatorio.")
            
        existing_company = Company.query.filter_by(name=name).first()
        if existing_company:
            raise ValueError("Ya existe una empresa con este nombre.")

        company = Company(
            name=name,
            currency=data.get('currency', 'USD'),
            tax_rate=float(data.get('tax_rate', 0.0)),
            address=data.get('address', '').strip(),
            phone=data.get('phone', '').strip(),
            email=data.get('email', '').strip(),
            identifier=data.get('identifier', '').strip(),
            timezone=CompanyService._normalize_timezone(data.get('timezone')),
            logo_url=CompanyService._save_logo(files.get('logo')) if files else None,
            created_at=datetime.now(UTC)
        )
        
        # Handle slug
        input_slug = data.get('slug', '').strip()
        if input_slug:
            candidate_slug = input_slug.lower()
            if Company.query.filter_by(slug=candidate_slug).first():
                raise ValueError("This URL alias (slug) is already in use by another company.")
            company.slug = candidate_slug
        else:
            # Auto-generate
            base_slug = Company.build_slug(name)
            candidate = base_slug
            counter = 1
            while Company.query.filter_by(slug=candidate).first():
                candidate = f"{base_slug}{counter}"
                counter += 1
            company.slug = candidate

        user_ids = data.getlist('user_ids')
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
            company.users.extend(users)
            
        if not current_user.is_admin and current_user not in company.users:
            company.users.append(current_user)

        db.session.add(company)
        db.session.flush() # Flush to get company.id

        default_accounts = [
            Account(company_id=company.id, name='Cash/Bank', type=AccountType.asset, is_default=True),
            Account(company_id=company.id, name='Accounts Receivable', type=AccountType.asset, is_default=True),
            Account(company_id=company.id, name='Inventory', type=AccountType.asset, is_default=True),
            Account(company_id=company.id, name='Accounts Payable', type=AccountType.liability, is_default=True),
            Account(company_id=company.id, name='Sales Revenue', type=AccountType.revenue, is_default=True),
            Account(company_id=company.id, name='Cost of Goods Sold (COGS)', type=AccountType.expense, is_default=True),
            Account(company_id=company.id, name='General Expenses', type=AccountType.expense, is_default=True)
        ]
        db.session.add_all(default_accounts)
        db.session.commit()
        return company

    @staticmethod
    def get_company_with_stats(company_id, current_user):
        company = CompanyService.get_company_for_user(company_id, current_user)

        stats = {
            'users_count': len(company.users),
            'clients_count': Contact.query.filter_by(company_id=company.id, type=ContactType.customer).count(),
            'suppliers_count': Contact.query.filter_by(company_id=company.id, type=ContactType.supplier).count(),
            'inventory_count': InventoryItem.query.filter_by(company_id=company.id).count(),
            'documents_count': Document.query.filter_by(company_id=company.id).count(),
            'payments_count': Payment.query.filter_by(company_id=company.id).count(),
            'reports_count': Report.query.filter_by(company_id=company.id).count()
        }
        
        recent_documents = Document.query.filter_by(company_id=company.id).order_by(Document.issued_date.desc()).limit(5).all()
        recent_payments = Payment.query.filter_by(company_id=company.id).order_by(Payment.payment_date.desc()).limit(5).all()

        return company, stats, recent_documents, recent_payments

    @staticmethod
    def update_company(company_id, data, current_user, files=None):
        company = CompanyService.get_company_for_user(company_id, current_user)
        
        name = data.get('name', '').strip()
        if not name:
            raise ValueError("El nombre de la empresa es obligatorio.")
            
        existing_company = Company.query.filter(Company.name == name, Company.id != company_id).first()
        if existing_company:
            raise ValueError("Ya existe una empresa con este nombre.")

        company.name = name
        company.currency = data.get('currency', 'USD')
        company.tax_rate = float(data.get('tax_rate', 0.0))
        company.address = data.get('address', '').strip()
        company.phone = data.get('phone', '').strip()
        company.email = data.get('email', '').strip()
        company.identifier = data.get('identifier', '').strip()
        company.timezone = CompanyService._normalize_timezone(data.get('timezone'))
        company.updated_at = datetime.now(UTC)

        uploaded_logo = CompanyService._save_logo(files.get('logo')) if files else None
        if uploaded_logo:
            company.logo_url = uploaded_logo
        
        # Handle slug update
        input_slug = data.get('slug', '').strip()
        if input_slug:
            candidate_slug = input_slug.lower()
            if Company.query.filter(Company.slug == candidate_slug, Company.id != company_id).first():
                raise ValueError("This URL alias (slug) is already in use by another company.")
            company.slug = candidate_slug
        elif not company.slug:
            # Generate one if it somehow doesn't have one
            base_slug = Company.build_slug(name)
            candidate = base_slug
            counter = 1
            while Company.query.filter(Company.slug == candidate, Company.id != company_id).first():
                candidate = f"{base_slug}{counter}"
                counter += 1
            company.slug = candidate

        company.users.clear()
        user_ids = data.getlist('user_ids')
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
            company.users.extend(users)
        
        db.session.commit()
        return company

    @staticmethod
    def delete_company(company_id, current_user):
        company = CompanyService.get_company_for_user(company_id, current_user)
        
        has_clients = Contact.query.filter_by(company_id=company.id).first() is not None
        has_suppliers = Contact.query.filter_by(company_id=company.id).first() is not None
        has_inventory = InventoryItem.query.filter_by(company_id=company.id).first() is not None
        has_documents = Document.query.filter_by(company_id=company.id).first() is not None
        has_payments = Payment.query.filter_by(company_id=company.id).first() is not None
        has_reports = Report.query.filter_by(company_id=company.id).first() is not None
        
        if any([has_clients, has_suppliers, has_inventory, has_documents, has_payments, has_reports]):
            raise ValueError("Cannot delete company with existing data. Please remove all related clients, suppliers, inventory, documents, payments, and reports first.")
        
        company.users.clear()
        company.is_deleted = True
        company.deleted_at = datetime.now(UTC)
        db.session.commit()
        return True

    @staticmethod
    def search_companies(query, current_user, limit=10):
        if not query:
            return []
            
        query_db = Company.query
        if not current_user.is_admin:
            query_db = query_db.filter(Company.users.any(id=current_user.id))
            
        companies = query_db.filter(Company.name.ilike(f'%{query}%')).limit(limit).all()
        return companies

    @staticmethod
    def get_sequences(company_id):
        return DocumentSequence.query.filter_by(company_id=company_id).order_by(DocumentSequence.expiration_date.desc()).all()

    @staticmethod
    def get_sequence(company_id, seq_id):
        return DocumentSequence.query.filter_by(id=seq_id, company_id=company_id).first_or_404()

    @staticmethod
    def create_sequence(company_id, data):
        cai = data.get('cai', '').strip()
        range_start = int(data.get('range_start', 0))
        range_end = int(data.get('range_end', 0))
        expiration_date_str = data.get('expiration_date', '')
        
        if not all([cai, range_start, range_end, expiration_date_str]):
            raise ValueError("All fields are required.")
            
        expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
        
        sequence = DocumentSequence(
            company_id=company_id,
            cai=cai,
            range_start=range_start,
            range_end=range_end,
            current=range_start - 1,
            expiration_date=expiration_date
        )
        
        db.session.add(sequence)
        db.session.commit()
        return sequence

    @staticmethod
    def update_sequence(company_id, seq_id, data):
        sequence = CompanyService.get_sequence(company_id, seq_id)
        
        cai = data.get('cai', '').strip()
        range_start = int(data.get('range_start', 0))
        range_end = int(data.get('range_end', 0))
        current = int(data.get('current', sequence.current))
        expiration_date_str = data.get('expiration_date', '')
        
        if not all([cai, expiration_date_str]):
            raise ValueError("CAI and Expiration Date are required.")
            
        sequence.cai = cai
        sequence.range_start = range_start
        sequence.range_end = range_end
        sequence.current = current
        sequence.expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
        
        db.session.commit()
        return sequence

    @staticmethod
    def delete_sequence(company_id, seq_id):
        sequence = CompanyService.get_sequence(company_id, seq_id)
        sequence.is_deleted = True
        sequence.deleted_at = datetime.now(UTC)
        db.session.commit()
        return True
