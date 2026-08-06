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
