from flask import Flask, session
from flask_login import current_user
from app.extensions import db

def register_request_hooks(app: Flask):
    @app.before_request
    def ensure_company_selected():
        if not current_user.is_authenticated:
            return

        user_companies = current_user.companies
        if not user_companies:
            return

        # Build a fast lookup: id -> company object
        company_by_id = {c.id: c for c in user_companies}

        stored_id = session.get('selected_company_id')

        # Validate the stored company is still accessible; clear if stale.
        if stored_id and stored_id not in company_by_id:
            session.pop('selected_company_id', None)
            session.pop('selected_company_slug', None)
            session.pop('currency', None)
            session.pop('tax_rate', None)
            stored_id = None

        # Auto-select the first accessible company (alphabetically) if none stored.
        if not stored_id:
            first_company = sorted(user_companies, key=lambda c: (c.name or '').lower())[0]
            stored_id = first_company.id
            session['selected_company_id'] = stored_id

        # Always keep slug, currency, and tax_rate in sync with the selected company.
        company = company_by_id.get(stored_id)
        if company:
            session['selected_company_slug'] = company.slug
            session['currency'] = company.currency
            session['tax_rate'] = float(company.tax_rate) if company.tax_rate else 0.0
