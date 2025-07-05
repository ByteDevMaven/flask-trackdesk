from flask import render_template
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime
from flask_babel import _

from models import Client, Document, DocumentType, InventoryItem, Payment, db

from . import dashboard

@dashboard.route('/<int:company_id>/')
@dashboard.route('/<int:company_id>/dashboard')
@login_required
def index(company_id = None):
    today = datetime.now()
    first_day_of_month = datetime(today.year, today.month, 1)

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
        page_title=_('Dashboard')
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

@dashboard.app_template_filter('locale_currency')
def locale_currency(value):
    """Format number according to the current locale, without currency symbol"""
    from flask_babel import get_locale
    import locale

    if value is None:
        return "0.00"

    try:
        # Set locale based on current language
        locale_str = str(get_locale())
        locale.setlocale(locale.LC_ALL, (locale_str, 'UTF-8'))

        # Format as number with grouping (no currency symbol)
        return locale.format_string('%.2f', float(value), grouping=True)
    except:
        # Fallback if locale fails
        return f"{float(value):,.2f}"

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