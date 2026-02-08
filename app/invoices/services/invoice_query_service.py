from sqlalchemy import or_
from datetime import datetime
from flask import current_app
from models import db, Document, Client, DocumentType


def get_invoice_list(company_id, filters):
    page = int(filters.get("page", 1))
    search = filters.get("search", "")
    status = filters.get("status", "")
    doc_type = filters.get("type", "")
    date_from = filters.get("date_from", "")
    date_to = filters.get("date_to", "")

    query = db.session.query(Document).filter(
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice,
            Document.type == DocumentType.quote)
    )

    if search:
        query = query.outerjoin(Client).filter(
            or_(
                Document.document_number.ilike(f"%{search}%"),
                Client.name.ilike(f"%{search}%")
            )
        )

    if status:
        query = query.filter(Document.status == status)

    if doc_type == "invoice":
        query = query.filter(Document.type == DocumentType.invoice)
    elif doc_type == "quote":
        query = query.filter(Document.type == DocumentType.quote)

    if date_from:
        try:
            query = query.filter(
                Document.issued_date >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        except ValueError:
            current_app.logger.warning(f"Invalid date_from format: {date_from}")

    if date_to:
        try:
            query = query.filter(
                Document.issued_date <= datetime.strptime(date_to, "%Y-%m-%d")
            )
        except ValueError:
            current_app.logger.warning(f"Invalid date_to format: {date_to}")

    query = query.order_by(Document.id.desc())

    pagination = query.paginate(
        page=page,
        per_page=int(current_app.config.get("ITEMS_PER_PAGE", 20)),
        error_out=False
    )

    return pagination
