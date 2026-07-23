import base64
import json
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import current_user, login_required
from sqlalchemy import MetaData, Table, and_, delete, func, insert, inspect, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.sqltypes import Boolean, Date, DateTime, Float, Integer, JSON, Numeric, Time
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

def get_database_tables():
    """Return the database's real tables, not just ORM model tables."""
    return sorted(inspect(db.engine).get_table_names())


def get_database_table(table_name):
    """Reflect one whitelisted table so user input can never name arbitrary SQL."""
    if table_name not in get_database_tables():
        abort(404)
    return Table(table_name, MetaData(), autoload_with=db.engine)


def serialize_value(value):
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    return value


def field_value(value):
    value = serialize_value(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return '' if value is None else str(value)


def input_kind(column):
    if isinstance(column.type, Boolean):
        return 'boolean'
    if isinstance(column.type, JSON):
        return 'json'
    if isinstance(column.type, DateTime):
        return 'datetime'
    return 'text'


def coerce_value(column, raw_value, force_null=False):
    """Convert browser input using the reflected column type before binding it."""
    if force_null:
        if column.nullable:
            return None
        raise ValueError(f'"{column.name}" no permite valores nulos.')
    if raw_value == '' and column.nullable:
        return None
    if isinstance(column.type, Boolean):
        return raw_value in ('1', 'true', 'True', 'on', 'yes')
    if isinstance(column.type, JSON):
        return json.loads(raw_value) if raw_value else None
    if isinstance(column.type, DateTime):
        return datetime.fromisoformat(raw_value)
    if isinstance(column.type, Date):
        return date.fromisoformat(raw_value)
    if isinstance(column.type, Time):
        return time.fromisoformat(raw_value)
    if isinstance(column.type, Integer):
        return int(raw_value)
    if isinstance(column.type, (Float, Numeric)):
        return Decimal(raw_value) if isinstance(column.type, Numeric) else float(raw_value)
    try:
        if column.type.python_type is UUID:
            return UUID(raw_value)
    except NotImplementedError:
        pass
    return raw_value


def encode_primary_key(table, row):
    values = [serialize_value(row[column.name]) for column in table.primary_key.columns]
    return base64.urlsafe_b64encode(json.dumps(values).encode()).decode().rstrip('=')


def primary_key_filters(table, key):
    if len(table.primary_key.columns) == 0:
        abort(400, 'Esta tabla no tiene clave primaria y no puede editarse de forma segura.')
    try:
        padded = key + '=' * (-len(key) % 4)
        values = json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        abort(400, 'Clave de registro no v?lida.')
    columns = list(table.primary_key.columns)
    if not isinstance(values, list) or len(values) != len(columns):
        abort(400, 'Clave de registro no v?lida.')
    return and_(*(column == coerce_value(column, str(value)) for column, value in zip(columns, values)))


def database_fields(table, record=None, include_primary_key=False):
    fields = []
    for column in table.columns:
        if column.computed or (column.primary_key and (not include_primary_key or column.autoincrement)):
            continue
        fields.append({
            'column': column,
            'value': field_value(record[column.name]) if record else '',
            'kind': input_kind(column),
            'required': not column.nullable and column.default is None and column.server_default is None,
        })
    return fields


def support_audit(table_name, action, record_key, old_data=None, new_data=None):
    """Core/reflected writes do not trigger ORM listeners, so record them explicitly."""
    db.session.add(AuditLog(
        user_id=current_user.id,
        action=action,
        table_name=table_name,
        record_id=None,
        old_data={'primary_key': record_key, **(old_data or {})},
        new_data={'primary_key': record_key, **(new_data or {})},
    ))

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

@support.route('/database')
def database_browser():
    table_name = request.args.get('table_name', '')
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = 50
    tables = get_database_tables()
    table = get_database_table(table_name) if table_name else None
    rows, columns, total, can_modify = [], [], 0, False

    if table is not None:
        columns, can_modify = list(table.columns), len(table.primary_key.columns) > 0
        total = db.session.execute(select(func.count()).select_from(table)).scalar_one()
        result = db.session.execute(select(table).limit(per_page).offset((page - 1) * per_page)).mappings()
        for row in result:
            values = {column.name: serialize_value(row[column.name]) for column in columns}
            rows.append({'values': values, 'key': encode_primary_key(table, row) if can_modify else None})

    return render_template('support/database_browser.html', tables=tables, selected_table=table_name,
                           table=table, columns=columns, rows=rows, total=total, page=page,
                           per_page=per_page, can_modify=can_modify)


@support.route('/database/<string:table_name>/new', methods=['GET', 'POST'])
def database_new_record(table_name):
    table = get_database_table(table_name)
    if len(table.primary_key.columns) == 0:
        abort(400, 'Esta tabla no tiene clave primaria y no puede modificarse de forma segura.')
    fields = database_fields(table, include_primary_key=True)

    if request.method == 'POST':
        try:
            values = {}
            for field in fields:
                column = field['column']
                raw = request.form.get(column.name, '')
                if column.primary_key and not raw and column.autoincrement:
                    continue
                values[column.name] = coerce_value(column, raw, f'null__{column.name}' in request.form)
            result = db.session.execute(insert(table).values(**values))
            key = list(result.inserted_primary_key) if result.inserted_primary_key else []
            support_audit(table_name, 'SUPPORT_CREATE', key, new_data=values)
            db.session.commit()
            flash('Registro creado y registrado en auditor?a.', 'success')
            return redirect(url_for('support.database_browser', table_name=table_name))
        except (ValueError, SQLAlchemyError, json.JSONDecodeError) as error:
            db.session.rollback()
            flash(f'No se pudo crear el registro: {error}', 'error')

    return render_template('support/database_record_form.html', table=table, table_name=table_name,
                           fields=fields, record=None, record_key=None, mode='create')


@support.route('/database/<string:table_name>/record/<string:record_key>', methods=['GET', 'POST'])
def database_edit_record(table_name, record_key):
    table = get_database_table(table_name)
    filters = primary_key_filters(table, record_key)
    record = db.session.execute(select(table).where(filters)).mappings().first()
    if record is None:
        abort(404)
    fields = database_fields(table, record)

    if request.method == 'POST':
        try:
            values = {
                field['column'].name: coerce_value(field['column'], request.form.get(field['column'].name, ''),
                                                    f"null__{field['column'].name}" in request.form)
                for field in fields
            }
            old_data = {name: serialize_value(record[name]) for name in values}
            db.session.execute(update(table).where(filters).values(**values))
            support_audit(table_name, 'SUPPORT_UPDATE', record_key, old_data=old_data, new_data=values)
            db.session.commit()
            flash('Registro actualizado y registrado en auditor?a.', 'success')
            return redirect(url_for('support.database_edit_record', table_name=table_name, record_key=record_key))
        except (ValueError, SQLAlchemyError, json.JSONDecodeError) as error:
            db.session.rollback()
            flash(f'No se pudo actualizar el registro: {error}', 'error')

    return render_template('support/database_record_form.html', table=table, table_name=table_name,
                           fields=fields, record=record, record_key=record_key, mode='edit')


@support.route('/database/<string:table_name>/record/<string:record_key>/delete', methods=['POST'])
def database_delete_record(table_name, record_key):
    table = get_database_table(table_name)
    if request.form.get('confirmation') != table_name:
        flash('Escribe el nombre exacto de la tabla para confirmar la eliminaci?n.', 'error')
        return redirect(url_for('support.database_edit_record', table_name=table_name, record_key=record_key))
    filters = primary_key_filters(table, record_key)
    record = db.session.execute(select(table).where(filters)).mappings().first()
    if record is None:
        abort(404)
    try:
        old_data = {column.name: serialize_value(record[column.name]) for column in table.columns}
        db.session.execute(delete(table).where(filters))
        support_audit(table_name, 'SUPPORT_DELETE', record_key, old_data=old_data)
        db.session.commit()
        flash('Registro eliminado y registrado en auditor?a.', 'success')
    except SQLAlchemyError as error:
        db.session.rollback()
        flash(f'No se pudo eliminar el registro: {error}', 'error')
        return redirect(url_for('support.database_edit_record', table_name=table_name, record_key=record_key))
    return redirect(url_for('support.database_browser', table_name=table_name))
