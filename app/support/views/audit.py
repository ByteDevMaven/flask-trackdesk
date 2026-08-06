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
