"""
invoice_pdf_service.py
======================
Pure PDF overlay engine — contains zero customer-specific logic.

All customer knowledge (template filename, coordinate positions) lives in
``app/invoices/services/pdf_layouts/``.  Add one file per customer there.

Usage from a script / management command
-----------------------------------------
    from app.invoices.services.invoice_pdf_service import generate_invoice_pdf
    from app.invoices.services.pdf_layouts import get_layout
    from app.models import Document

    doc = Document.query.get(42)
    layout = get_layout(doc.company_id)      # looks up the right customer layout

    pdf_bytes, filename = generate_invoice_pdf(
        doc,
        layout=layout,
        currency="L",
        tax_rate=0.15,
        include_tax=True,
        seller_name="Jane Doe",
    )
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
"""

from __future__ import annotations

import copy
import math
import os
from dataclasses import dataclass, field
from io import BytesIO

from flask import current_app
from flask_babel import _, get_locale

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from num2words import num2words

from app.models import (
    Contact,
    DocumentItem,
    DocumentType,
    InventoryItem,
    PaymentMethod,
)


# ============================================================================
# Coordinate dataclasses — reusable building blocks for any layout
# All y values are expressed as offsets FROM THE TOP of the page.
# ReportLab draws from the bottom, so internally we convert: y = height - offset
# ============================================================================

@dataclass
class HeaderCoords:
    """Coordinates for the document header block."""
    # White-out rectangle [x, offset_from_top, width, height]
    whiteout_rect: tuple = (10, 135, 120, 17)

    doc_type_x: float = 12
    doc_type_y_from_top: float = 130

    doc_number_x: float = 140
    doc_number_y_from_top: float = 130

    page_current_x: float = 49
    page_total_x: float = 70
    page_y_from_top: float = 110

    issued_date_x: float = 480
    issued_date_y_from_top: float = 165

    due_date_x: float = 480
    due_date_y_from_top: float = 172           # quotes
    payment_condition_y_from_top: float = 180  # invoices

    company_id_x: float = 480
    company_id_y_from_top: float = 196
    seller_x: float = 480
    seller_y_from_top: float = 210

    title_font_size: int = 11
    detail_font_size: int = 9


@dataclass
class ClientCoords:
    """Coordinates for the client information block."""
    block_y_from_top: float = 165
    x: float = 140
    line_gap: float = 15
    fallback_x: float = 100
    font_size: int = 10


@dataclass
class ItemsCoords:
    """Coordinates for the line-items table."""
    y_start_from_top: float = 260
    row_height: float = 15
    items_per_page: int = 25

    col_codigo: float = 30
    col_articulo: float = 110
    col_cantidad: float = 280
    col_precio: float = 350
    col_descuento: float = 430
    col_valor: float = 480

    col_cantidad_offset: float = 10
    col_precio_offset: float = 35
    col_descuento_offset: float = 35
    col_valor_offset: float = 65

    max_codigo_chars: int = 8
    max_articulo_chars: int = 25
    font_size: int = 8


@dataclass
class TotalsCoords:
    """Coordinates for the totals section on the last page."""
    x: float = 480
    y_anchor_from_top: float = 650
    right_x_offset: float = 50

    row_exenta: float = 27
    row_gravada_15: float = 45
    row_gravada_18: float = 65
    row_exonerada: float = 82
    row_imp_15: float = 100
    row_imp_18: float = 117
    row_total: float = 140

    words_x_offset: float = -160   # relative to x
    words_y_offset: float = 180    # subtracted from anchor_y

    font_size: int = 9
    total_font_size: int = 11
    words_font_size: int = 10
    max_words_chars: int = 70


@dataclass
class PdfTemplateLayout:
    """
    Complete layout definition for one customer's invoice PDF template.

    Create one instance per customer in ``pdf_layouts/<customer>.py`` and
    register it in ``pdf_layouts/__init__.py``.
    """
    template_name: str                                       # filename in static/templates/
    header: HeaderCoords = field(default_factory=HeaderCoords)
    client: ClientCoords = field(default_factory=ClientCoords)
    items: ItemsCoords   = field(default_factory=ItemsCoords)
    totals: TotalsCoords = field(default_factory=TotalsCoords)


# ============================================================================
# Core engine — no customer names, no defaults beyond Python type hints
# ============================================================================

