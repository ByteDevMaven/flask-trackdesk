from datetime import UTC, date, datetime

from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Employee, LeaveRequest, User, WorkSchedule
from app.models.enums import EmployeeClass, LeaveStatus, LeaveType, PTOAccrualPeriod, PayPeriod
from app.utils import resolve_company

from .. import hr
from .common import _is_ajax, _save_attachment


@hr.route('/<string:company_id>/hr/leaves')
@login_required
def leaves(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 15))
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    emp_filter = request.args.get('employee_id', '', type=str)

    q = LeaveRequest.query.filter_by(company_id=company_id)
    if status_filter:
        try:
            q = q.filter_by(status=LeaveStatus(status_filter))
        except ValueError:
            pass
    if type_filter:
        try:
            q = q.filter_by(leave_type=LeaveType(type_filter))
        except ValueError:
            pass
    if emp_filter:
        q = q.filter_by(employee_id=int(emp_filter))

    pagination = q.order_by(LeaveRequest.created_at.desc()).paginate(page=page, per_page=per_page)
    all_employees = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.last_name).all()

    return render_template(
        'hr/leave_requests.html',
        company_id=company_id,
        leaves=pagination,
        status_filter=status_filter,
        type_filter=type_filter,
        emp_filter=emp_filter,
        all_employees=all_employees,
        LeaveType=LeaveType,
        LeaveStatus=LeaveStatus,
    )


@hr.route('/<string:company_id>/hr/leaves/create', methods=['GET', 'POST'])
@login_required
def create_leave(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    all_employees = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.last_name).all()

    if request.method == 'POST':
        try:
            start = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            if end < start:
                raise ValueError('End date cannot be before start date')

            attachment_filename = None
            if 'attachment' in request.files:
                attachment_filename = _save_attachment(request.files['attachment'])

            leave = LeaveRequest(
                company_id=company_id,
                employee_id=int(request.form['employee_id']),
                leave_type=LeaveType(request.form['leave_type']),
                start_date=start,
                end_date=end,
                reason=request.form.get('reason', '').strip() or None,
                attachment_path=attachment_filename,
            )
            db.session.add(leave)
            db.session.commit()
            if _is_ajax():
                return jsonify({'success': True, 'message': 'Solicitud de permiso enviada'})
            flash('Solicitud de permiso enviada', 'success')
            return redirect(url_for('hr.leaves', company_id=company_id))
        except (ValueError, KeyError) as e:
            db.session.rollback()
            if _is_ajax():
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(str(e))
            if _is_ajax():
                return jsonify({'success': False, 'message': 'Ocurrió un error en la base de datos'}), 500
            flash('Ocurrió un error en la base de datos', 'error')

    return render_template(
        'hr/leave_form.html',
        company_id=company_id,
        leave=None,
        employees=all_employees,
        LeaveType=LeaveType,
        form_data=request.form if request.method == 'POST' else {},
    )


@hr.route('/<string:company_id>/hr/leaves/<int:leave_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_leave(company_id, leave_id):
    company = resolve_company(company_id)
    company_id = company.id
    leave = LeaveRequest.query.filter_by(id=leave_id, company_id=company_id).first_or_404()
    all_employees = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.last_name).all()

    if request.method == 'POST':
        try:
            start = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            if end < start:
                raise ValueError('End date cannot be before start date')

            if 'attachment' in request.files and request.files['attachment'].filename:
                leave.attachment_path = _save_attachment(request.files['attachment'])

            leave.employee_id = int(request.form['employee_id'])
            leave.leave_type = LeaveType(request.form['leave_type'])
            leave.start_date = start
            leave.end_date = end
            leave.reason = request.form.get('reason', '').strip() or None

            db.session.commit()
            if _is_ajax():
                return jsonify({'success': True, 'message': 'Solicitud de permiso actualizada'})
            flash('Solicitud de permiso actualizada', 'success')
            return redirect(url_for('hr.leaves', company_id=company_id))
        except (ValueError, KeyError) as e:
            db.session.rollback()
            if _is_ajax():
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(str(e))
            if _is_ajax():
                return jsonify({'success': False, 'message': 'Ocurrió un error en la base de datos'}), 500
            flash('Ocurrió un error en la base de datos', 'error')

    # Prep form data
    form_data = request.form if request.method == 'POST' else {
        'employee_id': leave.employee_id,
        'leave_type': leave.leave_type.value,
        'start_date': leave.start_date.strftime('%Y-%m-%d'),
        'end_date': leave.end_date.strftime('%Y-%m-%d'),
        'reason': leave.reason
    }

    return render_template(
        'hr/leave_form.html',
        company_id=company_id,
        leave=leave,
        employees=all_employees,
        LeaveType=LeaveType,
        form_data=form_data,
    )


@hr.route('/<string:company_id>/hr/leaves/<int:leave_id>/review', methods=['POST'])
@login_required
def review_leave(company_id, leave_id):
    company = resolve_company(company_id)
    company_id = company.id
    leave = LeaveRequest.query.filter_by(id=leave_id, company_id=company_id).first_or_404()
    action = request.form.get('action')

    if action == 'approve':
        if leave.leave_type == LeaveType.pto:
            days = leave.total_days
            if not leave.employee.approve_pto(days):
                if _is_ajax():
                    return jsonify({'success': False, 'message': 'Saldo de PTO insuficiente'})
                flash('Saldo de PTO insuficiente — no se puede aprobar la solicitud', 'error')
                return redirect(url_for('hr.leaves', company_id=company_id))
        leave.status = LeaveStatus.approved
        leave.reviewed_by_id = current_user.id
        leave.review_note = request.form.get('review_note', '').strip() or None
    elif action == 'reject':
        leave.status = LeaveStatus.rejected
        leave.reviewed_by_id = current_user.id
        leave.review_note = request.form.get('review_note', '').strip() or None
    else:
        if _is_ajax():
            return jsonify({'success': False, 'message': 'Acción inválida'})
        flash('Acción inválida', 'error')
        return redirect(url_for('hr.leaves', company_id=company_id))

    try:
        db.session.commit()
        if _is_ajax():
            return jsonify({'success': True, 'message': 'Solicitud de permiso actualizada'})
        flash('Solicitud de permiso actualizada', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(str(e))
        if _is_ajax():
            return jsonify({'success': False, 'message': 'Ocurrió un error en la base de datos'}), 500
        flash('Ocurrió un error en la base de datos', 'error')

    return redirect(url_for('hr.leaves', company_id=company_id))


@hr.route('/<string:company_id>/hr/leaves/<int:leave_id>/view')
@login_required
def view_leave(company_id, leave_id):
    company = resolve_company(company_id)
    company_id = company.id
    leave = LeaveRequest.query.filter_by(id=leave_id, company_id=company_id).first_or_404()
    return render_template(
        'hr/leave_view.html',
        company_id=company_id,
        leave=leave
    )


@hr.route('/<string:company_id>/hr/leaves/<int:leave_id>/delete', methods=['POST'])
@login_required
def delete_leave(company_id, leave_id):
    company = resolve_company(company_id)
    company_id = company.id
    leave = LeaveRequest.query.filter_by(id=leave_id, company_id=company_id).first_or_404()
    
    try:
        leave.is_deleted = True
        db.session.commit()
        if _is_ajax():
            return jsonify({'success': True, 'message': 'Solicitud de permiso eliminada'})
        flash('Solicitud de permiso eliminada', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(str(e))
        if _is_ajax():
            return jsonify({'success': False, 'message': 'Error al eliminar la solicitud'})
        flash('Error al eliminar la solicitud', 'error')

    return redirect(url_for('hr.leaves', company_id=company_id))
