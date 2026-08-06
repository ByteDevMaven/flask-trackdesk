from flask import Flask, request, session, url_for
from flask_login import current_user
from app.extensions import get_locale
from config import Config

def register_context_processors(app: Flask):
    def page_url(page, endpoint=None, **values):
        """Build a pagination URL while preserving the active filters."""
        args = request.args.to_dict(flat=True)
        args.update(values)
        args['page'] = page
        return url_for(endpoint or request.endpoint, **args)

    @app.context_processor
    def inject_conf_var():
        from datetime import datetime, UTC
        return dict(
            AVAILABLE_LANGUAGES=Config.LANGUAGES,
            CURRENT_LANGUAGE=get_locale(),
            now=datetime.now(UTC),
            company_id=session.get('selected_company_slug'),
            current_user=current_user,
            page_url=page_url
        )

    @app.template_filter('role_name_es')
    def role_name_es(role_name):
        if not role_name:
            return 'Sin rol'
        mapping = {
            'superadmin': 'Superadministrador',
            'owner': 'Dueño / Administrador',
            'sr_manager': 'Gerente Senior',
            'manager': 'Gerente General',
            'sr_accountant': 'Contador Senior',
            'accountant': 'Contador',
            'hr_manager': 'Gerente de RRHH',
            'hr_staff': 'Asistente de RRHH',
            'inventory_manager': 'Jefe de Inventario',
            'inventory_staff': 'Auxiliar de Inventario',
            'sales_manager': 'Jefe de Ventas',
            'sales_rep': 'Ejecutivo de Ventas',
            'staff': 'Staff / Empleado',
            'viewer': 'Auditor / Lector',
        }
        return mapping.get(role_name, role_name.title())

    @app.template_filter('translate_ref_es')
    def translate_ref_es(reference):
        if not reference:
            return reference
        mapping = {
            'Manual Adjustment': 'Ajuste Manual',
            'Stock Transfer': 'Transferencia de Stock',
            'Initial Stock': 'Stock Inicial',
            'Purchase Order': 'Orden de Compra',
            'Invoice': 'Factura'
        }
        return mapping.get(reference, reference)
