from io import BytesIO
from datetime import datetime, timedelta

import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import or_, and_, desc, asc, func
from flask_babel import _
from flask_login import current_user

from models import db, InventoryItem, StockMovement, StockMovementType


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
    def generate_barcode_image(company_id, item_id, item_name, item_price, currency_symbol='$', for_download=False, compact=False):
        """Generates a barcode image in memory and returns (output_buffer, barcode_data)."""
        barcode_data = f"{company_id}{item_id:06d}"
        
        code128 = barcode.get_barcode_class('code128')
        
        writer = ImageWriter()
        
        # Configure writer options
        writer_options = {
            'module_width': 0.2, # defaults to 0.2
            'module_height': 15.0, # defaults to 15.0
            'quiet_zone': 6.5, # defaults to 6.5
            'font_size': 10,
            'text_distance': 5.0,
            'background': 'white',
            'foreground': 'black',
            'write_text': True,
            'text': barcode_data,
        }
        
        # if compact:
        #     # Enhanced size for readability in grid printing
        #     writer_options.update({
        #         'module_width': 0.15,
        #         'module_height': 5.0,
        #         'font_size': 1, # Cannot be 0, so make it tiny
        #         'write_text': False,
        #         'quiet_zone': 2.0
        #     })
        
        writer.set_options(writer_options)

        barcode_instance = code128(barcode_data, writer=writer)
        
        buffer = BytesIO()
        barcode_instance.write(buffer, options=writer_options)
        buffer.seek(0)
        
        barcode_img = Image.open(buffer)
        
        # We manually add text on top/bottom
        img_width, img_height = barcode_img.size
        
        # Extra space for manually written text
        extra_space = 45 if compact else (60 if for_download else 80)
        new_height = img_height + extra_space
        final_img = Image.new('RGB', (img_width, new_height), 'white')
        final_img.paste(barcode_img, (0, 0)) 
        
        draw = ImageDraw.Draw(final_img)
        
        try:
            if compact:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 9)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
            else:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18 if for_download else 16)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14 if for_download else 12)
        except Exception:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            
        def get_text_width(text, font):
            try:
                # new PIL
                return draw.textbbox((0, 0), text, font=font)[2] - draw.textbbox((0, 0), text, font=font)[0]
            except Exception:
                try:
                    # older PIL
                    return draw.textsize(text, font=font)[0]
                except Exception:
                    # fallback approximation
                    return len(text) * 6
            
        text_y = img_height + (5 if compact else 10)
        truncate_len = 25 if compact else (50 if for_download else 40)
        name_text = item_name[:truncate_len]
        
        # Consistent layout: Item Name on top, Price/Code on bottom
        # Item name
        draw.text((5 if compact else 10, text_y), name_text, fill='black', font=font_large)
        
        # Second line position
        text_y += (15 if compact else 25)
        
        # Price (bottom left)
        price_text = f"{currency_symbol}{item_price:,.2f}"
        if for_download:
            price_text = f"{_('Price')} {price_text}"
        draw.text((5 if compact else 10, text_y), price_text, fill='black', font=font_medium)
        
        # Code (bottom right - only if not for download or if compact)
        if not for_download or compact:
            code_text = barcode_data if compact else f"Code: {barcode_data}"
            code_width = get_text_width(code_text, font_medium)
            draw.text((img_width - code_width - (5 if compact else 10), text_y), code_text, fill='black', font=font_medium)
            
        output_buffer = BytesIO()
        final_img.save(output_buffer, format='PNG', dpi=(300, 300) if (for_download or compact) else (72, 72))
        output_buffer.seek(0)
        
        return output_buffer, barcode_data

    @staticmethod
    def create_inventory_item(company_id, name, description=None, quantity=0, price=0.0, supplier_id=None):
        if not name:
            raise ValueError(_('Name is required'))
        if quantity < 0:
            raise ValueError(_('Quantity cannot be negative'))
        if price < 0:
            raise ValueError(_('Price cannot be negative'))

        item = InventoryItem(
            company_id=company_id,
            name=name,
            description=description,
            quantity=quantity,
            price=price,
            supplier_id=int(supplier_id) if supplier_id and str(supplier_id).isdigit() else None
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def get_inventory_item(company_id, item_id):
        return InventoryItem.query.filter_by(id=item_id, company_id=company_id).first()

    @staticmethod
    def update_inventory_item(company_id, item_id, name=None, description=None, quantity=None, price=None, supplier_id=None):
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
            
        if supplier_id is not None:
            item.supplier_id = int(supplier_id) if str(supplier_id).isdigit() else None
            
        db.session.commit()
        return item

    @staticmethod
    def delete_inventory_item(company_id, item_id):
        item = InventoryItem.query.filter_by(id=item_id, company_id=company_id).first_or_404()
        db.session.delete(item)
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
        
        deleted_count = InventoryItem.query.filter(
            and_(InventoryItem.id.in_(item_ids), InventoryItem.company_id == company_id)
        ).delete(synchronize_session=False)
        
        db.session.commit()
        return deleted_count

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
