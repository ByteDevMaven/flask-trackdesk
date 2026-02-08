from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user
from flask_wtf.csrf import validate_csrf
from flask_babel import _
from wtforms.validators import ValidationError
from urllib.parse import urlparse

from . import auth
from extensions import bcrypt, limiter
from models import User, Company, Role, db

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

        if user and not user.active:
            flash(_("Your account is inactive. Please contact support."), 'warning')
            return redirect(url_for('auth.login')) 

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard.index', company_id=current_user.companies[0].id)
                
            return redirect(next_page)
        else:
            flash(_("Invalid username or password"), 'warning')

    return render_template("auth/login.html")

@auth.route("/logout")
def logout():
    logout_user()
    flash(_("Logout success."), 'success')
    return redirect(url_for("auth.login"))

@auth.route('/register', methods=["GET", "POST"])
@auth.route('/register/<int:companyID>', methods=["GET", "POST"])
@limiter.limit("2 per minute", override_defaults=False)
def register(companyID=None):
    if request.method == "POST" and current_app.config.get("ALLOW_REGISTRATION", False):
        csrf_token = request.form.get("csrf_token")

        try:
            validate_csrf(csrf_token)
        except ValidationError:
            flash(_("Invalid CSRF token. Please try again."), "error")
            return redirect(url_for("auth.register"))

        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmpassword")
        company_id = request.form.get("company_id")

        if User.query.filter_by(email=email).first():
            flash(_("Email already exists"), 'warning')
        elif password != confirmpassword:
            flash(_("Passwords must match!"), 'warning')
        else:
            # Create or get company
            company = Company.query.get(company_id)
            if not company:
                flash(_("No valid company found."), 'error')
                redirect(url_for("auth.register", company_id=companyID))

            # Optional: assign a default role
            default_role = Role.query.filter_by(name="user").first()

            user = User(
                name=name,
                email=email,
                password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
                role_id=default_role.id if default_role else None
            )
            user.companies.append(company)

            db.session.add(user)
            db.session.commit()

            flash(_("Account created successfully!"), "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", company_id=companyID)

@auth.route('/forgot_password')
def forgot_password():
    pass