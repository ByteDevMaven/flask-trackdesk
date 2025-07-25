from flask import render_template, session
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timedelta
from flask_babel import _

from models import Client, Document, DocumentType, InventoryItem, Payment, db

from . import dashboard

@dashboard.route('/')
@dashboard.route('/<int:company_id>/')
@dashboard.route('/<int:company_id>/dashboard')
@login_required
def index(company_id = None):
    if company_id == None:
        company_id = session.get('selected_company_id')

    today = datetime.now()
    first_day_of_month = datetime(today.year, today.month, 1)
    first_day_of_last_month = datetime(today.year, today.month - 1, 1) if today.month > 1 else datetime(today.year - 1, 12, 1)
    last_day_of_last_month = first_day_of_month - timedelta(days=1)

    # Current month metrics
    client_count = Client.query.filter_by(company_id=company_id).count()
    outstanding_invoice_count = Document.query.filter(
        Document.company_id == company_id,
        Document.type == DocumentType.invoice,
        Document.status != 'paid'
    ).count()
    inventory_count = InventoryItem.query.filter_by(company_id=company_id).count()
    
    # Calculate revenue for month-to-date (sum of payments in current month)
    revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.company_id == company_id,
        Payment.payment_date >= first_day_of_month
    ).scalar() or 0

    # Previous month metrics for comparison
    last_month_clients = Client.query.filter(
        Client.company_id == company_id,
        Client.created_at < first_day_of_month
    ).count()
    
    last_month_outstanding = Document.query.filter(
        Document.company_id == company_id,
        Document.type == DocumentType.invoice,
        Document.status != 'paid',
        Document.issued_date < first_day_of_month
    ).count()
    
    last_month_inventory = InventoryItem.query.filter(
        InventoryItem.company_id == company_id,
        InventoryItem.created_at < first_day_of_month
    ).count()
    
    last_month_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.company_id == company_id,
        Payment.payment_date >= first_day_of_last_month,
        Payment.payment_date <= last_day_of_last_month
    ).scalar() or 0

    # Calculate growth percentages
    def calculate_growth(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)

    client_growth = calculate_growth(client_count, last_month_clients)
    outstanding_growth = calculate_growth(outstanding_invoice_count, last_month_outstanding)
    inventory_growth = calculate_growth(inventory_count, last_month_inventory)
    revenue_growth = calculate_growth(revenue, last_month_revenue)

    recent_invoices = Document.query.filter(
        Document.company_id == company_id,
        Document.type == DocumentType.invoice
    ).order_by(Document.issued_date.desc()).limit(5).all()

    recent_quotes = Document.query.filter(
        Document.company_id == company_id,
        Document.type == DocumentType.quote
    ).order_by(Document.issued_date.desc()).limit(5).all()
    
    # Check for overdue invoices and update their status
    overdue_invoices = Document.query.filter(
        Document.company_id == company_id,
        Document.type == DocumentType.invoice,
        Document.status != 'paid',
        Document.due_date < today
    ).all()
    
    for invoice in overdue_invoices:
        if invoice.status != 'overdue':
            invoice.status = 'overdue'
    
    # Commit any status changes
    if overdue_invoices:
        db.session.commit()
    
    return render_template(
        'dashboard/index.html',
        client_count=client_count,
        outstanding_invoice_count=outstanding_invoice_count,
        inventory_count=inventory_count,
        revenue=revenue,
        recent_invoices=recent_invoices,
        recent_quotes=recent_quotes,
        # Growth metrics
        client_growth=client_growth,
        outstanding_growth=outstanding_growth,
        inventory_growth=inventory_growth,
        revenue_growth=revenue_growth
    )

# Custom template filters
@dashboard.app_template_filter('format_currency')
def format_currency(value):
    """Format a number as currency"""
    if value is None:
        return "0.00"
    return f"{float(value):,.2f}"

@dashboard.app_template_filter('format_date')
def format_date(value):
    """Format a date in a readable format"""
    if value is None:
        return ""
    return value.strftime("%b %d, %Y")

@dashboard.app_template_filter('locale_date')
def locale_date(value):
    """Format date according to the current locale"""
    from flask_babel import format_datetime
    
    if value is None:
        return ""
    
    try:
        return format_datetime(value, format='medium')
    except:
        # Fall back to basic formatting
        return value.strftime("%b %d, %Y")