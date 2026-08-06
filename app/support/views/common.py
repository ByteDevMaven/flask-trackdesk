import base64
import json
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from flask import abort
from flask_login import current_user, login_required
from sqlalchemy import MetaData, Table, and_, inspect
from sqlalchemy.sql.sqltypes import Boolean, Date, DateTime, Float, Integer, JSON, Numeric, Time

from app.extensions import db
from app.models.audit import AuditLog
from app.models.base import BaseModel

from .. import support


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
