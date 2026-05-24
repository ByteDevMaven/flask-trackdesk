from flask import Flask, session
from flask_login import current_user
from app.extensions import db

def register_request_hooks(app: Flask):
    @app.before_request
    def ensure_company_selected():
        from app.models import user_companies
        if current_user.is_authenticated and 'selected_company_id' not in session:
            user_company = db.session.query(user_companies).filter_by(user_id=current_user.id).first()
            if user_company:
                session['selected_company_id'] = user_company.company_id
                matched_company = next(
                    (c for c in current_user.companies if c.id == user_company.company_id),
                    None
                )
                if matched_company:
                    session['currency'] = matched_company.currency
                    session['tax_rate'] = matched_company.tax_rate
                    app.logger.info(f"Tax rate: {session.get('tax_rate', 0)}%")