def generate_invoice_pdf(
    document,
    *,
    layout: PdfTemplateLayout,
    currency: str = "L",
    tax_rate: float = 0.15,
    include_tax: bool = True,
    seller_name: str = "ADMIN",
):
    """
    Overlay invoice data on ``layout.template_name`` and return ``(bytes, filename)``.

    Parameters
    ----------
    document     : Document ORM instance
    layout       : PdfTemplateLayout for this customer (required, no default)
    currency     : Currency symbol printed next to amounts
    tax_rate     : Decimal rate (0.15 = 15 %)
    include_tax  : Whether to add tax to the displayed total
    seller_name  : Name printed in the seller field
    """
    client = Contact.query.get(document.client_id) if document.client_id else None

    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    for item in document_items:
        item.inventory_item = (
            InventoryItem.query.get(item.inventory_item_id)
            if item.inventory_item_id else None
        )

    template_path = os.path.join(
        current_app.static_folder, "templates", layout.template_name
    )
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"PDF template not found: {template_path!r}")

    template_pdf = PdfReader(template_path)

    try:
        font_dir = os.path.join(current_app.static_folder, "fonts")
        pdfmetrics.registerFont(TTFont("Arial",      os.path.join(font_dir, "arial.ttf")))
        pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(font_dir, "arial-bold.ttf")))
        font_name, font_bold = "Arial", "Arial-Bold"
    except Exception:
        font_name, font_bold = "Helvetica", "Helvetica-Bold"

    _width, height = A4
    items_per_page = layout.items.items_per_page
    total_pages = math.ceil(len(document_items) / items_per_page) or 1
    output_pdf = PdfWriter()

    total_amount = float(document.total_amount or 0)
    subtotal     = round(total_amount / (1 + tax_rate), 2)
    imp_15       = round(subtotal * tax_rate, 2) if include_tax else 0.0
    total_final  = round(total_amount, 2) if include_tax else subtotal

    tax_data = {
        "vta_exenta":       subtotal,
        "venta_gravada_15": subtotal,
        "venta_gravada_18": 0.0,
        "venta_exonerada":  0.0,
        "imp_15":           imp_15,
        "imp_18":           0.0,
        "total_final":      total_final,
    }

    def number_to_words(amount: float) -> str:
        return num2words(round(amount, 2), lang="es")

    for page_num in range(total_pages):
        page_items = document_items[
            page_num * items_per_page : (page_num + 1) * items_per_page
        ]

        template_page  = copy.deepcopy(template_pdf.pages[0])
        overlay_buffer = BytesIO()
        c = canvas.Canvas(overlay_buffer, pagesize=A4)

        _draw_header(c, document, page_num, total_pages, height,
                     font_name, font_bold, seller_name, layout.header)
        _draw_client_info(c, client, height, font_name, layout.client)
        _draw_items(c, page_items, height, font_name, currency, layout.items)

        if page_num == total_pages - 1:
            _draw_totals(c, tax_data, number_to_words, height,
                         font_name, font_bold, currency, layout.totals)

        c.save()
        overlay_buffer.seek(0)
        overlay_pdf = PdfReader(overlay_buffer)
        template_page.merge_page(overlay_pdf.pages[0])
        output_pdf.add_page(template_page)
        overlay_buffer.close()

    doc_type = "quo" if document.type == DocumentType.quote else "inv"
    filename  = f"{doc_type}_{document.document_number}.pdf"

    output_buffer = BytesIO()
    output_pdf.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer.getvalue(), filename


# ============================================================================
# Private drawing helpers
# ============================================================================

def _draw_header(c, document, page_num, total_pages, height,
                 font_name, font_bold, seller_name, coords: HeaderCoords):
    h = coords
    doc_label = (
        _("COTIZACIÓN") + ":" if document.type == DocumentType.quote else _("FACTURA") + ":"
    )

    rx, r_off, rw, rh = h.whiteout_rect
    c.setFont(font_bold, h.title_font_size)
    c.setFillColorRGB(1, 1, 1)
    c.rect(rx, height - r_off, rw, rh, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)

    c.drawString(h.doc_type_x,   height - h.doc_type_y_from_top,   doc_label)
    c.drawString(h.doc_number_x, height - h.doc_number_y_from_top, str(document.document_number))

    c.setFont(font_name, h.detail_font_size)
    c.drawString(h.page_current_x, height - h.page_y_from_top, str(page_num + 1))
    c.drawString(h.page_total_x,   height - h.page_y_from_top, str(total_pages))

    if document.issued_date:
        c.drawString(h.issued_date_x, height - h.issued_date_y_from_top,
                     document.issued_date.strftime("%d/%m/%Y"))

    if document.due_date:
        if document.type == DocumentType.quote:
            c.drawString(h.due_date_x, height - h.due_date_y_from_top,
                         document.due_date.strftime("%d/%m/%Y"))
        else:
            payment_condition = (
                _(PaymentMethod(document.payments.first().method).value)
                if document.payments and document.payments.first()
                else _("N/A")
            )
            c.drawString(h.due_date_x, height - h.payment_condition_y_from_top,
                         payment_condition)

    c.drawString(h.company_id_x, height - h.company_id_y_from_top, f"{document.company_id:04d}")
    c.drawString(h.seller_x,     height - h.seller_y_from_top,     seller_name[:20])


