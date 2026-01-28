import os, math, copy
from io import BytesIO

from flask import current_app, session
from flask_login import current_user
from flask_babel import _, get_locale

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
from num2words import num2words

from models import (
    DocumentItem, Client, InventoryItem,
    DocumentType, PaymentMethod
)


def generate_invoice_pdf(document, request):
    client = Client.query.get(document.client_id) if document.client_id else None

    document_items = DocumentItem.query.filter_by(
        document_id=document.id
    ).all()

    for item in document_items:
        item.inventory_item = (
            InventoryItem.query.get(item.inventory_item_id)
            if item.inventory_item_id else None
        )

    template_path = os.path.join(
        current_app.static_folder,
        "templates",
        "Factura Ferre-lagos.pdf"
    )

    if not os.path.exists(template_path):
        raise FileNotFoundError(_("PDF template not found"))

    template_pdf = PdfReader(template_path)

    # Fonts
    try:
        font_dir = os.path.join(current_app.static_folder, "fonts")
        pdfmetrics.registerFont(TTFont("Arial", os.path.join(font_dir, "arial.ttf")))
        pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(font_dir, "arial-bold.ttf")))
        font_name, font_bold = "Arial", "Arial-Bold"
    except Exception:
        font_name, font_bold = "Helvetica", "Helvetica-Bold"

    # -------------------------
    # Pagination
    # -------------------------
    width, height = A4
    items_per_page = 25
    total_pages = math.ceil(len(document_items) / items_per_page) or 1
    output_pdf = PdfWriter()

    # -------------------------
    # Totals
    # -------------------------
    tax_param = request.args.get("tax", "1")
    include_tax = tax_param != "0"
    tax_rate = session.get("tax_rate", 15) / 100

    total_amount = document.total_amount or 0
    subtotal = round(total_amount / (1 + tax_rate), 2)

    vta_exenta = subtotal
    venta_gravada_15 = subtotal #* 0.6
    venta_gravada_18 = 0
    venta_exonerada = 0
    imp_15 = round(subtotal * tax_rate, 2) if include_tax else 0
    imp_18 = 0
    total_final = round(total_amount, 2) if include_tax else subtotal

    def number_to_words(amount):
        return num2words(
            round(amount, 2),
            lang=get_locale().language
        )

    # -------------------------
    # Page loop
    # -------------------------
    for page_num in range(total_pages):
        page_items = document_items[
            page_num * items_per_page:(page_num + 1) * items_per_page
        ]

        template_page = copy.deepcopy(template_pdf.pages[0])

        overlay_buffer = BytesIO()
        c = canvas.Canvas(overlay_buffer, pagesize=A4)

        draw_header(c, document, page_num, total_pages, width, height, font_name, font_bold)
        draw_client_info(c, client, document, height, font_name)
        draw_items(c, page_items, height, font_name)

        if page_num == total_pages - 1:
            draw_totals(
                c,
                subtotal,
                vta_exenta,
                venta_gravada_15,
                venta_gravada_18,
                venta_exonerada,
                imp_15,
                imp_18,
                total_final,
                number_to_words,
                height,
                font_name,
                font_bold
            )

        c.save()
        overlay_buffer.seek(0)

        overlay_pdf = PdfReader(overlay_buffer)
        template_page.merge_page(overlay_pdf.pages[0])
        output_pdf.add_page(template_page)
        overlay_buffer.close()

    # -------------------------
    # Output
    # -------------------------
    doc_type = "quo" if document.type == DocumentType.quote else "inv"
    filename = f"{doc_type}_{document.document_number}.pdf"

    output_buffer = BytesIO()
    output_pdf.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer.getvalue(), filename

