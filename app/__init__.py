from flask import Flask
from dotenv import load_dotenv

from config import Config
from app.extensions import register_extensions
from app.blueprints import register_blueprints
from app.context_processors import register_context_processors
from app.hooks import register_request_hooks
from app.routes import register_routes
from app.cli import register_cli
from app.middleware import init_rbac, register_audit_listeners

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    Config.init_app(app)

    register_extensions(app)
    with app.app_context():
        register_audit_listeners()
    register_blueprints(app)
    register_context_processors(app)
    register_request_hooks(app)
    register_routes(app)
    init_rbac(app)
    register_cli(app)

    return app

