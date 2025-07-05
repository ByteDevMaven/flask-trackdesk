from flask import Flask, abort, request, session, redirect, url_for
from flask_login import LoginManager, current_user
from flask_cors import CORS
from flask_babel import Babel, _
from dotenv import load_dotenv

from config import Config
from models import db, migrate
from extensions import bcrypt, limiter, csrf

load_dotenv()

login_manager = LoginManager()
babel = Babel()

def get_locale():
    # 1. Check if user has explicitly set a language in session
    if 'language' in session:
        return session['language']
    
    # 2. Otherwise, detect from browser's Accept-Language header
    return request.accept_languages.best_match(Config.LANGUAGES.keys())

def createApp():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    CORS(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    
    # Initialize Babel for internationalization
    babel.init_app(app, locale_selector=get_locale)

    # Create a user loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))
    
    @app.before_request
    def ensure_company_selected():
        from models import user_companies
        if current_user.is_authenticated and 'selected_company_id' not in session:
            user_company = db.session.query(user_companies).filter_by(user_id=current_user.id).first()
            if user_company:
                session['selected_company_id'] = user_company.company_id

    @app.route('/set-company/<int:id>')
    def set_company(id):
        if not current_user.is_authenticated:
            abort(401)

        # Loop through the user's related companies
        for company in current_user.companies:
            if company.id == id:
                session['selected_company_id'] = id
                break  # Stop if found

        # return redirect(request.referrer or url_for('dashboard.index', company_id=session.get('selected_company_id')))
        return redirect(url_for('dashboard.index', company_id=session.get('selected_company_id')))
    
    # Language switcher route
    @app.route('/set-language/<language>')
    def set_language(language):
        if language in Config.LANGUAGES:
            session['language'] = language
        return redirect(request.referrer or url_for('dashboard.index'))
    
    # Make language info available to all templates
    @app.context_processor
    def inject_conf_var():
        return dict(
            AVAILABLE_LANGUAGES=Config.LANGUAGES,
            CURRENT_LANGUAGE=get_locale()
        )

    with app.app_context():
        from auth import auth
        from dashboard import dashboard
        from customers import customers
        from suppliers import suppliers
        from inventory import inventory
        from invoices import invoices
        from payments import payments
        from users import users
        from companies import companies

        app.register_blueprint(auth)
        app.register_blueprint(dashboard)
        app.register_blueprint(customers)
        app.register_blueprint(suppliers)
        app.register_blueprint(inventory)
        app.register_blueprint(invoices)
        app.register_blueprint(payments)
        app.register_blueprint(users)
        app.register_blueprint(companies)

    return app

app = createApp()

if __name__ == '__main__':
    app.run(debug=True)