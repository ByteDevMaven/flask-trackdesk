from models import PurchaseOrder, db
from sqlalchemy import func
from datetime import datetime


def get_purchase_order_stats(company_id):
    total_orders = PurchaseOrder.query.filter_by(
        company_id=company_id
    ).count()

    total_value = db.session.query(
        func.sum(PurchaseOrder.total_amount)
    ).filter_by(company_id=company_id).scalar() or 0

    recent_orders = PurchaseOrder.query.filter_by(
        company_id=company_id
    ).filter(
        PurchaseOrder.created_at >= datetime.now().replace(day=1)
    ).count()

    avg_order_value = (
        total_value / total_orders if total_orders else 0
    )

    return {
        'total_orders': total_orders,
        'total_value': total_value,
        'recent_orders': recent_orders,
        'avg_order_value': avg_order_value,
    }