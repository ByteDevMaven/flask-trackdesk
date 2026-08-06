from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.models import Contact, Document, DocumentType, InventoryItem, Payment, db
from app.models.enums import ContactType, DocumentStatus


class DashboardService:
    @staticmethod
    def _calculate_growth(current, previous) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    @staticmethod
    def _month_boundaries(now: datetime) -> tuple[datetime, datetime, datetime]:
        current_start = datetime(now.year, now.month, 1)
        previous_start = (
            datetime(now.year, now.month - 1, 1)
            if now.month > 1
            else datetime(now.year - 1, 12, 1)
        )
        next_start = (
            datetime(now.year + 1, 1, 1)
            if now.month == 12
            else datetime(now.year, now.month + 1, 1)
        )
        return previous_start, current_start, next_start

    @staticmethod
    def get_dashboard_data(company_id: int) -> dict:
        now = datetime.now(UTC)
        previous_start, current_start, next_start = DashboardService._month_boundaries(now)
        customer_types = [ContactType.customer, ContactType.customer_supplier]
        open_statuses = [
            DocumentStatus.sent,
            DocumentStatus.issued,
            DocumentStatus.partial,
            DocumentStatus.overdue,
            DocumentStatus.pending,
        ]

        client_count = Contact.query.filter(
            Contact.company_id == company_id,
            Contact.type.in_(customer_types),
        ).count()
        outstanding_invoice_count = Document.query.filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice,
            Document.status.in_(open_statuses),
        ).count()
        inventory_count = InventoryItem.query.filter_by(company_id=company_id).count()
        revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.company_id == company_id,
            Payment.payment_date >= current_start,
            Payment.payment_date < next_start,
        ).scalar() or 0

        def count_created(model, start, end, *filters):
            return model.query.filter(
                model.company_id == company_id,
                model.created_at >= start,
                model.created_at < end,
                *filters,
            ).count()

        current_clients = count_created(Contact, current_start, next_start, Contact.type.in_(customer_types))
        previous_clients = count_created(Contact, previous_start, current_start, Contact.type.in_(customer_types))
        current_inventory = count_created(InventoryItem, current_start, next_start)
        previous_inventory = count_created(InventoryItem, previous_start, current_start)
        current_outstanding = Document.query.filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice,
            Document.status.in_(open_statuses),
            Document.issued_date >= current_start,
            Document.issued_date < next_start,
        ).count()
        previous_outstanding = Document.query.filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice,
            Document.status.in_(open_statuses),
            Document.issued_date >= previous_start,
            Document.issued_date < current_start,
        ).count()
        previous_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.company_id == company_id,
            Payment.payment_date >= previous_start,
            Payment.payment_date < current_start,
        ).scalar() or 0

        recent_invoices = Document.query.options(joinedload(Document.client)).filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice,
        ).order_by(Document.issued_date.desc()).limit(5).all()
        recent_quotes = Document.query.options(joinedload(Document.client)).filter(
            Document.company_id == company_id,
            Document.type == DocumentType.quote,
        ).order_by(Document.issued_date.desc()).limit(5).all()

        return {
            "client_count": client_count,
            "outstanding_invoice_count": outstanding_invoice_count,
            "inventory_count": inventory_count,
            "revenue": revenue,
            "recent_invoices": recent_invoices,
            "recent_quotes": recent_quotes,
            "client_growth": DashboardService._calculate_growth(current_clients, previous_clients),
            "outstanding_growth": DashboardService._calculate_growth(current_outstanding, previous_outstanding),
            "inventory_growth": DashboardService._calculate_growth(current_inventory, previous_inventory),
            "revenue_growth": DashboardService._calculate_growth(revenue, previous_revenue),
        }
