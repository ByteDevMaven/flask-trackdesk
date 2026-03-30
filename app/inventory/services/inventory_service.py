from io import BytesIO
from datetime import datetime

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
        
        if compact:
            # Significant reduction in size for printing many per page
            writer_options.update({
                'module_width': 0.15,
                'module_height': 5.0,
                'font_size': 1, # Cannot be 0, so make it tiny
                'write_text': False,
                'quiet_zone': 2.0
            })
        
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
            
        text_y = img_height + (2 if compact else 10)
        truncate_len = 22 if compact else (50 if for_download else 40)
        name_text = item_name[:truncate_len]
        
        if compact:
            # Center item name
            draw.text(((img_width - get_text_width(name_text, font_large)) / 2, text_y), name_text, fill='black', font=font_large)
            text_y += 12
            # Center price
            price_text = f"{_('Price')} {currency_symbol}{item_price:,.2f}"
            draw.text(((img_width - get_text_width(price_text, font_medium)) / 2, text_y), price_text, fill='black', font=font_medium)
            text_y += 12
            # Center code
            draw.text(((img_width - get_text_width(barcode_data, font_medium)) / 2, text_y), barcode_data, fill='black', font=font_medium)
        else:
            # Item name
            draw.text((10, text_y), name_text, fill='black', font=font_large)
            text_y += 25
            price_text = f"{_('Price')} {currency_symbol}{item_price:,.2f}" if for_download else f"{currency_symbol}{item_price:.2f}"
            draw.text((10, text_y), price_text, fill='black', font=font_medium)
            if not for_download:
                draw.text((img_width - 100, text_y), f"Code: {barcode_data}", fill='black', font=font_medium)
            
        output_buffer = BytesIO()
        final_img.save(output_buffer, format='PNG', dpi=(300, 300) if (for_download or compact) else (72, 72))
        output_buffer.seek(0)
        
        return output_buffer, barcode_data
