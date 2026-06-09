from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app.models import Role, Company
from . import users
from .services import UserService

@users.route('/users')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    company_filter = request.args.get('company', '')
    status_filter = request.args.get('status', '')
    
    pagination = UserService.get_paginated_users(
        page, 20, search, role_filter, company_filter, status_filter, current_user
    )
    users_list = pagination.items
    
    visible_companies_map = {}
    for u in users_list:
        visible_companies_map[u.id] = UserService.get_visible_companies_for_user(u, current_user)
    
    roles = Role.query.all()
    companies = Company.query.all()
    
    return render_template('users/index.html', 
                         users=users_list, 
                         pagination=pagination,
                         roles=roles,
                         companies=companies,
                         search=search,
                         role_filter=role_filter,
                         company_filter=company_filter,
                         status_filter=status_filter,
                         visible_companies_map=visible_companies_map)

@users.route('/users/create')
@login_required
def create():
    roles = Role.query.filter(Role.name != 'superadmin').all()
    if current_user.is_superadmin:
        companies = Company.query.all()
    else:
        companies = current_user.companies
    return render_template('users/form.html', 
                         user=None, 
                         roles=roles, 
                         companies=companies)

@users.route('/users/store', methods=['POST'])
@login_required
def store():
    try:
        user = UserService.create_user(request.form, current_user)
        flash(f'User {user.name} has been created successfully!', 'success')
        return redirect(url_for('users.index'))
    except ValueError as e:
        for error in e.args[0]:
            flash(error, 'error')
        return redirect(url_for('users.create'))
    except Exception as e:
        flash(f'Error creating user: {str(e)}', 'error')
        return redirect(url_for('users.create'))

@users.route('/users/<int:id>')
@login_required
def view(id):
    user, account_age_days = UserService.get_user_with_age(id, current_user)
    visible_companies = UserService.get_visible_companies_for_user(user, current_user)
    return render_template('users/view.html', user=user, account_age_days=account_age_days, visible_companies=visible_companies)

@users.route('/users/<int:id>/edit')
@login_required
def edit(id):
    user = UserService.get_user_for_edit(id, current_user)
    roles = Role.query.filter(Role.name != 'superadmin').all()
    if current_user.is_superadmin:
        companies = Company.query.all()
    else:
        companies = current_user.companies
        
    visible_companies = UserService.get_visible_companies_for_user(user, current_user)
    
    return render_template('users/form.html', 
                         user=user, 
                         roles=roles, 
                         companies=companies,
                         visible_companies=visible_companies)

@users.route('/users/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    try:
        user = UserService.update_user(id, request.form, current_user)
        flash(f'User {user.name} has been updated successfully!', 'success')
        return redirect(url_for('users.view', id=id))
    except ValueError as e:
        for error in e.args[0]:
            flash(error, 'error')
        return redirect(url_for('users.edit', id=id))
    except Exception as e:
        flash(f'Error updating user: {str(e)}', 'error')
        return redirect(url_for('users.edit', id=id))

@users.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    try:
        user_name = UserService.delete_user(id, current_user)
        flash(f'User {user_name} has been deleted successfully!', 'success')
    except ValueError as e:
        for error in e.args[0]:
            flash(error, 'error')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('users.index'))

@users.route('/users/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    try:
        user = UserService.toggle_user_status(id, current_user)
        status_text = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'success': True, 
            'message': f'User {user.name} has been {status_text} successfully',
            'active': user.is_active
        })
    except PermissionError as e:
        return jsonify({'success': False, 'message': str(e)})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@users.route('/users/<int:id>/send-password-reset', methods=['POST'])
@login_required
def send_password_reset(id):
    try:
        email = UserService.generate_and_send_password_reset(id)
        return jsonify({
            'success': True,
            'message': f'Password reset email sent to {email}'
        })
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@users.route('/users/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    users_list = UserService.search_users(query, current_user)
    
    results = []
    for user in users_list:
        visible_companies = UserService.get_visible_companies_for_user(user, current_user)
        results.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role.name if user.role else 'No Role',
            'companies': [company.name for company in visible_companies],
            'active': user.is_active
        })
    
    return jsonify(results)