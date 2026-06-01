from datetime import datetime, UTC

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app.models import User
from . import companies
from .services import CompanyService

@companies.route('/companies')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    pagination = CompanyService.get_paginated_companies(page, 10, search, current_user)
    
    return render_template('companies/index.html', 
                           companies=pagination.items, 
                           pagination=pagination, 
                           search=search)

@companies.route('/companies/create')
@login_required
def create():
    users = User.query.all()
    return render_template('companies/form.html', comp=None, users=users)

@companies.route('/companies/store', methods=['POST'])
@login_required
def store():
    try:
        company = CompanyService.create_company(request.form, current_user)
        flash('Company created successfully!', 'success')
        return redirect(url_for('companies.view', id=company.id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('companies.create'))
    except Exception as e:
        flash(f'Error creating company: {str(e)}', 'error')
        return redirect(url_for('companies.create'))

@companies.route('/companies/<int:id>')
@login_required
def view(id):
    company, stats, recent_documents, recent_payments = CompanyService.get_company_with_stats(id, current_user)
    
    return render_template('companies/view.html', 
                         company=company, 
                         stats=stats,
                         recent_documents=recent_documents,
                         recent_payments=recent_payments)

@companies.route('/companies/<int:id>/edit')
@login_required
def edit(id):
    company = CompanyService.get_company_for_user(id, current_user)
    users = User.query.all()
    return render_template('companies/form.html', comp=company, users=users)

@companies.route('/companies/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    try:
        company = CompanyService.update_company(id, request.form, current_user)
        flash('Company updated successfully!', 'success')
        return redirect(url_for('companies.view', id=company.id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('companies.edit', id=id))
    except Exception as e:
        flash(f'Error updating company: {str(e)}', 'error')
        return redirect(url_for('companies.edit', id=id))

@companies.route('/companies/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        CompanyService.delete_company(id, current_user)
        flash('Company deleted successfully!', 'success')
        return redirect(url_for('companies.index'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('companies.view', id=id))
    except Exception as e:
        flash(f'Error deleting company: {str(e)}', 'error')
        return redirect(url_for('companies.view', id=id))

@companies.route('/companies/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    companies_list = CompanyService.search_companies(query, current_user)
    
    results = []
    for company in companies_list:
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
    company = CompanyService.get_company_for_user(id, current_user)
    sequences = CompanyService.get_sequences(id)
    return render_template('companies/sequences/index.html', company=company, sequences=sequences, today=datetime.now(UTC).date())

@companies.route('/companies/<int:id>/sequences/create')
@login_required
def sequence_create(id):
    """Form to create a new document sequence"""
    company = CompanyService.get_company_for_user(id, current_user)
    return render_template('companies/sequences/form.html', company=company, sequence=None)

@companies.route('/companies/<int:id>/sequences/store', methods=['POST'])
@login_required
def sequence_store(id):
    """Store a new document sequence"""
    CompanyService.get_company_for_user(id, current_user)
    try:
        CompanyService.create_sequence(id, request.form)
        flash('Document sequence created successfully!', 'success')
        return redirect(url_for('companies.sequences_index', id=id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('companies.sequence_create', id=id))
    except Exception as e:
        flash(f'Error creating sequence: {str(e)}', 'error')
        return redirect(url_for('companies.sequence_create', id=id))

@companies.route('/companies/<int:id>/sequences/<int:seq_id>/edit')
@login_required
def sequence_edit(id, seq_id):
    """Form to edit an existing document sequence"""
    company = CompanyService.get_company_for_user(id, current_user)
    sequence = CompanyService.get_sequence(id, seq_id)
    return render_template('companies/sequences/form.html', company=company, sequence=sequence)

@companies.route('/companies/<int:id>/sequences/<int:seq_id>/update', methods=['POST'])
@login_required
def sequence_update(id, seq_id):
    """Update an existing document sequence"""
    CompanyService.get_company_for_user(id, current_user)
    try:
        CompanyService.update_sequence(id, seq_id, request.form)
        flash('Document sequence updated successfully!', 'success')
        return redirect(url_for('companies.sequences_index', id=id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('companies.sequence_edit', id=id, seq_id=seq_id))
    except Exception as e:
        flash(f'Error updating sequence: {str(e)}', 'error')
        return redirect(url_for('companies.sequence_edit', id=id, seq_id=seq_id))

@companies.route('/companies/<int:id>/sequences/<int:seq_id>/delete', methods=['POST'])
@login_required
def sequence_delete(id, seq_id):
    CompanyService.get_company_for_user(id, current_user)
    try:
        CompanyService.delete_sequence(id, seq_id)
        flash('Document sequence deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting sequence: {str(e)}', 'error')
        
    return redirect(url_for('companies.sequences_index', id=id))
