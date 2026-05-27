from flask import current_app, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from flask_babel import _
from sqlalchemy import or_, desc
from datetime import datetime, UTC

from app.models import db, Payment, Document, DocumentType, Contact
from app.extensions import limiter

from . import payments

@payments.route('/<int:company_id>/payments')
@login_required
@limiter.exempt
def index(company_id):
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    method = request.args.get('method', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
                           
    query = db.session.query(Payment).filter(
        Payment.company_id == company_id
    ).join(Document, Payment.document_id == Document.id, isouter=True)\
     .join(Contact, Document.client_id == Contact.id, isouter=True)
    
                   
    if search:
        query = query.filter(
            or_(
                Document.document_number.ilike(f'%{search}%'),
                Contact.name.ilike(f'%{search}%'),
                Payment.notes.ilike(f'%{search}%')
            )
        )
    
    if method:
        query = query.filter(Payment.method == method)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Payment.payment_date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(Payment.payment_date <= date_to_obj)
        except ValueError:
            pass
    
                                          
    query = query.order_by(desc(Payment.payment_date))
    
              
    pagination = query.paginate( # type: ignore
        page=page, 
        per_page=int(current_app.config.get('ITEMS_PER_PAGE', 20)),
        error_out=False
    )
    
    payments = pagination.items
    
                                       
    for payment in payments:
        if payment.document_id:
            payment.document = Document.query.get(payment.document_id)
            if payment.document and payment.document.client_id:
                payment.document.client = Contact.query.get(payment.document.client_id)
    
                      
    total_payments = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.company_id == company_id
    ).scalar() or 0
    
    return render_template('payments/index.html', 
                         payments=payments, 
                         pagination=pagination,
                         total_payments=total_payments)

@payments.route('/<int:company_id>/payments/create')
@login_required
@limiter.exempt
def create(company_id):
                                    
    invoice_id = request.args.get('invoice_id', type=int)
    selected_invoice = None
    
    if invoice_id:
        selected_invoice = Document.query.filter(
            Document.id == invoice_id,
            Document.company_id == company_id,
            Document.type == DocumentType.invoice
        ).first()
        
        if selected_invoice and selected_invoice.client_id:
            selected_invoice.client = Contact.query.get(selected_invoice.client_id)
    
    return render_template('payments/form.html', 
                         payment=None,
                         selected_invoice=selected_invoice)

@payments.route('/<int:company_id>/payments/search-invoices')
@login_required
@limiter.exempt
def search_invoices(company_id):
    search = request.args.get('q', '')
    
                                                  
    query = db.session.query(Document).filter(
        Document.company_id == company_id,
        or_(
            Document.status == 'sent',
            Document.status == 'overdue',
            Document.status == 'pending'
        )
    ).join(Contact, Document.client_id == Contact.id, isouter=True)
    
    if search:
        query = query.filter(
            or_(
                Document.document_number.ilike(f'%{search}%'),
                Contact.name.ilike(f'%{search}%')
            )
        )
    
    invoices = query.limit(10).all()
    
                                                  
    results = []
    for invoice in invoices:
                                             
        total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.document_id == invoice.id
        ).scalar() or 0
        
        remaining_balance = (invoice.total_amount or 0) - total_paid
        
        client_name = ''
        if invoice.client_id:
            client = Contact.query.get(invoice.client_id)
            client_name = client.name if client else ''
        
        results.append({
            'id': invoice.id,
            'document_number': invoice.document_number,
            'client_name': client_name,
            'total_amount': invoice.total_amount or 0,
            'remaining_balance': remaining_balance,
            'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
            'status': invoice.status
        })
    
    return jsonify(results)

@payments.route('/<int:company_id>/payments/store', methods=['POST'])
@login_required
@limiter.exempt
def store(company_id):
    try:
                            
        payment = Payment(
            company_id=company_id, # type: ignore
            document_id=int(request.form.get('document_id')) if request.form.get('document_id') else None, # type: ignore
            amount=float(request.form.get('amount', 0)), # type: ignore
            payment_date=datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d') if request.form.get('payment_date') else datetime.now(UTC), # type: ignore
            method=request.form.get('method', ''), # type: ignore
            notes=request.form.get('notes', '') # type: ignore
        )
        
        db.session.add(payment)
        
                                             
        if payment.document_id:
            invoice = Document.query.get(payment.document_id)
            if invoice:
                                                           
                total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
                    Payment.document_id == invoice.id
                ).scalar() or 0
                total_paid += payment.amount
                
                                                        
                if total_paid >= (invoice.total_amount or 0):
                    invoice.status = 'paid'
                elif total_paid > 0:
                    invoice.status = 'pending'
        
        db.session.commit()
        flash(_('Payment recorded successfully'), 'success')
        return redirect(url_for('payments.view', company_id=company_id, id=payment.id))
        
    except Exception as e:
        db.session.rollback()
        flash(_('Error recording payment: %(error)s', error=str(e)), 'error')
        return redirect(url_for('payments.create', company_id=company_id))

