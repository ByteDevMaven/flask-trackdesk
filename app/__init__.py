from flask import Flask, abort, request, session, redirect, url_for
from flask_login import LoginManager, current_user
from flask_cors import CORS
from flask_babel import Babel
from dotenv import load_dotenv

from config import Config
from models import db, migrate
from extensions import bcrypt, limiter, csrf

from app.auth import auth as auth_bp
from app.dashboard import dashboard as dashboard_bp
from app.customers import customers as customers_bp
from app.suppliers import suppliers as suppliers_bp
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

    # Register extensions
    register_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register context processors, request hooks, routes
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
        from models import User
        return db.session.get(User, int(user_id))

def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(companies_bp)

def register_request_hooks(app: Flask):
    @app.before_request
    def ensure_company_selected():
        from models import user_companies
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

def register_context_processors(app: Flask):
    @app.context_processor
    def inject_conf_var():
        return dict(
            AVAILABLE_LANGUAGES=Config.LANGUAGES,
            CURRENT_LANGUAGE=get_locale()
        )