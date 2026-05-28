from datetime import datetime, UTC
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user
from flask_wtf.csrf import validate_csrf
from flask_babel import _
from wtforms.validators import ValidationError
from urllib.parse import urlparse

from . import auth
from app.extensions import bcrypt, limiter
from app.models import User, db

@auth.route('/login', methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        csrf_token = request.form.get("csrf_token") 

        try:
            validate_csrf(csrf_token)
        except ValidationError:
            flash(_("Invalid CSRF token. Please try again."), "error")
            return redirect(url_for("auth.login")) 

        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if user and not user.is_active:
            flash(_("Your account is inactive. Please contact support."), 'warning')
            return redirect(url_for('auth.login')) 

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard.index', company_id=current_user.companies[0].id)
            user.last_login = datetime.now(UTC)
            db.session.commit()
            return redirect(next_page)
        else:
            flash(_("Invalid username or password"), 'warning')

    return render_template("auth/login.html")

@auth.route("/logout")
def logout():
    logout_user()
    flash(_("Logout success."), 'success')
    return redirect(url_for("auth.login"))

@auth.route('/register')
def register():
    pass

@auth.route('/forgot_password')
def forgot_password():
    pass