from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.audit import AuditLog

from .. import support
from .common import (
    coerce_value,
    database_fields,
    encode_primary_key,
    get_all_models,
    get_database_table,
    get_database_tables,
    primary_key_filters,
    serialize_value,
    support_audit,
)


@support.route('/deleted-items')
def deleted_items():
    from app.models.company import Company

    table_name     = request.args.get('table_name', '')
    search_query   = request.args.get('q', '').strip()
    company_filter = request.args.get('company_id', '').strip()
    models         = get_all_models()

    items   = []
    columns = []

    if table_name and table_name in models:
        model_cls = models[table_name]
        q = model_cls.query.execution_options(include_deleted=True).filter(model_cls.is_deleted == True)

        # Company filter (if the model has company_id)
        if company_filter and hasattr(model_cls, 'company_id'):
            try:
                q = q.filter(model_cls.company_id == int(company_filter))
            except ValueError:
                pass

        items = q.order_by(model_cls.deleted_at.desc()).all()

        # Text search across string columns (in Python after DB fetch)
        if search_query:
            mapper   = inspect(model_cls)
            str_cols = [c.key for c in mapper.columns if hasattr(c.type, 'length')]
            items = [
                item for item in items
                if any(search_query.lower() in str(getattr(item, col, '') or '').lower()
                       for col in str_cols)
            ]

        mapper  = inspect(model_cls)
        columns = [c.key for c in mapper.columns][:6]

    companies = Company.query.with_entities(Company.id, Company.name).order_by(Company.name).all()

    return render_template(
        'support/deleted_items.html',
        tables=sorted(list(models.keys())),
        selected_table=table_name,
        items=items,
        columns=columns,
        companies=companies,
        company_filter=company_filter,
        search_query=search_query,
    )


@support.route('/restore/<string:table_name>/<int:record_id>', methods=['POST'])
def restore_item(table_name, record_id):
    models = get_all_models()
    if table_name not in models:
        flash("Tabla no encontrada", "error")
        return redirect(url_for('support.deleted_items'))
        
    model_cls = models[table_name]
    record = model_cls.query.execution_options(include_deleted=True).get_or_404(record_id)
    
    if getattr(record, 'is_deleted', False):
        record.is_deleted = False
        record.deleted_at = None
        db.session.commit()
        flash(f"Registro {record_id} en {table_name} ha sido restaurado exitosamente.", "success")
    else:
        flash("El registro no estaba eliminado.", "info")
        
    return redirect(url_for('support.deleted_items', table_name=table_name))


@support.route('/view/<string:table_name>/<int:record_id>')
def record_view(table_name, record_id):
    models = get_all_models()
    if table_name not in models:
        abort(404)
        
    model_cls = models[table_name]
    record = model_cls.query.execution_options(include_deleted=True).get_or_404(record_id)
    
    # Introspect record fields
    mapper = inspect(model_cls)
    record_data = {}
    for column in mapper.columns:
        record_data[column.key] = getattr(record, column.key)
        
    # Get audit logs for this specific record
    audits = AuditLog.query.filter_by(
        table_name=table_name, 
        record_id=record_id
    ).order_by(AuditLog.id.desc()).all()
    
    return render_template(
        'support/record_view.html',
        table_name=table_name,
        record_id=record_id,
        record=record,
        record_data=record_data,
        audits=audits
    )
