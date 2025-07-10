import uuid
import os
from io import BytesIO

from flask import render_template, request, redirect, url_for, flash, current_app, make_response
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from flask_babel import _, get_locale
from sqlalchemy import or_
from datetime import datetime
from wtforms import ValidationError

from models import db, Document, DocumentItem, Client, InventoryItem, DocumentType

from . import invoices

@invoices.route('/<int:company_id>/invoices')
@login_required
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
    query = query.order_by(Document.issued_date.desc())
    
    # Paginate
    pagination = query.paginate(
        page=page, 
        per_page=current_app.config.get('ITEMS_PER_PAGE', 20),
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

@invoices.route('/<int:company_id>/invoices/create')
@login_required
def create(company_id):
    # Get clients and inventory items for the form
    clients = Client.query.filter_by(company_id=company_id).all()
    inventory_items = InventoryItem.query.filter_by(company_id=company_id).all()

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
        doc_type = DocumentType.invoice if doc_type_str == 'invoice' else DocumentType.quote
        
        # Generate document number if not provided
        document_number = request.form.get('document_number')
        if not document_number:
            # Generate a unique document number based on type
            prefix = "INV" if doc_type == DocumentType.invoice else "QUO"
            last_document = Document.query.filter(
                Document.company_id == company_id,
                Document.type == doc_type
            ).order_by(Document.id.desc()).first()
            
            if last_document and last_document.document_number:
                try:
                    last_num = int(last_document.document_number.split('-')[-1])
                    document_number = f"{prefix}-{last_num + 1:06d}"
                except:
                    document_number = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
            else:
                document_number = f"{prefix}-000001"
        
        # Create the document
        document = Document(
            company_id=company_id,
            document_number=document_number,
            type=doc_type,
            client_id=int(request.form.get('client_id')) if request.form.get('client_id') else None,
            user_id=current_user.id,
            status=request.form.get('status', 'draft'),
            issued_date=datetime.strptime(request.form.get('issued_date'), '%Y-%m-%d') if request.form.get('issued_date') else datetime.now(),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else None
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
                quantity = float(item_data.get('quantity', 0)) if item_data.get('quantity') else 0
                unit_price = float(item_data.get('unit_price', 0)) if item_data.get('unit_price') else 0
                
                document_item = DocumentItem(
                    document_id=document.id,
                    inventory_item_id=int(item_data.get('inventory_item_id')) if item_data.get('inventory_item_id') else None,
                    description=item_data.get('description', ''),
                    quantity=int(quantity),
                    unit_price=unit_price
                )
                
                db.session.add(document_item)
                total_amount += quantity * unit_price
        
        # Update document total
        document.total_amount = total_amount
        
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
        # Update document type if changed
        doc_type_str = request.form.get('type', 'invoice')
        new_doc_type = DocumentType.invoice if doc_type_str == 'invoice' else DocumentType.quote
        
        # Update document fields
        document.document_number = request.form.get('document_number', document.document_number)
        document.type = new_doc_type
        document.client_id = int(request.form.get('client_id')) if request.form.get('client_id') else None
        document.status = request.form.get('status', document.status)
        document.issued_date = datetime.strptime(request.form.get('issued_date'), '%Y-%m-%d') if request.form.get('issued_date') else document.issued_date
        document.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else document.due_date
        
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
                quantity = float(item_data.get('quantity', 0)) if item_data.get('quantity') else 0
                unit_price = float(item_data.get('unit_price', 0)) if item_data.get('unit_price') else 0
                
                document_item = DocumentItem(
                    document_id=document.id,
                    inventory_item_id=int(item_data.get('inventory_item_id')) if item_data.get('inventory_item_id') else None,
                    description=item_data.get('description', ''),
                    quantity=int(quantity),
                    unit_price=unit_price
                )
                
                db.session.add(document_item)
                total_amount += quantity * unit_price
        
        # Update document total
        document.total_amount = total_amount
        
        db.session.commit()
        
        doc_type_name = _('Invoice') if new_doc_type == DocumentType.invoice else _('Quote')
        flash(_(f'{doc_type_name} updated successfully'), 'success')
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

@invoices.route('/<int:company_id>/invoices/<int:id>/print')
@login_required
def print_invoice(company_id, id): 
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from PyPDF2 import PdfReader, PdfWriter
    from num2words import num2words

    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(Document.type == DocumentType.invoice, Document.type == DocumentType.quote)
    ).first_or_404()
    
    # Get client information
    client = None
    if document.client_id:
        client = Client.query.get(document.client_id)
    
    # Get document items with inventory information
    document_items = DocumentItem.query.filter_by(document_id=document.id).all()
    for item in document_items:
        if item.inventory_item_id:
            item.inventory_item = InventoryItem.query.get(item.inventory_item_id)
        else:
            item.inventory_item = None
    
    try:
        # Load the PDF template
        template_path = os.path.join(current_app.static_folder, 'templates', 'Factura Ferre-lagos.pdf')
        
        if not os.path.exists(template_path):
            flash(_('PDF template not found. Please contact administrator.'), 'error')
            return redirect(url_for('invoices.view', company_id=company_id, id=id))
        
        # Read the template PDF
        template_pdf = PdfReader(template_path)
        template_page = template_pdf.pages[0]
        
        # Create overlay with data
        overlay_buffer = BytesIO()
        overlay_canvas = canvas.Canvas(overlay_buffer, pagesize=A4)
        width, height = A4
        
        # Register fonts if available
        try:
            pdfmetrics.registerFont(TTFont('Arial', os.path.join(current_app.static_folder, 'fonts', 'arial.ttf')))
            pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(current_app.static_folder, 'fonts', 'arial-bold.ttf')))
            font_name = 'Arial'
            font_bold = 'Arial-Bold'
        except:
            font_name = 'Helvetica'
            font_bold = 'Helvetica-Bold'
        
        # Set transparent background for overlay
        overlay_canvas.setFillColorRGB(0, 0, 0)  # Black text
        
        # Document type and number
        doc_type = "COTIZACIÓN:" if document.type == DocumentType.quote else "FACTURA:"
        overlay_canvas.setFont(font_bold, 11)
    
        # Draw white background behind doc_type
        overlay_canvas.setFillColorRGB(1, 1, 1)  # White color
        overlay_canvas.rect(10, height - 135, 120, 17, fill=1, stroke=0)  # x, y, width, height

        # Draw the doc_type text on top (e.g., FACTURA / COTIZACIÓN)
        overlay_canvas.setFillColorRGB(0, 0, 0)  # Black text
        overlay_canvas.setFont(font_bold, 11)
        overlay_canvas.drawString(12, height - 130, f"{doc_type}")

        overlay_canvas.drawString(140, height - 130, f"{document.document_number}")
        
        # Page number
        overlay_canvas.setFont(font_name, 9)
        overlay_canvas.drawString(49, height - 110, "1")
        overlay_canvas.drawString(70, height - 110, "1")
        
        # Date information - Right side
        overlay_canvas.setFont(font_name, 9)
        if document.issued_date:
            overlay_canvas.drawString(480, height - 156, document.issued_date.strftime('%d/%m/%Y'))
        
        # Payment condition or validity
        if document.due_date:
            if document.type == DocumentType.quote:
                overlay_canvas.drawString(480, height - 172, document.due_date.strftime('%d/%m/%Y'))
            else:
                payment_condition = document.status.upper() if document.status else 'CONTADO'
                overlay_canvas.drawString(480, height - 172, payment_condition)
        
        # Branch and seller
        overlay_canvas.drawString(480, height - 187, "PRINCIPAL")
        seller_name = current_user.name if current_user and current_user.name else "ADMIN"
        overlay_canvas.drawString(480, height - 202, seller_name[:20])  # Limit length
        
        # Client information section - Left side, middle area
        overlay_canvas.setFont(font_name, 10)
        client_y_start = height - 155
        
        if client:
            # Client name
            overlay_canvas.drawString(140, client_y_start, client.name[:35])  # Limit to fit field
            
            # RTN (Tax ID) - usually empty, but could be added to client model
            overlay_canvas.drawString(140, client_y_start - 15, client.identifier)
            
            # Client code
            overlay_canvas.drawString(140, client_y_start - 30, f"CLI-{client.id:04d}")
            
            # Address
            if client.address:
                overlay_canvas.drawString(140, client_y_start - 45, client.address[:40])  # Limit to fit
        else:
            # Empty client fields
            overlay_canvas.drawString(100, client_y_start, "CLIENTE GENERAL")
            overlay_canvas.drawString(100, client_y_start - 20, "")
            overlay_canvas.drawString(100, client_y_start - 40, "CLI-0000")
            overlay_canvas.drawString(100, client_y_start - 60, "")
        
        # Items table - Main content area
        overlay_canvas.setFont(font_name, 8)
        items_start_y = height - 260
        row_height = 15
        
        # Column positions (adjust based on your template)
        col_codigo = 30      # Código column
        col_articulo = 110   # Artículo column  
        col_cantidad = 280   # Cantidad column
        col_precio = 340     # Precio Uni. column
        col_descuento = 410  # Descto/reb column
        col_valor = 480      # Valor column
        
        for i, item in enumerate(document_items[:25]):
            y_pos = items_start_y - (i * row_height)
            
            # Código
            codigo = str(item.inventory_item_id) if item.inventory_item_id else f"ART-{item.id}"
            overlay_canvas.drawString(col_codigo, y_pos, codigo[:8])
            
            # Artículo (description)
            articulo = ""
            if item.inventory_item_id and item.inventory_item:
                articulo = item.inventory_item.name
            elif item.description:
                articulo = item.description
            else:
                articulo = "Artículo personalizado"
            
            overlay_canvas.drawString(col_articulo, y_pos, articulo[:25])  # Truncate to fit
            
            # Cantidad (right aligned)
            overlay_canvas.drawRightString(col_cantidad + 10, y_pos, str(item.quantity or 0))
            
            # Precio Uni. (right aligned)
            overlay_canvas.drawRightString(col_precio + 35, y_pos, f"L{item.unit_price or 0:,.2f}")
            
            # Descuento (right aligned) - usually 0
            overlay_canvas.drawRightString(col_descuento + 35, y_pos, "0.00")
            
            # Valor total (right aligned)
            total_item = (item.quantity or 0) * (item.unit_price or 0)
            overlay_canvas.drawRightString(col_valor + 65, y_pos, f"L{total_item:,.2f}")
        
        # Totals section - Bottom right
        overlay_canvas.setFont(font_name, 9)
        totals_start_y = height - 650
        totals_x = 480  # Right aligned with valor column
        
        # Calculate totals
        subtotal = document.total_amount or 0
        
        # For Honduras tax system
        vta_exenta = subtotal
        venta_gravada_15 = subtotal * 0.6  # 60% at 15%
        venta_gravada_18 = subtotal * 0.4  # 40% at 18%
        venta_exonerada = 0
        imp_15 = venta_gravada_15 * 0.15
        imp_18 = venta_gravada_18 * 0.18
        total_final = subtotal + imp_15 + imp_18
        
        # VTA EXENTA
        overlay_canvas.drawRightString(totals_x + 50, totals_start_y - 27, f"L{vta_exenta:,.2f}")
        
        # VENTA GRAVADA 15%
        overlay_canvas.drawRightString(totals_x + 50, totals_start_y - 45, f"L{venta_gravada_15:,.2f}")
        
        # VENTA GRAVADA 18%
        overlay_canvas.drawRightString(totals_x + 50, totals_start_y - 65, f"L{venta_gravada_18:,.2f}")
        
        # VENTA EXONERADA
        overlay_canvas.drawRightString(totals_x + 50, totals_start_y - 82, f"L{venta_exonerada:,.2f}")
        
        # IMP. S/VENTA 15%
        overlay_canvas.drawRightString(totals_x + 50, totals_start_y - 100, f"L{imp_15:,.2f}")
        
        # IMP. S/VENTA 18%
        overlay_canvas.drawRightString(totals_x + 50, totals_start_y - 117, f"L{imp_18:,.2f}")
        
        # TOTAL (bold and larger)
        overlay_canvas.setFont(font_bold, 11)
        overlay_canvas.drawRightString(totals_x + 50, totals_start_y - 145, f"L{total_final:,.2f}")
        
        # Amount in words - Bottom left
        overlay_canvas.setFont(font_name, 10)
        
        # Convert number to words
        def number_to_words(amount):
            lang_code = get_locale().language
            amount = round(amount, 2)
            return num2words(amount, lang=lang_code)
        
        words = number_to_words(total_final)
        overlay_canvas.drawString(totals_x - 160, totals_start_y - 180, words[:70])  # Limit length to fit
        
        # Save the overlay
        overlay_canvas.save()
        overlay_buffer.seek(0)
        
        # Create overlay PDF
        overlay_pdf = PdfReader(overlay_buffer)
        overlay_page = overlay_pdf.pages[0]
        
        # Merge template with overlay
        template_page.merge_page(overlay_page)

        doc_type_name = "cotizacion" if document.type == DocumentType.quote else "factura"
        filename = f"{doc_type_name}_{document.document_number}.pdf"
        
        # Create output PDF
        output_buffer = BytesIO()
        output_pdf = PdfWriter()
        output_pdf.add_metadata({
            '/Title': filename
        })
        output_pdf.add_page(template_page)
        output_pdf.write(output_buffer)
        
        # Prepare response
        output_buffer.seek(0)
        response = make_response(output_buffer.getvalue())
        output_buffer.close()
        overlay_buffer.close()
        
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
        
    except Exception as e:
        flash(_(f'Error generating PDF: {str(e)}'), 'error')
        return redirect(url_for('invoices.view', company_id=company_id, id=id))

@invoices.route('/<int:company_id>/invoices/<int:id>/convert', methods=['POST'])
@login_required
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
            company_id=company_id,
            document_number=invoice_number,
            type=DocumentType.invoice,
            client_id=quote.client_id,
            user_id=current_user.id,
            status='draft',
            issued_date=datetime.now(),
            due_date=quote.due_date,
            total_amount=quote.total_amount
        )
        
        db.session.add(invoice)
        db.session.flush()
        
        # Copy items from quote to invoice
        quote_items = DocumentItem.query.filter_by(document_id=quote.id).all()
        for item in quote_items:
            invoice_item = DocumentItem(
                document_id=invoice.id,
                inventory_item_id=item.inventory_item_id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price
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
