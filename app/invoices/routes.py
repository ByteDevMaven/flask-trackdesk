import os, math, copy, uuid
from io import BytesIO

from flask import render_template, request, redirect, session, url_for, flash, current_app, make_response
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from flask_babel import _, get_locale
from sqlalchemy import or_
from datetime import datetime
from wtforms import ValidationError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
from num2words import num2words

from extensions import limiter

from models import db, Document, DocumentItem, Client, InventoryItem, DocumentType, Payment, PaymentMethod

from . import invoices

@invoices.route('/<int:company_id>/invoices')
@login_required
@limiter.exempt
def index(company_id):
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    doc_type = request.args.get('type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Base query - now includes both invoices and quotes
    query = db.session.query(Document).filter(
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    )
    
    # Apply filters
    if search:
        query = query.outerjoin(Client, Document.client_id == Client.id).filter(
            or_(
                Document.document_number.ilike(f'%{search}%'),
                Client.name.ilike(f'%{search}%')
            )
        )
    
    if status:
        query = query.filter(Document.status == status)
    
    if doc_type:
        if doc_type == 'invoice':
            query = query.filter(Document.type == DocumentType.invoice)
        elif doc_type == 'quote':
            query = query.filter(Document.type == DocumentType.quote)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Document.issued_date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(Document.issued_date <= date_to_obj)
        except ValueError:
            pass
    
    # Order by creation date (newest first)
    query = query.order_by(Document.id.desc())
    
    # Paginate
    pagination = query.paginate( # type: ignore
        page=page, 
        per_page=int(current_app.config.get('ITEMS_PER_PAGE', 20)),
        error_out=False
    )
    
    documents = pagination.items
    
    # Get client information for each document
    for document in documents:
        if document.client_id:
            document.client = Client.query.get(document.client_id)
        else:
            document.client = None
    
    return render_template('invoices/index.html', 
                         invoices=documents, 
                         pagination=pagination)


@invoices.route('/invoices/item-row', methods=['POST'])
@login_required
@limiter.exempt
def item_row():
    index = int(request.form.get('index', 0))
    csrf_token = request.form.get("csrf_token") 

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login")) 

    inventory_items = InventoryItem.query.filter(
        InventoryItem.company_id == session.get('selected_company_id'),
        InventoryItem.quantity > 0
    ).all()
    
    return render_template('invoices/item_row.html', index=index, inventory_items=inventory_items)


@invoices.route('/<int:company_id>/invoices/create')
@login_required
@limiter.exempt
def create(company_id):
    # Get clients and inventory items for the form
    clients = Client.query.filter_by(company_id=company_id).all()
    inventory_items = InventoryItem.query.filter(
        InventoryItem.company_id == company_id,
        InventoryItem.quantity > 0
    ).all()

    selected_client_id = int(request.args.get('client_id', 0))
    selected_type = request.args.get('type', None)

    return render_template('invoices/form.html',
                         customer_id=selected_client_id, 
                         doc_type=selected_type,
                         invoice=None, 
                         clients=clients, 
                         inventory_items=inventory_items,
                         document_items=None)

@invoices.route('/<int:company_id>/invoices/store', methods=['POST'])
@login_required
@limiter.exempt
def store(company_id):
    csrf_token = request.form.get("csrf_token") 

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login")) 
    
    try:
        # Get document type from form
        doc_type_str = request.form.get('type', 'invoice')
        doc_type = DocumentType[doc_type_str]  # safer for enum use

        # Generate document_number if not provided
        document_number = request.form.get('document_number')
        if not document_number:
            company_id_str = str(company_id)

            # Single-letter type prefix
            type_letter = 'I' if doc_type == DocumentType.invoice else 'Q'

            # Prefix pattern
            prefix = f"{type_letter}-{company_id_str}-"

            # Find the last document for this company (any type)
            last_doc = Document.query.filter(
                Document.company_id == company_id,
                Document.document_number.like(f"%-{company_id_str}-%")
            ).order_by(Document.id.desc()).first()

            if last_doc:
                try:
                    last_seq = int(last_doc.document_number.split('-')[-1])
                except ValueError:
                    last_seq = 0
            else:
                last_seq = 0

            document_number = f"{prefix}{last_seq + 1:06d}"

        # Create the document
        document = Document(
            company_id=company_id, # type: ignore
            document_number=document_number, # type: ignore
            type=doc_type, # type: ignore
            client_id=int(request.form.get('client_id')) if request.form.get('client_id') else None, # type: ignore
            user_id=current_user.id, # type: ignore
            status=request.form.get('status', 'draft'), # type: ignore
            issued_date=datetime.strptime(request.form.get('issued_date'), '%Y-%m-%d') if request.form.get('issued_date') else datetime.now(), # type: ignore
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else None # type: ignore
        )

        db.session.add(document)
        db.session.flush()  # Get the document ID
        
        # Process items
        total_amount = 0
        items_data = {}
        
        # Parse form data for items
        for key, value in request.form.items():
            if key.startswith('items[') and '][' in key:
                # Extract index and field name
                parts = key.split('][')
                index = parts[0].split('[')[1]
                field = parts[1].rstrip(']')
                
                if index not in items_data:
                    items_data[index] = {}
                items_data[index][field] = value
        
        # Create document items
        for item_data in items_data.values():
            if item_data.get('inventory_item_id') or item_data.get('description'):
                quantity = int(item_data.get('quantity', 0)) if item_data.get('quantity') else 0
                unit_price = float(item_data.get('unit_price', 0)) if item_data.get('unit_price') else 0
                discount = float(item_data.get('discount', 0)) if item_data.get('discount') else 0

                inventory_item_id = item_data.get('inventory_item_id')
                if inventory_item_id:
                    inventory_item = InventoryItem.query.get(int(inventory_item_id))
                    if inventory_item and doc_type == DocumentType.invoice:
                        # Decrease inventory quantity
                        inventory_item.quantity = int(inventory_item.quantity or 0) - int(quantity)
                        if inventory_item.quantity < 0:
                            inventory_item.quantity = 0

                document_item = DocumentItem(
                    document_id=document.id, # type: ignore
                    inventory_item_id=int(inventory_item_id) if inventory_item_id else None, # type: ignore
                    description=item_data.get('description', ''), # type: ignore
                    quantity=quantity, # type: ignore
                    unit_price=unit_price, # type: ignore
                    discount=discount # type: ignore
                )

                db.session.add(document_item)
                item_total = quantity * unit_price
                item_discount = item_total * (discount / 100)
                total_amount += item_total - item_discount

        tax_rate = session.get('tax_rate', 0)  # Get tax rate from session
        multiplier = 1 + tax_rate / 100
        # current_app.logger.info(f"Multiplier: {multiplier}")
        final_total = round(total_amount * multiplier, 2)
        document.total_amount = final_total

        if document.status == 'paid':
            payment = Payment(
            company_id=company_id, # type: ignore
            document_id=document.id, # type: ignore
            amount=document.total_amount, # type: ignore
            payment_date=datetime.now(), # type: ignore
            method=PaymentMethod.cash, # type: ignore
            notes=request.form.get('notes', '') # type: ignore
            )
            
            db.session.add(payment)
        
        db.session.commit()
        
        doc_type_name = _('Invoice') if doc_type == DocumentType.invoice else _('Quote')
        flash(_(f'{doc_type_name} created successfully'), 'success')
        return redirect(url_for('invoices.view', company_id=company_id, id=document.id))
        
    except Exception as e:
        db.session.rollback()
        flash(_('Error creating document: %(error)s', error=str(e)), 'error')
        return redirect(url_for('invoices.create', company_id=company_id))

@invoices.route('/<int:company_id>/invoices/<int:id>')
@login_required
@limiter.exempt
def view(company_id, id):
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
    # Get client information
    if document.client_id:
        document.client = Client.query.get(document.client_id)
    else:
        document.client = None
    
    # Get document items with inventory information
    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    for item in document_items:
        if item.inventory_item_id:
            item.inventory_item = InventoryItem.query.get(item.inventory_item_id)
        else:
            item.inventory_item = None
    
    return render_template('invoices/view.html', 
                         invoice=document, 
                         document_items=document_items)

@invoices.route('/<int:company_id>/invoices/<int:id>/edit')
@login_required
@limiter.exempt
def edit(company_id, id):
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
    # Get client information
    if document.client_id:
        document.client = Client.query.get(document.client_id)
    else:
        document.client = None
    
    clients = Client.query.filter_by(company_id=company_id).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).all()
    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    
    # Get inventory information for each document item
    for item in document_items:
        if item.inventory_item_id:
            item.inventory_item = InventoryItem.query.get(item.inventory_item_id)
        else:
            item.inventory_item = None
    
    return render_template('invoices/form.html', 
                         invoice=document, 
                         clients=clients, 
                         inventory_items=inventory_items,
                         document_items=document_items)

