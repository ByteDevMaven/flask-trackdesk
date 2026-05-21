from flask import Flask, abort, request, session, redirect, url_for, render_template
from flask_login import LoginManager, login_required, current_user
from flask_cors import CORS
from flask_babel import Babel
from dotenv import load_dotenv

from config import Config
from sqlalchemy import or_
from app.models import db, migrate, Company, Contact, Document, InventoryItem, PurchaseOrder
from app.extensions import bcrypt, limiter, csrf

from app.auth import auth as auth_bp
from app.dashboard import dashboard as dashboard_bp
from app.contacts import contacts as contacts_bp
from app.inventory import inventory as inventory_bp
from app.orders import orders as orders_bp
from app.invoices import invoices as invoices_bp
from app.payments import payments as payments_bp
from app.users import users as users_bp
from app.companies import companies as companies_bp

load_dotenv()

login_manager = LoginManager()
babel = Babel()

def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(Config.LANGUAGES.keys()) or "en"

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    Config.init_app(app)

                         
    register_extensions(app)

                         
    register_blueprints(app)

                                                        
    register_context_processors(app)
    register_request_hooks(app)
    register_routes(app)

    return app

def register_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    CORS(app)

    login_manager.login_view = 'auth.login'  # type: ignore[assignment]
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(companies_bp)

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

def register_routes(app: Flask):
    @app.route('/set-company/<int:id>')
    def set_company(id):
        if not current_user.is_authenticated:
            abort(401)
        for company in current_user.companies:
            if company.id == id:
                session['selected_company_id'] = id
                session['currency'] = company.currency
                session['tax_rate'] = company.tax_rate
                app.logger.info(f"Tax rate: {session.get('tax_rate', 0)}%")
                break
        return redirect(url_for('dashboard.index', company_id=session.get('selected_company_id')))

    @app.route('/set-language/<language>')
    def set_language(language):
        if language in Config.LANGUAGES:
            session['language'] = language
        return redirect(request.referrer or url_for('dashboard.index'))

    @app.route('/search')
    @login_required
    def search():
        query_text = request.args.get('q', '').strip()
        company_id = session.get('selected_company_id')
        results = {
            'contacts': [],
            'documents': [],
            'inventory_items': [],
            'purchase_orders': [],
            'companies': []
        }

        if query_text:
            search_term = f"%{query_text}%"
            company_ids = [company_id] if company_id else [c.id for c in current_user.companies]

            contacts = Contact.query.filter(Contact.company_id.in_(company_ids)).filter(
                or_(
                    Contact.name.ilike(search_term),
                    Contact.email.ilike(search_term),
                    Contact.identifier.ilike(search_term),
                    Contact.phone.ilike(search_term)
                )
            ).order_by(Contact.name).limit(10).all()

            results['contacts'] = [
                {
                    'title': c.name,
                    'subtitle': f"{c.type.name.title()} · {c.email or c.phone or c.identifier or ''}".strip(' · '),
                    'url': url_for('contacts.view', company_id=c.company_id, contact_id=c.id)
                }
                for c in contacts
            ]

            documents = Document.query.filter(Document.company_id.in_(company_ids)).filter(
                or_(
                    Document.document_number.ilike(search_term),
                    Document.status.ilike(search_term)
                )
            ).order_by(Document.issued_date.desc()).limit(10).all()

            results['documents'] = [
                {
                    'title': f"{d.document_number}",
                    'subtitle': f"{d.type.name.title()} · {d.status.name.title()} · {d.client.name if d.client else ''}".strip(' · '),
                    'url': url_for('invoices.view', company_id=d.company_id, id=d.id)
                }
                for d in documents
            ]

            inventory_items = InventoryItem.query.filter(InventoryItem.company_id.in_(company_ids)).filter(
                or_(
                    InventoryItem.name.ilike(search_term),
                    InventoryItem.description.ilike(search_term)
                )
            ).order_by(InventoryItem.name).limit(10).all()

            results['inventory_items'] = [
                {
                    'title': i.name,
                    'subtitle': i.description or '',
                    'url': url_for('inventory.view', company_id=i.company_id, id=i.id)
                }
                for i in inventory_items
            ]

            purchase_orders = PurchaseOrder.query.filter(PurchaseOrder.company_id.in_(company_ids)).filter(
                PurchaseOrder.order_number.ilike(search_term)
            ).order_by(PurchaseOrder.buy_date.desc()).limit(10).all()

            results['purchase_orders'] = [
                {
                    'title': p.order_number,
                    'subtitle': f"{p.supplier.name if p.supplier else ''} · {p.buy_date.isoformat() if p.buy_date else ''}".strip(' · '),
                    'url': url_for('orders.view', company_id=p.company_id, id=p.id)
                }
                for p in purchase_orders
            ]

            if not company_id:
                company_ids = [c.id for c in current_user.companies]
                company_results = Company.query.filter(Company.id.in_(company_ids)).filter(
                    or_(
                        Company.name.ilike(search_term),
                        Company.identifier.ilike(search_term),
                        Company.email.ilike(search_term),
                        Company.phone.ilike(search_term)
                    )
                ).order_by(Company.name).limit(10).all()

                results['companies'] = [
                    {
                        'title': c.name,
                        'subtitle': f"{c.identifier or ''} · {c.email or ''}".strip(' · '),
                        'url': url_for('companies.view', id=c.id)
                    }
                    for c in company_results
                ]

        return render_template('search/results.html', query=query_text, results=results)

def register_context_processors(app: Flask):
    @app.context_processor
    def inject_conf_var():
        from datetime import datetime, UTC
        return dict(
            AVAILABLE_LANGUAGES=Config.LANGUAGES,
            CURRENT_LANGUAGE=get_locale(),
            now=datetime.now(UTC),
            company_id=session.get('selected_company_id'),
            current_user=current_user
        )
