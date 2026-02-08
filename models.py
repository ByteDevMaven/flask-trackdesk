from datetime import datetime
import enum

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_babel import _

db = SQLAlchemy()
migrate = Migrate()

# Association table for roles and permissions
role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True, index=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True, index=True)
)

# Association table for users and companies
user_companies = db.Table(
    'user_companies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True, index=True),
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id'), primary_key=True, index=True)
)

class DocumentType(enum.Enum):
    quote = 'quote'
    invoice = 'invoice'

class InvoiceType(enum.Enum):
    sent = _('sent')
    draft = _('draft')
    issued = _('issued')
    cancelled = _('cancelled')
    partial = _('partial')
    paid = _('paid')
    overdue = _('overdue')
    pending = _('pending')
    credit = _('credit')

class PaymentMethod(enum.Enum):
    cash = _('cash')
    bank_transfer = _('bank transfer')
    credit_card = _('credit card')
    cheque = _('cheque')
    other = _('other')

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    currency = db.Column(db.String, default='$')
    tax_rate = db.Column(db.Float, default=0.0)
    address = db.Column(db.String)
    phone = db.Column(db.String, index=True)
    email = db.Column(db.String, index=True)
    identifier = db.Column(db.String(50), index=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True, index=True)
    permissions = db.relationship('Permission', secondary=role_permissions, back_populates='roles')

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True, index=True)
    roles = db.relationship('Role', secondary=role_permissions, back_populates='permissions')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    name = db.Column(db.String, nullable=False, index=True)
    email = db.Column(db.String, unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), index=True)
    companies = db.relationship('Company', secondary=user_companies, backref='users')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False, index=True)
    identifier = db.Column(db.String(50), default='', nullable=False, index=True)
    email = db.Column(db.String, index=True)
    phone = db.Column(db.String, index=True)
    address = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False, index=True)
    contact_email = db.Column(db.String, index=True)
    phone = db.Column(db.String, index=True)
    address = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False, index=True)
    description = db.Column(db.String)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    discount = db.Column(db.Float, default=0.0)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), index=True)

    supplier = db.relationship('Supplier', backref='inventory_items')
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String, nullable=False, unique=True, index=True)
    order_document = db.Column(db.String, default='document-000000', nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)

    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    supplier = db.relationship('Supplier', backref='purchase_orders')
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan')

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False, index=True)

    item_code = db.Column(db.String, nullable=False, default='', index=True)
    name = db.Column(db.String, nullable=False, default='')
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.00)
    total = db.Column(db.Float, nullable=False, default=0.00)

    inventory_item = db.relationship('InventoryItem', backref='purchase_order_items')

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    document_number = db.Column(db.String, unique=True, nullable=False, index=True)
    type = db.Column(db.Enum(DocumentType), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    status = db.Column(db.Enum(InvoiceType), nullable=False, default=InvoiceType.draft)
    total_amount = db.Column(db.Float)
    issued_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    payments = db.relationship('Payment', backref='document', cascade='all, delete-orphan', lazy='dynamic')

    def get_balance(self):
        paid = sum((p.amount or 0) for p in self.payments)
        return (self.total_amount or 0) - paid

class DocumentItem(db.Model):
    __tablename__ = 'document_items'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), index=True)
    description = db.Column(db.String)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    discount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), index=True)
    amount = db.Column(db.Float)
    payment_date = db.Column(db.DateTime)
    method = db.Column(db.Enum(PaymentMethod), nullable=False, default=PaymentMethod.cash)
    notes = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String, nullable=False, index=True)
    report_type = db.Column(db.String, index=True)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    file_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    type = db.Column(db.String, index=True)  # 'email' or 'whatsapp'
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String, index=True)  # 'sent', 'failed', etc.
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())