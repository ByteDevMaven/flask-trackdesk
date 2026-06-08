import secrets
from datetime import datetime, UTC, timedelta
from urllib.parse import urlparse

from flask import url_for
from flask_login import login_user

from app.extensions import bcrypt
from app.models import User, Token, db
from app.services.email_service import EmailService


class AuthService:
    @staticmethod
    def authenticate_user(email: str, password: str, remember: bool):
        """
        Authenticate a user by email and password.
        Returns (user, error_message). If successful, user is logged in.
        """
        user = User.query.filter_by(email=email).first()

        if user is None:
            # Prevent timing attacks by checking a dummy hash
            dummy_hash = b'$2b$12$5J0b5y5H9V1m1o5H5K5M5u5R5T5F5E5D5C5B5A5z5y5x5w5v5u5t5'
            try:
                bcrypt.check_password_hash(dummy_hash, password)
            except ValueError:
                pass
            return None, 'invalid_credentials'

        if not bcrypt.check_password_hash(user.password_hash, password):
            return None, 'invalid_credentials'
            
        if not user.is_active:
            return None, 'invalid_credentials'

        login_user(user, remember=remember)
        user.last_login = datetime.now(UTC)
        db.session.commit()
        return user, None

    @staticmethod
    def get_redirect_url(next_page: str, current_user) -> str:
        """Determine safe redirect URL after login."""
        # Check if next_page is safe: must be relative, not absolute
        if not next_page or urlparse(next_page).netloc != '' or next_page.startswith(('\\\\', '//')):
            if current_user.companies:
                return url_for('dashboard.index', company_id=current_user.companies[0].id)
            return url_for('companies.index')
        return next_page

    @staticmethod
    def generate_password_reset_token(email: str):
        """Generate and send a password reset token if user exists."""
        user = User.query.filter_by(email=email).first()
        if not user or not user.is_active:
            # Silently return to prevent email enumeration
            return True

        # Invalidate existing unused password reset tokens for this user
        Token.query.filter_by(user_id=user.id, type='password_reset', is_valid=True).update({'is_valid': False})

        # Generate a new token
        raw_token = secrets.token_urlsafe(32)
        token_hash = bcrypt.generate_password_hash(raw_token).decode('utf-8')

        token = Token(
            user_id=user.id,
            token_hash=token_hash,
            type='password_reset',
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(token)
        db.session.commit()

        reset_url = url_for('auth.reset_password', token=raw_token, email=user.email, _external=True)
        EmailService.send_password_reset(user, reset_url)
        return True

    @staticmethod
    def validate_and_reset_password(email: str, raw_token: str, new_password: str):
        """Validate token and reset password."""
        user = User.query.filter_by(email=email).first()
        if not user or not user.is_active:
            return False, "Token inválido o expirado."

        # Find a valid token for this user
        valid_tokens = Token.query.filter_by(
            user_id=user.id, 
            type='password_reset', 
            is_valid=True
        ).all()

        matched_token = None
        for t in valid_tokens:
            if not t.is_expired() and bcrypt.check_password_hash(t.token_hash, raw_token):
                matched_token = t
                break

        if not matched_token:
            return False, "Token inválido o expirado."

        # Reset password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        matched_token.mark_used()
        
        # Invalidate all other password reset tokens
        for t in valid_tokens:
            if t.id != matched_token.id:
                t.is_valid = False

        db.session.commit()
        return True, "Contraseña actualizada exitosamente."
