from datetime import datetime, UTC

from app.models import Company, InventoryItem, Notification, User, UserStatus, db

LOW_STOCK_THRESHOLD = 5


def _inventory_link(item):
    if item.sku:
        return f'/{item.company_id}/inventory/{item.sku}'
    return f'/{item.company_id}/inventory'


def _active_company_users(company_id):
    return (
        User.query
        .filter(
            User.status == UserStatus.active,
            User.companies.any(Company.id == company_id),
        )
        .order_by(User.id)
        .all()
    )


def _notification_exists(user_id, company_id, link_url):
    return Notification.query.filter(
        Notification.user_id == user_id,
        Notification.company_id == company_id,
        Notification.type == 'low_stock',
        Notification.link_url == link_url,
    ).first() is not None


def send_low_stock_notifications(threshold=LOW_STOCK_THRESHOLD, commit=True):
    now = datetime.now(UTC)
    low_stock_items = (
        InventoryItem.query
        .filter(InventoryItem.quantity <= threshold)
        .order_by(InventoryItem.company_id, InventoryItem.name)
        .all()
    )

    created_count = 0
    checked_count = 0

    for item in low_stock_items:
        checked_count += 1
        link_url = _inventory_link(item)
        quantity = item.quantity or 0
        body = (
            f'El producto {item.name} tiene stock bajo. '
            f'Cantidad actual: {quantity}.'
        )

        for user in _active_company_users(item.company_id):
            if _notification_exists(user.id, item.company_id, link_url):
                continue

            db.session.add(Notification(
                user_id=user.id,
                company_id=item.company_id,
                type='low_stock',
                title=f'Stock bajo: {item.name}',
                message=body,
                body=body,
                link_url=link_url,
                priority='high',
                channel='in_app',
                status='unread',
                is_popup=False,
                sent_at=now,
            ))
            created_count += 1

    if commit:
        db.session.commit()

    return {
        'checked_items': checked_count,
        'created_notifications': created_count,
        'threshold': threshold,
    }