def _draw_client_info(c, client, height, font_name, coords: ClientCoords):
    cl = coords
    c.setFont(font_name, cl.font_size)
    y = height - cl.block_y_from_top

    if client:
        c.drawString(cl.x, y,                   client.name[:55])
        c.drawString(cl.x, y - cl.line_gap,     client.identifier or "")
        c.drawString(cl.x, y - cl.line_gap * 2, f"CLI-{client.id:04d}")
        if client.address:
            c.drawString(cl.x, y - cl.line_gap * 3, client.address[:40])
    else:
        c.drawString(cl.fallback_x, y,                   _("CLIENTE GENERAL"))
        c.drawString(cl.fallback_x, y - cl.line_gap * 2, "CLI-0000")


def _draw_items(c, page_items, height, font_name, currency, coords: ItemsCoords):
    it = coords
    c.setFont(font_name, it.font_size)
    y_start = height - it.y_start_from_top

    for i, item in enumerate(page_items):
        y = y_start - (i * it.row_height)

        codigo   = str(item.inventory_item_id) if item.inventory_item_id else f"ART-{item.id}"
        articulo = (
            item.inventory_item.name if item.inventory_item
            else (item.description or _("Artículo personalizado"))
        )
        discount   = float(item.unit_price or 0) * float(item.discount or 0) / 100
        total_item = float(item.quantity or 0) * float(item.unit_price or 0) - discount * float(item.quantity or 0)

        c.drawString(it.col_codigo,   y, codigo[:it.max_codigo_chars])
        c.drawString(it.col_articulo, y, articulo[:it.max_articulo_chars])
        c.drawRightString(it.col_cantidad  + it.col_cantidad_offset,  y, str(item.quantity or 0))
        c.drawRightString(it.col_precio    + it.col_precio_offset,    y, f"{currency}{float(item.unit_price or 0):,.2f}")
        c.drawRightString(it.col_descuento + it.col_descuento_offset, y, f"{currency}{discount:,.2f}")
        c.drawRightString(it.col_valor     + it.col_valor_offset,     y, f"{currency}{total_item:,.2f}")


def _draw_totals(c, tax_data, number_to_words, height, font_name, font_bold, currency,
                 coords: TotalsCoords):
    tot = coords
    c.setFont(font_name, tot.font_size)
    anchor_y = height - tot.y_anchor_from_top
    rx = tot.x + tot.right_x_offset

    c.drawRightString(rx, anchor_y - tot.row_exenta,     f"{currency}{tax_data['vta_exenta']:,.2f}")
    c.drawRightString(rx, anchor_y - tot.row_gravada_15, f"{currency}{tax_data['venta_gravada_15']:,.2f}")
    c.drawRightString(rx, anchor_y - tot.row_gravada_18, f"{currency}{tax_data['venta_gravada_18']:,.2f}")
    c.drawRightString(rx, anchor_y - tot.row_exonerada,  f"{currency}{tax_data['venta_exonerada']:,.2f}")
    c.drawRightString(rx, anchor_y - tot.row_imp_15,     f"{currency}{tax_data['imp_15']:,.2f}")
    c.drawRightString(rx, anchor_y - tot.row_imp_18,     f"{currency}{tax_data['imp_18']:,.2f}")

    c.setFont(font_bold, tot.total_font_size)
    c.drawRightString(rx, anchor_y - tot.row_total, f"{currency}{tax_data['total_final']:,.2f}")

    c.setFont(font_name, tot.words_font_size)
    words = number_to_words(tax_data["total_final"])
    c.drawString(tot.x + tot.words_x_offset, anchor_y - tot.words_y_offset,
                 words[:tot.max_words_chars])


# ============================================================================
# Backward-compat wrapper — keeps routes.py untouched
# ============================================================================

def generate_invoice_pdf_from_request(document, request, session, current_user):
    """
    Used by the existing invoice route.  Resolves the layout automatically
    from the company ID via the layout registry.
    Script callers should use generate_invoice_pdf() directly.
    """
    from app.invoices.services.pdf_layouts import get_layout

    tax_param   = request.args.get("tax", "1")
    include_tax = tax_param != "0"
    try:
        tax_rate = float(session.get("tax_rate", 15)) / 100
    except (TypeError, ValueError):
        tax_rate = 0.15

    currency    = session.get("currency", "L")
    seller      = current_user.name if current_user and current_user.name else "ADMIN"
    layout      = get_layout(document.company_id)

    return generate_invoice_pdf(
        document,
        layout=layout,
        currency=currency,
        tax_rate=tax_rate,
        include_tax=include_tax,
        seller_name=seller,
    )