@invoices.route('/<int:company_id>/invoices/<int:id>/update', methods=['POST'])
@login_required
@limiter.exempt
def update(company_id, id):
    csrf_token = request.form.get("csrf_token") 

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login")) 
    
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
    try:
        # Get the new document type from form
        doc_type_str = request.form.get('type', 'invoice')
        new_doc_type = DocumentType.invoice if doc_type_str == 'invoice' else DocumentType.quote

        # Check if the type changed or document_number is missing
        if new_doc_type != document.type or not request.form.get('document_number'):
            company_id_str = str(company_id)
            type_letter = 'I' if new_doc_type == DocumentType.invoice else 'Q'

            # Keep the same sequence if the old document_number exists
            if document.document_number:
                try:
                    seq_num = int(document.document_number.split('-')[-1])
                except ValueError:
                    seq_num = None
            else:
                seq_num = None

            if seq_num is not None:
                # Keep sequence, just change type letter
                new_number = f"{type_letter}-{company_id_str}-{seq_num:06d}"

                # Check if another document already has this number
                exists = Document.query.filter(
                    Document.company_id == company_id,
                    Document.type == new_doc_type,
                    Document.document_number == new_number,
                    Document.id != document.id
                ).first()
                if exists:
                    raise ValueError(_("Document number already exists for this type"))
                
                document.document_number = new_number
            else:
                # No valid existing sequence → generate new
                last_doc = Document.query.filter(
                    Document.company_id == company_id,
                    Document.type == new_doc_type
                ).order_by(Document.id.desc()).first()

                if last_doc:
                    try:
                        last_seq = int(last_doc.document_number.split('-')[-1])
                    except ValueError:
                        last_seq = 0
                else:
                    last_seq = 0

                document.document_number = f"{type_letter}-{company_id_str}-{last_seq + 1:06d}"
        else:
            # Keep manually provided or existing number
            document.document_number = request.form.get('document_number', document.document_number)

        # Update core document fields
        document.type = new_doc_type
        document.client_id = int(request.form.get('client_id')) if request.form.get('client_id') else None # type: ignore
        document.status = request.form.get('status', document.status)
        document.issued_date = datetime.strptime(request.form.get('issued_date'), '%Y-%m-%d') if request.form.get('issued_date') else document.issued_date # type: ignore
        document.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else document.due_date # type: ignore

        # Delete existing items
        DocumentItem.query.filter_by(document_id=document.id).delete()

        # Process new items
        total_amount = 0
        items_data = {}

        # Parse form data for items
        for key, value in request.form.items():
            if key.startswith('items[') and '][' in key:
                parts = key.split('][')
                index = parts[0].split('[')[1]
                field = parts[1].rstrip(']')
                
                if index not in items_data:
                    items_data[index] = {}
                items_data[index][field] = value

        # Create new document items
        for item_data in items_data.values():
            if item_data.get('inventory_item_id') or item_data.get('description'):
                quantity = int(item_data.get('quantity', 0)) if item_data.get('quantity') else 0
                unit_price = float(item_data.get('unit_price', 0)) if item_data.get('unit_price') else 0
                discount = float(item_data.get('discount', 0)) if item_data.get('discount') else 0

                document_item = DocumentItem(
                    document_id=document.id, # type: ignore
                    inventory_item_id=int(item_data.get('inventory_item_id')) if item_data.get('inventory_item_id') else None, # type: ignore
                    description=item_data.get('description', ''), # type: ignore
                    quantity=quantity, # type: ignore
                    unit_price=unit_price, # type: ignore
                    discount=discount # type: ignore
                )

                db.session.add(document_item)
                item_total = quantity * unit_price
                item_discount = item_total * (discount / 100)
                total_amount += item_total - item_discount

        tax_rate = session.get('tax_rate', 0)
        multiplier = 1 + tax_rate / 100
        final_total = round(total_amount * multiplier, 2)
        document.total_amount = final_total

        db.session.commit()

        doc_type_name = _('Invoice') if new_doc_type == DocumentType.invoice else _('Quote')
        flash(doc_type_name + ' ' + _('updated successfully'), 'success')
        return redirect(url_for('invoices.view', company_id=company_id, id=document.id))

    except Exception as e:
        db.session.rollback()
        flash(_('Error updating document: %(error)s', error=str(e)), 'error')
        return redirect(url_for('invoices.edit', company_id=company_id, id=id))

