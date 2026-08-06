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
