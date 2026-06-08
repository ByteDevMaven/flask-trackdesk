from flask import render_template, request, redirect, url_for, flash
from flask_login import logout_user, current_user
from flask_wtf.csrf import validate_csrf
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
            flash("Token CSRF inválido. Por favor, inténtalo de nuevo.", "error")
            return redirect(url_for("auth.login"))

        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember") == "on"

        user, error = AuthService.authenticate_user(email, password, remember)

        if user:
            next_page = request.args.get('next')
            return redirect(AuthService.get_redirect_url(next_page, current_user))
        else:
            flash("Usuario o contraseña inválidos.", 'warning')

    return render_template("auth/login.html")


@auth.route("/logout")
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", 'success')
    return redirect(url_for("auth.login"))


@auth.route('/register')
def register():
    pass


@auth.route('/forgot_password', methods=["GET", "POST"])
@limiter.limit("3 per minute")
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index', company_id=current_user.companies[0].id if current_user.companies else 0))

    if request.method == "POST":
        email = request.form.get("email")
        if email:
            AuthService.generate_password_reset_token(email)
            flash("Si el correo existe en nuestro sistema, hemos enviado un enlace para restablecer la contraseña.", "success")
            return redirect(url_for("auth.login"))
            
    return render_template("auth/forgot_password.html")


@auth.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index', company_id=current_user.companies[0].id if current_user.companies else 0))
        
    email = request.args.get('email')
    if not email:
        flash("Enlace de restablecimiento inválido.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        if not password or password != password_confirm:
            flash("Las contraseñas no coinciden o están vacías.", "error")
            return render_template("auth/reset_password.html", token=token, email=email)
            
        success, message = AuthService.validate_and_reset_password(email, token, password)
        if success:
            flash(message, "success")
            return redirect(url_for("auth.login"))
        else:
            flash(message, "error")
            
    return render_template("auth/reset_password.html", token=token, email=email)