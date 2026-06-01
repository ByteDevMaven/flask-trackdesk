from datetime import datetime, timedelta, UTC

from sqlalchemy import func

from app.models import Contact, Document, DocumentType, InventoryItem, Payment, db
from app.models.enums import ContactType


class DashboardService:
    @staticmethod
    def _calculate_growth(current, previous) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    @staticmethod
    def get_dashboard_data(company_id: int) -> dict:
        today = datetime.now(UTC)
        first_day_of_month = datetime(today.year, today.month, 1)
        first_day_of_last_month = (
            datetime(today.year, today.month - 1, 1)
            if today.month > 1
            else datetime(today.year - 1, 12, 1)
        )
        last_day_of_last_month = first_day_of_month - timedelta(days=1)

        # Current period stats
        client_count = Contact.query.filter_by(company_id=company_id, type=ContactType.customer).count()
        outstanding_invoice_count = Document.query.filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice,
            Document.status != 'paid'
        ).count()
        inventory_count = InventoryItem.query.filter_by(company_id=company_id).count()
        revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.company_id == company_id,
            Payment.payment_date >= first_day_of_month
        ).scalar() or 0

        # Previous period stats (for growth)
        last_month_clients = Contact.query.filter(
            Contact.company_id == company_id,
            Contact.type == ContactType.customer,
            Contact.created_at < first_day_of_month
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

        # Growth calculations
        client_growth = DashboardService._calculate_growth(client_count, last_month_clients)
        outstanding_growth = DashboardService._calculate_growth(outstanding_invoice_count, last_month_outstanding)
        inventory_growth = DashboardService._calculate_growth(inventory_count, last_month_inventory)
        revenue_growth = DashboardService._calculate_growth(revenue, last_month_revenue)

        # Recent documents
        recent_invoices = Document.query.filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice
        ).order_by(Document.issued_date.desc()).limit(5).all()
        for inv in recent_invoices:
            inv.client = Contact.query.get(inv.client_id) if inv.client_id else None

        recent_quotes = Document.query.filter(
            Document.company_id == company_id,
            Document.type == DocumentType.quote
        ).order_by(Document.issued_date.desc()).limit(5).all()
        for q in recent_quotes:
            q.client = Contact.query.get(q.client_id) if q.client_id else None

        # Mark overdue invoices
        overdue_invoices = Document.query.filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice,
            Document.status != 'paid',
            Document.due_date < today
        ).all()
        updated = False
        for invoice in overdue_invoices:
            if invoice.status != 'overdue':
                invoice.status = 'overdue'
                updated = True
        if updated:
            db.session.commit()

        return {
            'client_count': client_count,
            'outstanding_invoice_count': outstanding_invoice_count,
            'inventory_count': inventory_count,
            'revenue': revenue,
            'recent_invoices': recent_invoices,
            'recent_quotes': recent_quotes,
            'client_growth': client_growth,
            'outstanding_growth': outstanding_growth,
            'inventory_growth': inventory_growth,
            'revenue_growth': revenue_growth,
        }
