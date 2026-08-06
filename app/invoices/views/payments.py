from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, send_file, session, url_for
from flask_login import current_user, login_required
from flask_wtf.csrf import validate_csrf
from sqlalchemy import or_
from wtforms import ValidationError

from app.extensions import limiter
from app.models import Contact, Document, DocumentItem, DocumentType, InventoryItem, Payment, PaymentMethod, Project, db
from app.models.enums import ContactType, DocumentStatus
from app.utils import resolve_company

from .. import invoices
from ..services import create_invoice_or_quote, generate_invoice_pdf_from_request, get_invoice_list, update_invoice_or_quote
from ..services.invoice_create_service import _generate_document_number
from ..services.invoice_query_service import export_invoice_report_xlsx
from ..services.template_service import TemplateService


@invoices.route('/<string:company_id>/invoices/<int:id>/add-payment', methods=['GET', 'POST'])
@login_required
@limiter.exempt
def add_payment(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id
    ).first_or_404()
    
    if request.method == 'GET':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return render_template('invoices/partials/payment_form.html', invoice=document, now=datetime.now(UTC))
        return redirect(url_for('invoices.view', company_id=company_id, id=id))

    csrf_token = request.form.get("csrf_token")
    try:
        validate_csrf(csrf_token)
    except ValidationError:
        flash("Invalid CSRF token. Please try again.", "error")
        return redirect(url_for("auth.login"))

    try:
        from ..services import add_invoice_payment
        add_invoice_payment(document, request.form, request.files)
        flash('Payment recorded successfully', 'success')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return {"success": True}
        return redirect(url_for('invoices.view', company_id=company_id, id=id))

    except ValueError as e:
        flash(f'Invalid payment data: {e}', 'error')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return {"success": False, "message": str(e)}, 400

        return redirect(url_for('invoices.view', company_id=company_id, id=id))
    except Exception as e:
        flash(f'Error recording payment: {e}', 'error')
        return redirect(url_for('invoices.view', company_id=company_id, id=id))


@invoices.route('/<string:company_id>/invoices/<int:id>/print')
@login_required
def print_invoice(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    document = Document.query.filter(
        Document.id == id,
        Document.company_id == company_id,
        or_(
            Document.type == DocumentType.invoice,
            Document.type == DocumentType.quote
        )
    ).first_or_404()

    try:
        # Check if user selected a specific template
        template_id_param = request.args.get('template_id')
        template = None
        if template_id_param:
            try:
                template = TemplateService.get(company_id, int(template_id_param))
            except Exception:
                pass
                
        pdf_bytes, filename = generate_invoice_pdf_from_request(
            document=document,
            request=request,
            session=session,
            current_user=current_user,
            template=template,
        )

        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'inline; filename="{filename}"'
        return response

    except Exception as e:
        flash(f"Error generating PDF: {str(e)}", "error")
        return redirect(
            url_for("invoices.view", company_id=company_id, id=id)
        )
