from flask import render_template, request, redirect, url_for, flash
from flask_login import logout_user, current_user
from flask_wtf.csrf import validate_csrf
from flask_babel import _
from wtforms.validators import ValidationError

from . import auth
from app.extensions import limiter
from .services import AuthService


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

        user, error = AuthService.authenticate_user(email, password, remember)

        if error == 'inactive':
            flash(_("Your account is inactive. Please contact support."), 'warning')
            return redirect(url_for('auth.login'))

        if user:
            next_page = request.args.get('next')
            return redirect(AuthService.get_redirect_url(next_page, current_user))
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