def draw_header(c, document, page_num, total_pages, width, height, font_name, font_bold):
    """Draw document header info."""
    doc_type = _("COTIZACIÓN") + ":" if document.type == DocumentType.quote else _("FACTURA") + ":"
    c.setFont(font_bold, 11)
    c.setFillColorRGB(1, 1, 1)
    c.rect(10, height - 135, 120, 17, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(12, height - 130, doc_type)
    c.drawString(140, height - 130, f"{document.document_number}")

    c.setFont(font_name, 9)
    c.drawString(49, height - 110, str(page_num + 1))
    c.drawString(70, height - 110, str(total_pages))

    if document.issued_date:
        c.drawString(480, height - 156, document.issued_date.strftime("%d/%m/%Y"))

    if document.due_date:
        if document.type == DocumentType.quote:
            c.drawString(480, height - 172, document.due_date.strftime("%d/%m/%Y"))
        else:
            payment_condition = (
                _(PaymentMethod(document.payments.first().method).value)
                if document.payments and document.payments.first()
                else _("N/A")
            )
            c.drawString(480, height - 172, payment_condition)

    c.drawString(480, height - 187, f"{document.company_id:04d}")
    seller_name = current_user.name if current_user and current_user.name else "ADMIN"
    c.drawString(480, height - 202, seller_name[:20])


def draw_client_info(c, client, document, height, font_name):
    """Draw client information."""
    c.setFont(font_name, 10)
    y = height - 155
    if client:
        c.drawString(140, y, client.name[:55])
        c.drawString(140, y - 15, client.identifier or "")
        c.drawString(140, y - 30, f"CLI-{client.id:04d}")
        if client.address:
            c.drawString(140, y - 45, client.address[:40])
    else:
        c.drawString(100, y, _("CLIENTE GENERAL"))
        c.drawString(100, y - 20, "")
        c.drawString(100, y - 40, "CLI-0000")
        c.drawString(100, y - 60, "")


def draw_items(c, page_items, height, font_name):
    """Draw invoice/quote items."""
    c.setFont(font_name, 8)
    y_start = height - 260
    row_height = 15
    col_codigo, col_articulo, col_cantidad, col_precio, col_descuento, col_valor = 30, 110, 280, 350, 430, 480

    for i, item in enumerate(page_items):
        y = y_start - (i * row_height)
        codigo = str(item.inventory_item_id) if item.inventory_item_id else f"ART-{item.id}"
        articulo = (
            item.inventory_item.name if item.inventory_item else (item.description or _("Artículo personalizado"))
        )
        discount = (item.unit_price * item.discount / 100 if item.discount else 0)
        total_item = (item.quantity or 0) * (item.unit_price or 0) - discount * (item.quantity or 0)

        c.drawString(col_codigo, y, codigo[:8])
        c.drawString(col_articulo, y, articulo[:25])
        c.drawRightString(col_cantidad + 10, y, str(item.quantity or 0))
        c.drawRightString(col_precio + 35, y, f"{session['currency']}{item.unit_price or 0:,.2f}")
        c.drawRightString(col_descuento + 35, y, f"{session['currency']}{discount:,.2f}")
        c.drawRightString(col_valor + 65, y, f"{session['currency']}{total_item:,.2f}")


def draw_totals(c, subtotal, vta_exenta, gravada15, gravada18, exonerada,
                imp15, imp18, total_final, number_to_words, height, font_name, font_bold):
    """Draw totals (only on last page)."""
    c.setFont(font_name, 9)
    totals_start_y, x = height - 650, 480
    c.drawRightString(x + 50, totals_start_y - 27, f"{session['currency']}{vta_exenta:,.2f}")
    c.drawRightString(x + 50, totals_start_y - 45, f"{session['currency']}{gravada15:,.2f}")
    c.drawRightString(x + 50, totals_start_y - 65, f"{session['currency']}{gravada18:,.2f}")
    c.drawRightString(x + 50, totals_start_y - 82, f"{session['currency']}{exonerada:,.2f}")
    c.drawRightString(x + 50, totals_start_y - 100, f"{session['currency']}{imp15:,.2f}")
    c.drawRightString(x + 50, totals_start_y - 117, f"{session['currency']}{imp18:,.2f}")

    c.setFont(font_bold, 11)
    c.drawRightString(x + 50, totals_start_y - 145, f"{session['currency']}{total_final:,.2f}")

    c.setFont(font_name, 10)
    words = number_to_words(total_final)
    c.drawString(x - 160, totals_start_y - 180, words[:70])