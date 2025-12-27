from models import PurchaseOrder, Supplier
from sqlalchemy import asc, desc, or_


def get_purchase_orders(
    company_id,
    page,
    per_page,
    search=None,
    supplier_id=None,
    sort_by='created_at',
    sort_order='desc'
):
    query = PurchaseOrder.query.filter_by(company_id=company_id)

    if search:
        query = query.filter(
            or_(
                PurchaseOrder.order_number.ilike(f'%{search}%'),
                PurchaseOrder.supplier.has(
                    Supplier.name.ilike(f'%{search}%')
                )
            )
        )

    if supplier_id and str(supplier_id).isdigit():
        query = query.filter_by(supplier_id=int(supplier_id))

    sort_map = {
        'order_number': PurchaseOrder.order_number,
        'total_amount': PurchaseOrder.total_amount,
        'created_at': PurchaseOrder.created_at,
    }

    sort_column = sort_map.get(sort_by, PurchaseOrder.created_at)
    order_fn = asc if sort_order == 'asc' else desc
    query = query.order_by(order_fn(sort_column))

    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )