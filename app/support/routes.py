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
    page = request.args.get('page', 1, type=int)
    per_page = 50
    table_filter = request.args.get('table_name', '').strip()
    action_filter = request.args.get('action', '').strip()
    
    query = AuditLog.query

    if table_filter:
        query = query.filter(AuditLog.table_name == table_filter)
    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
        
    pagination = query.order_by(AuditLog.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    models = get_all_models()
    return render_template(
        'support/audit_logs.html', 
        pagination=pagination, 
        tables=sorted(list(models.keys())),
        table_filter=table_filter,
        action_filter=action_filter
    )

@support.route('/deleted-items')
def deleted_items():
    table_name = request.args.get('table_name', '')
    models = get_all_models()
    
    items = []
    columns = []
    
    if table_name and table_name in models:
        model_cls = models[table_name]
        items = model_cls.query.execution_options(include_deleted=True).filter(model_cls.is_deleted == True).order_by(model_cls.deleted_at.desc()).all()
        # Get primary columns to display (just a few)
        mapper = inspect(model_cls)
        columns = [c.key for c in mapper.columns][:5] # Show first 5 columns

    return render_template(
        'support/deleted_items.html',
        tables=sorted(list(models.keys())),
        selected_table=table_name,
        items=items,
        columns=columns
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
