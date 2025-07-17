from datetime import datetime, timezone
import re
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from extensions import bcrypt
from models import db, User, Role, Company

from . import users

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_password_reset_email(user_email, user_name, reset_token):
    """Send password reset email using SMTP"""
    try:
        # Email configuration (you should set these in your app config)
        smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = current_app.config.get('SMTP_PORT', 587)
        smtp_username = current_app.config.get('SMTP_USERNAME', '')
        smtp_password = current_app.config.get('SMTP_PASSWORD', '')
        from_email = current_app.config.get('FROM_EMAIL', smtp_username)
        
        if not all([smtp_username, smtp_password]):
            raise Exception("SMTP credentials not configured")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = user_email
        msg['Subject'] = "Password Reset Request - Business Management System"
        
        # Email body
        reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
        body = f"""
        Hello {user_name},

        You have requested a password reset for your Business Management System account.

        Please click the link below to reset your password:
        {reset_url}

        This link will expire in 1 hour for security reasons.

        If you did not request this password reset, please ignore this email.

        Best regards,
        Business Management System Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, user_email, text)
        server.quit()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {str(e)}")
        return False

@users.route('/users')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    company_filter = request.args.get('company', '')
    status_filter = request.args.get('status', '')
    
    query = User.query
    
    # Apply search filter
    if search:
        query = query.filter(
            or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    # Apply role filter
    if role_filter:
        query = query.filter(User.role_id == role_filter)
    
    # Apply company filter
    if company_filter:
        query = query.join(User.companies).filter(Company.id == company_filter)
    
    # Apply status filter
    if status_filter:
        if status_filter == 'active':
            query = query.filter(User.active == True)
        elif status_filter == 'inactive':
            query = query.filter(User.active == False)
    
    # Order by creation date (newest first)
    query = query.order_by(User.created_at.desc())
    
    # Paginate results
    per_page = 20
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    users = pagination.items
    
    # Get filter options
    roles = Role.query.all()
    companies = Company.query.all()
    
    return render_template('users/index.html', 
                         users=users, 
                         pagination=pagination,
                         roles=roles,
                         companies=companies,
                         search=search,
                         role_filter=role_filter,
                         company_filter=company_filter,
                         status_filter=status_filter)

@users.route('/users/create')
@login_required
def create():
    roles = Role.query.all()
    companies = Company.query.all()
    return render_template('users/form.html', 
                         user=None, 
                         roles=roles, 
                         companies=companies)

@users.route('/users/store', methods=['POST'])
@login_required
def store():
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role_id = request.form.get('role_id')
        company_ids = request.form.getlist('company_ids')
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Name is required')
        elif len(name) < 2:
            errors.append('Name must be at least 2 characters long')
            
        if not email:
            errors.append('Email is required')
        elif not is_valid_email(email):
            errors.append('Please enter a valid email address')
        elif User.query.filter_by(email=email).first():
            errors.append('Email address is already registered')
            
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        elif password != confirm_password:
            errors.append('Passwords do not match')
            
        if not role_id:
            errors.append('Role is required')
        elif not Role.query.get(role_id):
            errors.append('Invalid role selected')
            
        if not company_ids:
            errors.append('At least one company must be selected')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('users.create'))
        
        # Create new user
        user = User(
            active=True,
            name=name,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            role_id=role_id
        )
        
        # Add companies
        for company_id in company_ids:
            company = Company.query.get(company_id)
            if company:
                user.companies.append(company)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {name} has been created successfully!', 'success')
        return redirect(url_for('users.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating user: {str(e)}', 'error')
        return redirect(url_for('users.create'))

@users.route('/users/<int:id>')
@login_required
def view(id):
    user = User.query.get_or_404(id)
    now = datetime.now(timezone.utc)
    created_at = user.created_at.replace(tzinfo=timezone.utc)
    days = (now - created_at).days
    return render_template('users/view.html', user=user, account_age_days=days)

@users.route('/users/<int:id>/edit')
@login_required
def edit(id):
    user = User.query.get_or_404(id)
    roles = Role.query.all()
    companies = Company.query.all()
    return render_template('users/form.html', 
                         user=user, 
                         roles=roles, 
                         companies=companies)

@users.route('/users/<int:id>/update', methods=['POST'])
@login_required
def update(id):
    user = User.query.get_or_404(id)
    
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role_id = request.form.get('role_id')
        company_ids = request.form.getlist('company_ids')
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Name is required')
        elif len(name) < 2:
            errors.append('Name must be at least 2 characters long')
            
        if not email:
            errors.append('Email is required')
        elif not is_valid_email(email):
            errors.append('Please enter a valid email address')
        else:
            # Check if email is taken by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user.id:
                errors.append('Email address is already registered')
                
        # Password validation (only if password is provided)
        if password:
            if len(password) < 6:
                errors.append('Password must be at least 6 characters long')
            elif password != confirm_password:
                errors.append('Passwords do not match')
                
        if not role_id:
            errors.append('Role is required')
        elif not Role.query.get(role_id):
            errors.append('Invalid role selected')
            
        if not company_ids:
            errors.append('At least one company must be selected')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('users.edit', id=id))
        
        # Update user
        user.name = name
        user.email = email
        user.role_id = role_id
        
        # Update password if provided
        if password:
            user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Update companies
        user.companies.clear()
        for company_id in company_ids:
            company = Company.query.get(company_id)
            if company:
                user.companies.append(company)
        
        db.session.commit()
        
        flash(f'User {name} has been updated successfully!', 'success')
        return redirect(url_for('users.view', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user: {str(e)}', 'error')
        return redirect(url_for('users.edit', id=id))

@users.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    user = User.query.get_or_404(id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('users.index'))
    
    try:
        user_name = user.name
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {user_name} has been deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('users.index'))

@users.route('/users/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    user = User.query.get_or_404(id)
    
    # Prevent self-deactivation
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot deactivate your own account'})
    
    try:
        # Toggle user status
        user.active = not user.active
        db.session.commit()
        
        status_text = 'activated' if user.active else 'deactivated'
        return jsonify({
            'success': True, 
            'message': f'User {user.name} has been {status_text} successfully',
            'active': user.active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@users.route('/users/<int:id>/send-password-reset', methods=['POST'])
@login_required
def send_password_reset(id):
    user = User.query.get_or_404(id)
    
    try:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)

        from flask import session
        session[f'reset_token_{reset_token}'] = {
            'user_id': user.id,
            'expires': (datetime.now() + datetime.timedelta(hours=1)).isoformat()
        }
        
        # Send email
        if send_password_reset_email(user.email, user.name, reset_token):
            return jsonify({
                'success': True,
                'message': f'Password reset email sent to {user.email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send password reset email. Please check SMTP configuration.'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@users.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    users = User.query.filter(
        or_(
            User.name.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    results = []
    for user in users:
        results.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role.name if user.role else 'No Role',
            'companies': [company.name for company in user.companies],
            'active': user.active
        })
    
    return jsonify(results)