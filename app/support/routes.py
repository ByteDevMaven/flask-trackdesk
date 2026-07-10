import json
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import current_user, login_required
from sqlalchemy import or_, text, inspect
from app.extensions import db
from . import support
from app.models.base import BaseModel
from app.models.audit import AuditLog

# Utility to get all models dynamically
def get_all_models():
    models = {}
    for mapper in db.Model.registry.mappers:
        cls = mapper.class_
        # Ensure it inherits from BaseModel to have is_deleted etc.
        if issubclass(cls, BaseModel) and cls != BaseModel:
            models[cls.__tablename__] = cls
    return models

@support.before_request
@login_required
def restrict_to_superadmins():
    if not current_user.is_superadmin:
        abort(403)

@support.route('/')
def dashboard():
    # Gather some basic stats
    models = get_all_models()
    
    deleted_counts = {}
    total_deleted = 0
    for table_name, model_cls in models.items():
        if hasattr(model_cls, 'is_deleted'):
            # Must use include_deleted=True to count them
            count = model_cls.query.execution_options(include_deleted=True).filter(model_cls.is_deleted == True).count()
            if count > 0:
                deleted_counts[table_name] = count
                total_deleted += count

    audit_count = AuditLog.query.count()
    recent_audits = AuditLog.query.order_by(AuditLog.id.desc()).limit(10).all()

    return render_template(
        'support/dashboard.html',
        total_deleted=total_deleted,
        deleted_counts=deleted_counts,
        audit_count=audit_count,
        recent_audits=recent_audits,
        tables=list(models.keys())
    )

@support.route('/audit-logs')
def audit_logs():
    from app.models.user import User
    from app.models.company import Company
    from datetime import datetime, timedelta

    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Collect all filter params
    table_filter   = request.args.get('table_name', '').strip()
    action_filter  = request.args.get('action', '').strip()
    user_filter    = request.args.get('user_id', '').strip()
    company_filter = request.args.get('company_id', '').strip()
    record_filter  = request.args.get('record_id', '').strip()
    date_from      = request.args.get('date_from', '').strip()
    date_to        = request.args.get('date_to', '').strip()

    query = AuditLog.query

    if table_filter:
        query = query.filter(AuditLog.table_name == table_filter)
    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
    if user_filter:
        try:
            query = query.filter(AuditLog.user_id == int(user_filter))
        except ValueError:
            pass
    if company_filter:
        try:
            query = query.filter(AuditLog.company_id == int(company_filter))
        except ValueError:
            pass
    if record_filter:
        try:
            query = query.filter(AuditLog.record_id == int(record_filter))
        except ValueError:
            pass
    if date_from:
        try:
            query = query.filter(AuditLog.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(AuditLog.created_at < datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1))
        except ValueError:
            pass

    pagination = query.order_by(AuditLog.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    models    = get_all_models()
    users     = User.query.with_entities(User.id, User.name).order_by(User.name).all()
    companies = Company.query.with_entities(Company.id, Company.name).order_by(Company.name).all()

    # Build active filter dict for badge display
    active_filters = {k: v for k, v in {
        'Tabla': table_filter,
        'Acción': action_filter,
        'Usuario': next((u.name for u in users if str(u.id) == user_filter), None) if user_filter else None,
        'Empresa': next((c.name for c in companies if str(c.id) == company_filter), None) if company_filter else None,
        'Registro #': record_filter,
        'Desde': date_from,
        'Hasta': date_to,
    }.items() if v}

    return render_template(
        'support/audit_logs.html',
        pagination=pagination,
        tables=sorted(list(models.keys())),
        users=users,
        companies=companies,
        table_filter=table_filter,
        action_filter=action_filter,
        user_filter=user_filter,
        company_filter=company_filter,
        record_filter=record_filter,
        date_from=date_from,
        date_to=date_to,
        active_filters=active_filters,
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
