import io

from flask import Response, current_app, flash, jsonify, redirect, render_template, request, send_file, session, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import limiter
from app.models import Contact, InventoryItem, db
from app.models.enums import ContactType
from app.utils import resolve_company

from .. import inventory
from ..services import InventoryService


@inventory.route('/<string:company_id>/inventory/<string:sku>/barcode')
@login_required
@limiter.exempt
def barcode(company_id, sku):
    company = resolve_company(company_id)
    company_id = company.id
    """Barcode label for an inventory item"""
    item = InventoryService.get_item_by_sku(company_id, sku)
    if not item:
        from flask import abort; abort(404)
    copies = request.args.get('copies', 12, type=int)
    currency_symbol = session.get('currency', '$')
    barcode_value = item.generated_tag

    return render_template('inventory/barcode.html',
                          company_id=company_id,
                          item=item,
                          copies=copies,
                          currency_symbol=currency_symbol,
                          barcode_value=barcode_value)
