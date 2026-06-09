import re
import secrets
import smtplib
from datetime import datetime, UTC, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import current_app, url_for, session, abort
from sqlalchemy import or_

from app.extensions import bcrypt
from app.models import db, User, Role, Company
from app.models.enums import UserStatus

class UserService:
    @staticmethod
    def _get_visible_company_ids(current_user):
        """Returns IDs of companies the current user can see."""
        if current_user.is_superadmin:
            return [c.id for c in Company.query.all()]
        return [c.id for c in current_user.companies]

    @staticmethod
    def _user_is_visible(user, current_user):
        """Returns True if current_user can see/manage *user*."""
        if current_user.is_superadmin:
            return True
        my_company_ids = set(c.id for c in current_user.companies)
        target_company_ids = set(c.id for c in user.companies)
        return bool(my_company_ids & target_company_ids)

    @staticmethod
    def get_visible_companies_for_user(target_user, current_user):
        """Returns the companies of target_user that current_user is allowed to see."""
        if current_user.is_superadmin:
            return target_user.companies
        visible_ids = set(UserService._get_visible_company_ids(current_user))
        return [c for c in target_user.companies if c.id in visible_ids]

    @staticmethod
    def is_valid_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def send_password_reset_email(user_email, user_name, reset_token):
        try:
            smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('SMTP_PORT', 587)
            smtp_username = current_app.config.get('SMTP_USERNAME', '')
            smtp_password = current_app.config.get('SMTP_PASSWORD', '')
            from_email = current_app.config.get('FROM_EMAIL', smtp_username)
            
            if not all([smtp_username, smtp_password]):
                raise Exception("SMTP credentials not configured")
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = user_email
            msg['Subject'] = "Password Reset Request - Business Management System"
            
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

    @staticmethod
    def get_paginated_users(page, per_page, search, role_filter, company_filter, status_filter, current_user):
        query = User.query

        if not current_user.is_superadmin:
            visible_ids = UserService._get_visible_company_ids(current_user)
            query = query.join(User.companies).filter(Company.id.in_(visible_ids)).distinct()
        
        if search:
            query = query.filter(
                or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        if role_filter:
            query = query.filter(User.role_id == role_filter)
        
        if company_filter:
            query = query.join(User.companies).filter(Company.id == company_filter)
        
        if status_filter:
            if status_filter == 'active':
                query = query.filter(User.status == UserStatus.active)
            elif status_filter == 'inactive':
                query = query.filter(User.status != UserStatus.active)
        
        query = query.order_by(User.created_at.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def create_user(data, current_user):
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        role_id = data.get('role_id')
        company_ids = data.getlist('company_ids')
        
        errors = []
        if not name: errors.append('Name is required')
        elif len(name) < 2: errors.append('Name must be at least 2 characters long')
            
        if not email: errors.append('Email is required')
        elif not UserService.is_valid_email(email): errors.append('Please enter a valid email address')
        elif User.query.filter_by(email=email).first(): errors.append('Email address is already registered')
            
        if not password: errors.append('Password is required')
        elif len(password) < 6: errors.append('Password must be at least 6 characters long')
        elif password != confirm_password: errors.append('Passwords do not match')
            
        if not role_id: errors.append('Role is required')
        elif not Role.query.get(role_id): errors.append('Invalid role selected')
            
        if not company_ids: errors.append('At least one company must be selected')
        
        if errors:
            raise ValueError(errors)
        
        user = User(
            status=UserStatus.active,
            name=name,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            role_id=role_id
        )
        
        for company_id in company_ids:
            company = Company.query.get(company_id)
            if company:
                user.companies.append(company)
        
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_with_age(user_id, current_user):
        user = User.query.get_or_404(user_id)
        if not UserService._user_is_visible(user, current_user):
            abort(403)
        now = datetime.now(UTC)
        created_at = user.created_at.replace(tzinfo=UTC)
        days = (now - created_at).days
        return user, days

    @staticmethod
    def get_user_for_edit(user_id, current_user):
        user = User.query.get_or_404(user_id)
        if not UserService._user_is_visible(user, current_user):
            abort(403)
        if user.is_superadmin and not current_user.is_superadmin:
            abort(403)
        return user

    @staticmethod
    def update_user(user_id, data, current_user):
        user = User.query.get_or_404(user_id)
        if not UserService._user_is_visible(user, current_user):
            abort(403)
            
        if user.is_superadmin and not current_user.is_superadmin:
            abort(403)
            
        has_manage = current_user.has_permission('users.manage')
            
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        role_id = data.get('role_id') if has_manage else None
        company_ids = data.getlist('company_ids') if has_manage else []
        
        errors = []
        if not name: errors.append('Name is required')
        elif len(name) < 2: errors.append('Name must be at least 2 characters long')
            
        if not email: errors.append('Email is required')
        elif not UserService.is_valid_email(email): errors.append('Please enter a valid email address')
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user.id:
                errors.append('Email address is already registered')
                
        if password:
            if len(password) < 6: errors.append('Password must be at least 6 characters long')
            elif password != confirm_password: errors.append('Passwords do not match')
                
        if has_manage:
            if not role_id: errors.append('Role is required')
            elif not Role.query.get(role_id): errors.append('Invalid role selected')
                
            if not company_ids: errors.append('At least one company must be selected')
        
        if errors:
            raise ValueError(errors)
        
        user.name = name
        user.email = email
        
        if has_manage:
            user.role_id = role_id
        
        if password:
            user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        if has_manage:
            visible_company_ids = set(UserService._get_visible_company_ids(current_user))
            unseen_companies = [c for c in user.companies if c.id not in visible_company_ids]
            
            user.companies.clear()
            for c in unseen_companies:
                user.companies.append(c)
                
            for company_id in company_ids:
                if int(company_id) in visible_company_ids:
                    company = Company.query.get(company_id)
                    if company:
                        user.companies.append(company)
        
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id, current_user):
        user = User.query.get_or_404(user_id)
        if not UserService._user_is_visible(user, current_user):
            abort(403)
            
        if user.is_superadmin and not current_user.is_superadmin:
            abort(403)

        if user.id == current_user.id:
            raise ValueError(['You cannot delete your own account'])
        
        user_name = user.name
        user.is_deleted = True
        user.deleted_at = datetime.now(UTC)
        db.session.commit()
        return user_name

    @staticmethod
    def toggle_user_status(user_id, current_user):
        user = User.query.get_or_404(user_id)
        if not UserService._user_is_visible(user, current_user):
            raise PermissionError("Access denied")
            
        if user.is_superadmin and not current_user.is_superadmin:
            raise PermissionError("Cannot modify a superadmin")

        if user.id == current_user.id:
            raise ValueError("You cannot deactivate your own account")
    
        user.status = UserStatus.inactive if user.status == UserStatus.active else UserStatus.active
        db.session.commit()
        return user

    @staticmethod
    def generate_and_send_password_reset(user_id):
        user = User.query.get_or_404(user_id)
        
        reset_token = secrets.token_urlsafe(32)
        session[f'reset_token_{reset_token}'] = {
            'user_id': user.id,
            'expires': (datetime.now(UTC) + timedelta(hours=1)).isoformat()
        }
        
        if UserService.send_password_reset_email(user.email, user.name, reset_token):
            return user.email
        else:
            raise RuntimeError("Failed to send password reset email. Please check SMTP configuration.")

    @staticmethod
    def search_users(query, current_user, limit=10):
        if not query or len(query) < 2:
            return []
        
        users = User.query.filter(
            or_(
                User.name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        )

        if not current_user.is_superadmin:
            visible_ids = UserService._get_visible_company_ids(current_user)
            users = users.join(User.companies).filter(Company.id.in_(visible_ids)).distinct()

        return users.limit(limit).all()
