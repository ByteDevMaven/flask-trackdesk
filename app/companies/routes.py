from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from models import db, Company, User, Client, Supplier, InventoryItem, Document, Payment, Report, DocumentSequence

from . import companies

@companies.route('/companies')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Company.query
    
    if search:
        query = query.filter(Company.name.ilike(f'%{search}%'))
    
    companies = query.order_by(Company.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('companies/index.html', companies=companies, search=search)

@companies.route('/companies/create')
@login_required
def create():
    users = User.query.all()
    return render_template('companies/form.html', company=None, users=users)

@companies.route('/companies/store', methods=['POST'])
@login_required
def store():
    try:
        name = request.form.get('name', '').strip()
        currency = request.form.get('currency', 'USD')
        tax_rate = request.form.get('tax_rate', 0.0)
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        identifier = request.form.get('identifier', '').strip()
        user_ids = request.form.getlist('user_ids')
        
        if not name:
            flash('Company name is required.', 'error')
            return redirect(url_for('companies.create'))
        
        # Check if company name already exists
        existing_company = Company.query.filter_by(name=name).first()
        if existing_company:
            flash('A company with this name already exists.', 'error')
            return redirect(url_for('companies.create'))
        
        company = Company(
            name=name, # type: ignore
            currency=currency, # type: ignore
            tax_rate=float(tax_rate), # type: ignore
            address=address, # type: ignore
            phone=phone, # type: ignore
            email=email, # type: ignore
            identifier=identifier, # type: ignore
            created_at=datetime.now() # type: ignore
        )
        
        # Add selected users to the company
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
            company.users.extend(users) # type: ignore
        
        db.session.add(company)
        db.session.commit()
        
        flash('Company created successfully!', 'success')
        return redirect(url_for('companies.view', id=company.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating company: {str(e)}', 'error')
        return redirect(url_for('companies.create'))

@companies.route('/companies/<int:id>')
@login_required
def view(id):
    company = Company.query.get_or_404(id)
    
    # Get company statistics
    stats = {
        'users_count': len(company.users),
        'clients_count': Client.query.filter_by(company_id=company.id).count(),
        'suppliers_count': Supplier.query.filter_by(company_id=company.id).count(),
        'inventory_count': InventoryItem.query.filter_by(company_id=company.id).count(),
        'documents_count': Document.query.filter_by(company_id=company.id).count(),
        'payments_count': Payment.query.filter_by(company_id=company.id).count(),
        'reports_count': Report.query.filter_by(company_id=company.id).count()
    }
    
    # Get recent activity
    recent_documents = Document.query.filter_by(company_id=company.id).order_by(Document.issued_date.desc()).limit(5).all()
    recent_payments = Payment.query.filter_by(company_id=company.id).order_by(Payment.payment_date.desc()).limit(5).all()
    
    return render_template('companies/view.html', 
                         company=company, 
                         stats=stats,
                         recent_documents=recent_documents,
                         recent_payments=recent_payments)

@companies.route('/companies/<int:id>/edit')
@login_required
def edit(id):
    company = Company.query.get_or_404(id)
    users = User.query.all()
    return render_template('companies/form.html', company=company, users=users)

@companies.route('/companies/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    company = Company.query.get_or_404(id)
    
    try:
        name = request.form.get('name', '').strip()
        currency = request.form.get('currency', 'USD')
        tax_rate = request.form.get('tax_rate', 0.0)
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        identifier = request.form.get('identifier', '').strip()
        user_ids = request.form.getlist('user_ids')
        
        if not name:
            flash('Company name is required.', 'error')
            return redirect(url_for('companies.edit', id=id))
        
        # Check if company name already exists (excluding current company)
        existing_company = Company.query.filter(Company.name == name, Company.id != id).first()
        if existing_company:
            flash('A company with this name already exists.', 'error')
            return redirect(url_for('companies.edit', id=id))
        
        company.name = name
        company.currency = currency
        company.tax_rate = float(tax_rate)
        company.address = address
        company.phone = phone
        company.email = email
        company.identifier = identifier
        company.updated_at = datetime.now()
        
        # Update user associations
        company.users.clear()
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
            company.users.extend(users)
        
        db.session.commit()
        
        flash('Company updated successfully!', 'success')
        return redirect(url_for('companies.view', id=company.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating company: {str(e)}', 'error')
        return redirect(url_for('companies.edit', id=id))

@companies.route('/companies/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    company = Company.query.get_or_404(id)
    
    try:
        # Check if company has related data
        has_clients = Client.query.filter_by(company_id=company.id).first() is not None
        has_suppliers = Supplier.query.filter_by(company_id=company.id).first() is not None
        has_inventory = InventoryItem.query.filter_by(company_id=company.id).first() is not None
        has_documents = Document.query.filter_by(company_id=company.id).first() is not None
        has_payments = Payment.query.filter_by(company_id=company.id).first() is not None
        has_reports = Report.query.filter_by(company_id=company.id).first() is not None
        
        if any([has_clients, has_suppliers, has_inventory, has_documents, has_payments, has_reports]):
            flash('Cannot delete company with existing data. Please remove all related clients, suppliers, inventory, documents, payments, and reports first.', 'error')
            return redirect(url_for('companies.view', id=id))
        
        # Clear user associations
        company.users.clear()
        
        db.session.delete(company)
        db.session.commit()
        
        flash('Company deleted successfully!', 'success')
        return redirect(url_for('companies.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting company: {str(e)}', 'error')
        return redirect(url_for('companies.view', id=id))

@companies.route('/companies/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    companies = Company.query.filter(
        Company.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    results = []
    for company in companies:
        results.append({
            'id': company.id,
            'name': company.name,
            'users_count': len(company.users),
            'created_at': company.created_at.strftime('%Y-%m-%d') if company.created_at else ''
        })
    
    return jsonify(results)

@companies.route('/companies/<int:id>/sequences')
@login_required
def sequences_index(id):
    """List all document sequences for a company"""
    company = Company.query.get_or_404(id)
    sequences = DocumentSequence.query.filter_by(company_id=id).order_by(DocumentSequence.expiration_date.desc()).all()
    return render_template('companies/sequences/index.html', company=company, sequences=sequences, today=datetime.now().date())

@companies.route('/companies/<int:id>/sequences/create')
@login_required
def sequence_create(id):
    """Form to create a new document sequence"""
    company = Company.query.get_or_404(id)
    return render_template('companies/sequences/form.html', company=company, sequence=None)

@companies.route('/companies/<int:id>/sequences/store', methods=['POST'])
@login_required
def sequence_store(id):
    """Store a new document sequence"""
    company = Company.query.get_or_404(id)
    try:
        cai = request.form.get('cai', '').strip()
        range_start = int(request.form.get('range_start', 0))
        range_end = int(request.form.get('range_end', 0))
        expiration_date_str = request.form.get('expiration_date', '')
        
        if not all([cai, range_start, range_end, expiration_date_str]):
            flash('All fields are required.', 'error')
            return redirect(url_for('companies.sequence_create', id=id))
        
        expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
        
        sequence = DocumentSequence(
            company_id=id,
            cai=cai,
            range_start=range_start,
            range_end=range_end,
            current=range_start - 1,
            expiration_date=expiration_date
        )
        
        db.session.add(sequence)
        db.session.commit()
        
        flash('Document sequence created successfully!', 'success')
        return redirect(url_for('companies.sequences_index', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating sequence: {str(e)}', 'error')
        return redirect(url_for('companies.sequence_create', id=id))

@companies.route('/companies/<int:id>/sequences/<int:seq_id>/edit')
@login_required
def sequence_edit(id, seq_id):
    """Form to edit an existing document sequence"""
    company = Company.query.get_or_404(id)
    sequence = DocumentSequence.query.filter_by(id=seq_id, company_id=id).first_or_404()
    return render_template('companies/sequences/form.html', company=company, sequence=sequence)

@companies.route('/companies/<int:id>/sequences/<int:seq_id>/update', methods=['POST'])
@login_required
def sequence_update(id, seq_id):
    """Update an existing document sequence"""
    company = Company.query.get_or_404(id)
    sequence = DocumentSequence.query.filter_by(id=seq_id, company_id=id).first_or_404()
    
    try:
        cai = request.form.get('cai', '').strip()
        range_start = int(request.form.get('range_start', 0))
        range_end = int(request.form.get('range_end', 0))
        current = int(request.form.get('current', sequence.current))
        expiration_date_str = request.form.get('expiration_date', '')
        
        if not all([cai, expiration_date_str]):
            flash('CAI and Expiration Date are required.', 'error')
            return redirect(url_for('companies.sequence_edit', id=id, seq_id=seq_id))
        
        sequence.cai = cai
        sequence.range_start = range_start
        sequence.range_end = range_end
        sequence.current = current
        sequence.expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
        
        db.session.commit()
        
        flash('Document sequence updated successfully!', 'success')
        return redirect(url_for('companies.sequences_index', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating sequence: {str(e)}', 'error')
        return redirect(url_for('companies.sequence_edit', id=id, seq_id=seq_id))

@companies.route('/companies/<int:id>/sequences/<int:seq_id>/delete', methods=['POST'])
@login_required
def sequence_delete(id, seq_id):
    """Delete a document sequence"""
    sequence = DocumentSequence.query.filter_by(id=seq_id, company_id=id).first_or_404()
    
    try:
        db.session.delete(sequence)
        db.session.commit()
        flash('Document sequence deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting sequence: {str(e)}', 'error')
        
    return redirect(url_for('companies.sequences_index', id=id))
