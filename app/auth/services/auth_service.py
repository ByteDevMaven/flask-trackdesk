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

        if user and not user.is_active:
            return None, 'inactive'

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            user.last_login = datetime.now(UTC)
            db.session.commit()
            return user, None

        return None, 'invalid_credentials'

    @staticmethod
    def get_redirect_url(next_page: str, current_user) -> str:
        """Determine safe redirect URL after login."""
        if not next_page or urlparse(next_page).netloc != '':
            if current_user.companies:
                return url_for('dashboard.index', company_id=current_user.companies[0].id)
            return url_for('companies.index')
        return next_page
