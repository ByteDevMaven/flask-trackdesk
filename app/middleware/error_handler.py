import traceback
from flask import render_template, request, current_app
from app.services.email_service import EmailService

def init_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/error.html', error_code=400, error_message="Solicitud Incorrecta"), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template('errors/error.html', error_code=401, error_message="No Autorizado"), 401

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/error.html', error_code=403, error_message="Acceso Denegado"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        if request.path.startswith('/api/'):
            return {"error": "No encontrado"}, 404
        return render_template('errors/error.html', error_code=404, error_message="Página no encontrada"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        current_app.logger.error(f"Server Error: {error}")
        EmailService.notify_error(str(error))
        return render_template('errors/error.html', error_code=500, error_message="Error Interno del Servidor"), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        current_app.logger.exception("Unhandled exception:")
        EmailService.notify_error(str(e), stack_trace=traceback.format_exc())
        return render_template('errors/error.html', error_code=500, error_message="Error Interno del Servidor"), 500