@payments.route('/<int:company_id>/payments/<int:id>')
@login_required
@limiter.exempt
def view(company_id, id):
    payment = Payment.query.filter(
        Payment.id == id,
        Payment.company_id == company_id
    ).first_or_404()
    
                                                 
    if payment.document_id:
        payment.document = Document.query.get(payment.document_id)
        if payment.document and payment.document.client_id:
            payment.document.client = Contact.query.get(payment.document.client_id)
    
    return render_template('payments/view.html', payment=payment)

@payments.route('/<int:company_id>/payments/<int:id>/edit')
@login_required
@limiter.exempt
def edit(company_id, id):
    payment = Payment.query.filter(
        Payment.id == id,
        Payment.company_id == company_id
    ).first_or_404()
    
                                      
    selected_invoice = None
    if payment.document_id:
        selected_invoice = Document.query.get(payment.document_id)
        if selected_invoice and selected_invoice.client_id:
            selected_invoice.client = Contact.query.get(selected_invoice.client_id)
    
    return render_template('payments/form.html', 
                         payment=payment,
                         selected_invoice=selected_invoice)

@payments.route('/<int:company_id>/payments/<int:id>/update', methods=['POST'])
@login_required
@limiter.exempt
def update(company_id, id):   
    payment = Payment.query.filter(
        Payment.id == id,
        Payment.company_id == company_id
    ).first_or_404()
    
    try:
        old_amount = payment.amount
        old_document_id = payment.document_id
        
                               
        payment.document_id = int(request.form.get('document_id')) if request.form.get('document_id') else None # type: ignore
        payment.amount = float(request.form.get('amount', 0))
        payment.payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d') if request.form.get('payment_date') else payment.payment_date # type: ignore
        payment.method = request.form.get('method', payment.method)
        payment.notes = request.form.get('notes', payment.notes)
        
                                 
        invoices_to_update = set()
        if old_document_id:
            invoices_to_update.add(old_document_id)
        if payment.document_id:
            invoices_to_update.add(payment.document_id)
        
        for invoice_id in invoices_to_update:
            invoice = Document.query.get(invoice_id)
            if invoice:
                                                             
                total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
                    Payment.document_id == invoice_id
                ).scalar() or 0
                
                                       
                if total_paid >= (invoice.total_amount or 0):
                    invoice.status = 'paid'
                elif total_paid > 0:
                    invoice.status = 'partial'
                else:
                    invoice.status = 'sent'
        
        db.session.commit()
        flash(_('Payment updated successfully'), 'success')
        return redirect(url_for('payments.view', company_id=company_id, id=payment.id))
        
    except Exception as e:
        db.session.rollback()
        flash(_('Error updating payment: %(error)s', error=str(e)), 'error')
        return redirect(url_for('payments.edit', company_id=company_id, id=id))

@payments.route('/<int:company_id>/payments/<int:id>/delete', methods=['POST'])
@login_required
def delete(company_id, id):
    payment = Payment.query.filter(
        Payment.id == id,
        Payment.company_id == company_id
    ).first_or_404()
    
    try:
        document_id = payment.document_id
        
                            
        payment.is_deleted = True
        payment.deleted_at = datetime.now(UTC)
        
                                             
        if document_id:
            invoice = Document.query.get(document_id)
            if invoice:
                                                             
                total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
                    Payment.document_id == document_id
                ).scalar() or 0
                
                                       
                if total_paid >= (invoice.total_amount or 0):
                    invoice.status = 'paid'
                elif total_paid > 0:
                    invoice.status = 'partial'
                else:
                    invoice.status = 'sent'
        
        db.session.commit()
        flash(_('Payment deleted successfully'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Error deleting payment: %(error)s', error=str(e)), 'error')
    
    return redirect(url_for('payments.index', company_id=company_id))
