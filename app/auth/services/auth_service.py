from datetime import datetime, UTC
from urllib.parse import urlparse

from flask import url_for
from flask_login import login_user

from app.extensions import bcrypt
from app.models import User, db


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
