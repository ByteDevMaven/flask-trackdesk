from datetime import datetime, timedelta, UTC

from sqlalchemy import or_, and_, desc, asc, func
from flask_babel import _
from flask_login import current_user

from app.models import db, InventoryItem, StockMovement, StockMovementType


class InventoryService:
    @staticmethod
    def get_inventory_items(company_id, page=1, per_page=15, search='', supplier_id=None, sort_by='name', sort_order='asc'):
        query = InventoryItem.query.filter_by(company_id=company_id)
        
        if search:
            query = query.filter(
                or_(
                    InventoryItem.name.ilike(f'%{search}%'),
                    InventoryItem.description.ilike(f'%{search}%')
                )
            )
        
        if supplier_id and str(supplier_id).isdigit():
            query = query.filter_by(supplier_id=int(supplier_id))
            
        if sort_by == 'name':
            query = query.order_by(asc(InventoryItem.name) if sort_order == 'asc' else desc(InventoryItem.name))
        elif sort_by == 'quantity':
            query = query.order_by(asc(InventoryItem.quantity) if sort_order == 'asc' else desc(InventoryItem.quantity))
        elif sort_by == 'price':
            query = query.order_by(asc(InventoryItem.price) if sort_order == 'asc' else desc(InventoryItem.price))
        else:
            query = query.order_by(InventoryItem.name)
            
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_inventory_stats(company_id):
        total_items = InventoryItem.query.filter_by(company_id=company_id).count()
        low_stock_items = InventoryItem.query.filter(
            and_(InventoryItem.company_id == company_id, InventoryItem.quantity <= 10)
        ).count()
        out_of_stock_items = InventoryItem.query.filter(
            and_(InventoryItem.company_id == company_id, InventoryItem.quantity == 0)
        ).count()
        total_value = db.session.query(func.sum(InventoryItem.quantity * InventoryItem.price))\
            .filter_by(company_id=company_id).scalar() or 0
        
        return {
            'total_items': total_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_value': float(total_value),
            'in_stock_items': total_items - out_of_stock_items
        }

    @staticmethod
    def adjust_stock(company_id, item_id, adjustment, reference=None):
        item = InventoryItem.query.filter_by(id=item_id, company_id=company_id).first_or_404()
        new_quantity = max(0, item.quantity + adjustment)
        
        movement = StockMovement(
            company_id=company_id,
            inventory_item_id=item_id,
            user_id=current_user.id if current_user.is_authenticated else None,
            type=StockMovementType.adjustment,
            quantity=adjustment,
            reference=reference or _('Manual Adjustment'),
            date=datetime.now()
        )
        db.session.add(movement)
        
        item.quantity = new_quantity
        db.session.commit()
        return new_quantity


    @staticmethod
    def create_inventory_item(company_id, name, description=None, quantity=0, price=0.0, cost_price=0.0, discount=0.0, supplier_id=None):
        if not name:
            raise ValueError(_('Name is required'))
        if quantity < 0:
            raise ValueError(_('Quantity cannot be negative'))
        if price < 0:
            raise ValueError(_('Price cannot be negative'))
        if cost_price < 0:
            raise ValueError(_('Cost price cannot be negative'))
        if discount < 0 or discount > 100:
            raise ValueError(_('Discount must be between 0 and 100'))

        item = InventoryItem(
            company_id=company_id,
            name=name,
            description=description,
            quantity=quantity,
            price=price,
            cost_price=cost_price,
            discount=discount,
            supplier_id=int(supplier_id) if supplier_id and str(supplier_id).isdigit() else None
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def get_inventory_item(company_id, item_id):
        return InventoryItem.query.filter_by(id=item_id, company_id=company_id).first()

    @staticmethod
    def update_inventory_item(company_id, item_id, name=None, description=None, quantity=None, price=None, cost_price=None, discount=None, supplier_id=None):
        item = InventoryItem.query.filter_by(id=item_id, company_id=company_id).first_or_404()
        
        if name is not None:
            if not name.strip():
                raise ValueError(_('Name is required'))
            item.name = name.strip()
            
        if description is not None:
            item.description = description if description else None
            
        if quantity is not None:
            if quantity < 0:
                raise ValueError(_('Quantity cannot be negative'))
            item.quantity = quantity
            
        if price is not None:
            if price < 0:
                raise ValueError(_('Price cannot be negative'))
            item.price = price

        if cost_price is not None:
            if cost_price < 0:
                raise ValueError(_('Cost price cannot be negative'))
            item.cost_price = cost_price

        if discount is not None:
            if discount < 0 or discount > 100:
                raise ValueError(_('Discount must be between 0 and 100'))
            item.discount = discount
            
        if supplier_id is not None:
            item.supplier_id = int(supplier_id) if str(supplier_id).isdigit() else None
            
        db.session.commit()
        return item

    @staticmethod
    def delete_inventory_item(company_id, item_id):
        item = InventoryItem.query.filter_by(id=item_id, company_id=company_id).first_or_404()
        item.is_deleted = True
        item.deleted_at = datetime.now(UTC)
        db.session.commit()
        return True

    @staticmethod
    def get_stock_movements(company_id, item_id=None, movement_type=None, period='all', search='', page=1, per_page=20):
        query = StockMovement.query.filter_by(company_id=company_id)
        
        if item_id:
            query = query.filter_by(inventory_item_id=item_id)
            
        if search:
            query = query.join(InventoryItem).filter(
                or_(
                    InventoryItem.name.ilike(f'%{search}%'),
                    StockMovement.reference.ilike(f'%{search}%')
                )
            )
            
        if movement_type and movement_type in [t.value for t in StockMovementType]:
            query = query.filter(StockMovement.type == movement_type)
            
        today = datetime.now()
        if period == 'day':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(StockMovement.date >= start_date)
        elif period == 'week':
            start_date = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(StockMovement.date >= start_date)
        elif period == 'month':
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(StockMovement.date >= start_date)
            
        return query.order_by(StockMovement.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def bulk_delete_items(company_id, item_ids):
        if not item_ids:
            return 0
        
        items = InventoryItem.query.filter(
            and_(InventoryItem.id.in_(item_ids), InventoryItem.company_id == company_id)
        ).all()
        for item in items:
            item.is_deleted = True
            item.deleted_at = datetime.now(UTC)
        
        db.session.commit()
        return len(items)

    @staticmethod
    def search_inventory_items(company_id, query, limit=10):
        if not query or len(query) < 2:
            return []
            
        return InventoryItem.query.filter(
            and_(
                InventoryItem.company_id == company_id,
                or_(
                    InventoryItem.name.ilike(f'%{query}%'),
                    InventoryItem.description.ilike(f'%{query}%')
                )
            )
        ).limit(limit).all()
