from flask import Flask

from app.auth import auth as auth_bp
from app.dashboard import dashboard as dashboard_bp
from app.contacts import contacts as contacts_bp
from app.inventory import inventory as inventory_bp
from app.orders import orders as orders_bp
from app.invoices import invoices as invoices_bp
from app.payments import payments as payments_bp
from app.users import users as users_bp
from app.companies import companies as companies_bp
from app.accounting import accounting as accounting_bp
from app.warehouses import warehouses as warehouses_bp
from app.hr import hr as hr_bp

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
    app.register_blueprint(accounting_bp)
    app.register_blueprint(warehouses_bp)
    app.register_blueprint(hr_bp)
