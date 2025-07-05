from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from models import db, Company, User, Client, Supplier, InventoryItem, Document, Payment, Report

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
            name=name,
            created_at=datetime.now()
        )
        
        # Add selected users to the company
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
            company.users.extend(users)
        
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
