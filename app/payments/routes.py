from app.utils import resolve_company
from flask import current_app, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from flask_babel import _

from . import payments
from app.extensions import limiter
from .services import PaymentService


@payments.route('/<string:company_id>/payments')
@login_required
@limiter.exempt
def index(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    method = request.args.get('method', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 20))
    pagination = PaymentService.get_paginated_payments(
        company_id, page, per_page, search, method, date_from, date_to
    )
    total_payments = PaymentService.get_total_payments(company_id)

    return render_template('payments/index.html',
                         payments=pagination.items,
                         pagination=pagination,
                         total_payments=total_payments)


@payments.route('/<string:company_id>/payments/create')
@login_required
@limiter.exempt
def create(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    invoice_id = request.args.get('invoice_id', type=int)
    selected_invoice = PaymentService.get_selected_invoice(company_id, invoice_id)

    return render_template('payments/form.html',
                         payment=None,
                         selected_invoice=selected_invoice)


@payments.route('/<string:company_id>/payments/search-invoices')
@login_required
@limiter.exempt
def search_invoices(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    search = request.args.get('q', '')
    results = PaymentService.search_invoices(company_id, search)
    return jsonify(results)


@payments.route('/<string:company_id>/payments/store', methods=['POST'])
@login_required
@limiter.exempt
def store(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    try:
        payment = PaymentService.create_payment(company_id, request.form)
        flash(_('Payment recorded successfully'), 'success')
        return redirect(url_for('payments.view', company_id=company_id, id=payment.id))
    except Exception as e:
        flash(_('Error recording payment: %(error)s', error=str(e)), 'error')
        return redirect(url_for('payments.create', company_id=company_id))


@payments.route('/<string:company_id>/payments/<int:id>')
@login_required
@limiter.exempt
def view(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    payment = PaymentService.get_payment(company_id, id)
    return render_template('payments/view.html', payment=payment)


@payments.route('/<string:company_id>/payments/<int:id>/edit')
@login_required
@limiter.exempt
def edit(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    payment = PaymentService.get_payment(company_id, id)
    selected_invoice = None
    if payment.document_id:
        selected_invoice = payment.document if hasattr(payment, 'document') else None

    return render_template('payments/form.html',
                         payment=payment,
                         selected_invoice=selected_invoice)


@payments.route('/<string:company_id>/payments/<int:id>/update', methods=['POST'])
@login_required
@limiter.exempt
def update(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    try:
        payment = PaymentService.update_payment(company_id, id, request.form)
        flash(_('Payment updated successfully'), 'success')
        return redirect(url_for('payments.view', company_id=company_id, id=payment.id))
    except Exception as e:
        flash(_('Error updating payment: %(error)s', error=str(e)), 'error')
        return redirect(url_for('payments.edit', company_id=company_id, id=id))


@payments.route('/<string:company_id>/payments/<int:id>/delete', methods=['POST'])
@login_required
def delete(company_id, id):
    company = resolve_company(company_id)
    company_id = company.id
    try:
        PaymentService.delete_payment(company_id, id)
        flash(_('Payment deleted successfully'), 'success')
    except Exception as e:
        flash(_('Error deleting payment: %(error)s', error=str(e)), 'error')

    return redirect(url_for('payments.index', company_id=company_id))