@invoices.route('/<int:company_id>/invoices/<int:id>/delete', methods=['POST'])
@login_required
def delete(company_id, id):
    csrf_token = request.form.get("csrf_token") 

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login")) 
    
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
    try:
        # Delete related items first
        DocumentItem.query.filter_by(document_id=document.id).delete()
        
        # Delete the document
        db.session.delete(document)
        db.session.commit()
        
        doc_type_name = _('Invoice') if document.type == DocumentType.invoice else _('Quote')
        flash(_(f'{doc_type_name} deleted successfully'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Error deleting document: %(error)s', error=str(e)), 'error')
    
    return redirect(url_for('invoices.index', company_id=company_id))

@invoices.route('/<int:company_id>/invoices/<int:id>/convert', methods=['POST'])
@login_required
@limiter.exempt
def convert_to_invoice(company_id, id):
    csrf_token = request.form.get("csrf_token") 

    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash(_("Invalid CSRF token. Please try again."), "error")
        return redirect(url_for("auth.login")) 
    
    # Get the quote
    quote = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        Document.type == DocumentType.quote
    ).first_or_404()
    
    try:
        # Generate new invoice number
        last_invoice = Document.query.filter(
            Document.company_id == company_id,
            Document.type == DocumentType.invoice
        ).order_by(Document.id.desc()).first()
        
        if last_invoice and last_invoice.document_number:
            try:
                last_num = int(last_invoice.document_number.split('-')[-1])
                invoice_number = f"INV-{last_num + 1:06d}"
            except:
                invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        else:
            invoice_number = "INV-000001"
        
        # Create new invoice based on quote
        invoice = Document(
            company_id=company_id, # type: ignore
            document_number=invoice_number, # type: ignore
            type=DocumentType.invoice, # type: ignore
            client_id=quote.client_id, # type: ignore
            user_id=current_user.id, # type: ignore
            status='draft', # type: ignore
            issued_date=datetime.now(), # type: ignore
            due_date=quote.due_date, # type: ignore
            total_amount=quote.total_amount # type: ignore
        )
        
        db.session.add(invoice)
        db.session.flush()
        
        # Copy items from quote to invoice
        quote_items = DocumentItem.query.filter_by(document_id=quote.id).all()
        for item in quote_items:
            invoice_item = DocumentItem(
                document_id=invoice.id, # type: ignore
                inventory_item_id=item.inventory_item_id, # type: ignore
                description=item.description, # type: ignore
                quantity=item.quantity, # type: ignore
                unit_price=item.unit_price # type: ignore
            )
            db.session.add(invoice_item)
        
        # Update quote status to converted
        quote.status = 'converted'
        
        db.session.commit()
        flash(_('Quote converted to invoice successfully'), 'success')
        return redirect(url_for('invoices.view', company_id=company_id, id=invoice.id))
        
    except Exception as e:
        db.session.rollback()
        flash(_('Error converting quote: %(error)s', error=str(e)), 'error')
        return redirect(url_for('invoices.view', company_id=company_id, id=id))

@invoices.route('/<int:company_id>/invoices/<int:id>/print')
@login_required
@limiter.exempt
def print_invoice(company_id, id):
    """
    Generate and return an invoice/quote PDF.
    Includes multi-page support, client data, item rows, totals,
    and localized number-to-words conversion.
    """

    # -------------------------
    # Fetch document & related data
    # -------------------------
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()

    client = Client.query.get(document.client_id) if document.client_id else None

    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    for item in document_items:
        item.inventory_item = (
            InventoryItem.query.get(item.inventory_item_id)
            if item.inventory_item_id else None
        )

    try:
        # -------------------------
        # Template setup
        # -------------------------
        template_path = os.path.join(current_app.static_folder, "templates", "Factura Ferre-lagos.pdf") # type: ignore
        if not os.path.exists(template_path):
            flash(_("PDF template not found. Please contact administrator."), "error")
            return redirect(url_for("invoices.view", company_id=company_id, id=id))

        template_pdf = PdfReader(template_path)

        # Fonts
        try:
            font_dir = os.path.join(current_app.static_folder, "fonts") # type: ignore
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
        # Totals calculation
        # -------------------------

        tax_param = request.args.get("tax", "1")  # default = include tax
        include_tax = tax_param != "0"
        tax_rate = session.get("tax_rate", 15) / 100

        total_amount = document.total_amount or 0
        subtotal = round(total_amount / (1 + tax_rate), 2)
        vta_exenta = subtotal
        venta_gravada_15 = subtotal * 0.6
        venta_gravada_18 = 0
        venta_exonerada = 0
        imp_15 = round(subtotal * tax_rate, 2) if include_tax else 0
        imp_18 = 0
        total_final = round(total_amount, 2) if include_tax else subtotal

        # Number to words
        def number_to_words(amount):
            lang_code = get_locale().language # type: ignore
            return num2words(round(amount, 2), lang=lang_code)

        # -------------------------
        # Loop per page
        # -------------------------
        for page_num in range(total_pages):
            page_items = document_items[page_num * items_per_page : (page_num + 1) * items_per_page]
            template_page = copy.deepcopy(template_pdf.pages[0])

            overlay_buffer = BytesIO()
            c = canvas.Canvas(overlay_buffer, pagesize=A4)
            c.setFillColorRGB(0, 0, 0)

            # 🔹 HEADER
            draw_header(c, document, page_num, total_pages, width, height, font_name, font_bold)

            # 🔹 CLIENT INFO
            draw_client_info(c, client, document, height, font_name)

            # 🔹 ITEMS
            draw_items(c, page_items, height, font_name)

            # 🔹 TOTALS (last page only)
            if page_num == total_pages - 1:
                draw_totals(c, subtotal, vta_exenta, venta_gravada_15, venta_gravada_18,
                            venta_exonerada, imp_15, imp_18, total_final, number_to_words, height,
                            font_name, font_bold)

            c.save()
            overlay_buffer.seek(0)

            overlay_pdf = PdfReader(overlay_buffer)
            template_page.merge_page(overlay_pdf.pages[0])
            output_pdf.add_page(template_page)
            overlay_buffer.close()

        # -------------------------
        # Output response
        # -------------------------
        doc_type_name = "quo" if document.type == DocumentType.quote else "inv"
        filename = f"{doc_type_name}_{document.document_number}.pdf"
        output_buffer = BytesIO()
        output_pdf.add_metadata({"/Title": filename})
        output_pdf.write(output_buffer)
        output_buffer.seek(0)

        response = make_response(output_buffer.getvalue())
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'inline; filename="{filename}"'
        output_buffer.close()
        return response

    except Exception as e:
        flash(_(f"Error generating PDF: {str(e)}"), "error")
        return redirect(url_for("invoices.view", company_id=company_id, id=id))


# -------------------------------------------------
# 🔹 HELPER DRAWING FUNCTIONS
# -------------------------------------------------
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