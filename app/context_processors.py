from flask import Flask, session
from flask_login import current_user
from app.extensions import get_locale
from config import Config

def register_context_processors(app: Flask):
    @app.context_processor
    def inject_conf_var():
        from datetime import datetime, UTC
        return dict(
            AVAILABLE_LANGUAGES=Config.LANGUAGES,
            CURRENT_LANGUAGE=get_locale(),
            now=datetime.now(UTC),
            company_id=session.get('selected_company_id'),
            current_user=current_user
        )

    @app.template_filter('role_name_es')
    def role_name_es(role_name):
        if not role_name:
            return 'Sin rol'
        mapping = {
            'superadmin': 'Superadministrador',
            'owner': 'Dueño / Administrador',
            'manager': 'Gerente General',
            'hr_manager': 'Recursos Humanos',
            'inventory_manager': 'Jefe de Inventario',
            'sales_manager': 'Jefe de Ventas',
            'accountant': 'Contador',
            'staff': 'Staff / Empleado',
            'viewer': 'Auditor / Lector',
        }
        return mapping.get(role_name, role_name.title())
