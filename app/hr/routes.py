from app.utils import resolve_company
import os
import uuid
from datetime import datetime, UTC, date

from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Employee, LeaveRequest, WorkSchedule, User
from app.models.enums import EmployeeClass, PayPeriod, LeaveType, LeaveStatus, PTOAccrualPeriod

from . import hr

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp'}


def _is_ajax():
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_attachment(file) -> str | None:
    if not file or file.filename == '':
        return None
    if not _allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"hr_{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    return filename


# ─────────────────────────────────────────────────────────────────────────────
#  EMPLOYEES
# ─────────────────────────────────────────────────────────────────────────────

@hr.route('/<string:company_id>/hr/employees')
@login_required
def employees(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'active')
    class_filter = request.args.get('class', '')
    page = request.args.get('page', 1, type=int)
    per_page = int(current_app.config.get('ITEMS_PER_PAGE', 15))

    q = Employee.query.filter_by(company_id=company_id)
    if status_filter == 'active':
        q = q.filter_by(is_active=True)
    elif status_filter == 'inactive':
        q = q.filter_by(is_active=False)
    if class_filter:
        try:
            q = q.filter_by(employee_class=EmployeeClass(class_filter))
        except ValueError:
            pass
    if search:
        like = f'%{search}%'
        q = q.filter(
            (Employee.first_name.ilike(like)) |
            (Employee.last_name.ilike(like)) |
            (Employee.email.ilike(like))
        )
    pagination = q.order_by(Employee.last_name, Employee.first_name).paginate(page=page, per_page=per_page)

    return render_template(
        'hr/employees.html',
        company_id=company_id,
        employees=pagination,
        search=search,
        status_filter=status_filter,
        class_filter=class_filter,
        EmployeeClass=EmployeeClass,
    )


@hr.route('/<string:company_id>/hr/employees/create', methods=['GET', 'POST'])
@login_required
def create_employee(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    users_without_profile = (
        User.query
        .filter(~User.id.in_(
            db.session.query(Employee.user_id).filter(Employee.user_id.isnot(None))
        ))
        .order_by(User.name)
        .all()
    )

    if request.method == 'POST':
        try:
            user_id_raw = request.form.get('user_id') or None
            emp = Employee(
                company_id=company_id,
                user_id=int(user_id_raw) if user_id_raw else None,
                first_name=request.form['first_name'].strip(),
                last_name=request.form['last_name'].strip(),
                email=request.form.get('email', '').strip() or None,
                phone=request.form.get('phone', '').strip() or None,
                address=request.form.get('address', '').strip() or None,
                employee_class=EmployeeClass(request.form['employee_class']),
                hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date(),
                termination_date=(
                    datetime.strptime(request.form['termination_date'], '%Y-%m-%d').date()
                    if request.form.get('termination_date') else None
                ),
                pay_rate=float(request.form.get('pay_rate', 0)),
                pay_period=PayPeriod(request.form['pay_period']),
                pto_balance=float(request.form.get('pto_balance', 0)),
                pto_accrual_rate=(
                    float(request.form['pto_accrual_rate'])
                    if request.form.get('pto_accrual_rate') else None
                ),
                pto_accrual_period=(
                    PTOAccrualPeriod(request.form['pto_accrual_period'])
                    if request.form.get('pto_accrual_period') else None
                ),
                standard_start_time=(
                    datetime.strptime(request.form['standard_start_time'], '%H:%M').time()
                    if request.form.get('standard_start_time') else None
                ),
                standard_end_time=(
                    datetime.strptime(request.form['standard_end_time'], '%H:%M').time()
                    if request.form.get('standard_end_time') else None
                ),
                working_days=','.join(request.form.getlist('working_days')) if request.form.getlist('working_days') else None,
                notes=request.form.get('notes', '').strip() or None,
                is_active=True,
            )
            db.session.add(emp)
            db.session.commit()
            if _is_ajax():
                return jsonify({'success': True, 'message': 'Empleado creado exitosamente'})
            flash('Empleado creado exitosamente', 'success')
            return redirect(url_for('hr.employees', company_id=company_id))
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
        'hr/employee_form.html',
        company_id=company_id,
        employee=None,
        users=users_without_profile,
        EmployeeClass=EmployeeClass,
        PayPeriod=PayPeriod,
        PTOAccrualPeriod=PTOAccrualPeriod,
        form_data=request.form if request.method == 'POST' else {},
    )


@hr.route('/<string:company_id>/hr/employees/<int:emp_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(company_id, emp_id):
    company = resolve_company(company_id)
    company_id = company.id
    emp = Employee.query.filter_by(id=emp_id, company_id=company_id).first_or_404()

    users_available = (
        User.query
        .filter(
            (User.id == emp.user_id) |
            (~User.id.in_(
                db.session.query(Employee.user_id).filter(Employee.user_id.isnot(None))
            ))
        )
        .order_by(User.name)
        .all()
    )

    if request.method == 'POST':
        try:
            user_id_raw = request.form.get('user_id') or None
            emp.user_id = int(user_id_raw) if user_id_raw else None
            emp.first_name = request.form['first_name'].strip()
            emp.last_name = request.form['last_name'].strip()
            emp.email = request.form.get('email', '').strip() or None
            emp.phone = request.form.get('phone', '').strip() or None
            emp.address = request.form.get('address', '').strip() or None
            emp.employee_class = EmployeeClass(request.form['employee_class'])
            emp.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date()
            emp.termination_date = (
                datetime.strptime(request.form['termination_date'], '%Y-%m-%d').date()
                if request.form.get('termination_date') else None
            )
            emp.pay_rate = float(request.form.get('pay_rate', 0))
            emp.pay_period = PayPeriod(request.form['pay_period'])
            emp.pto_balance = float(request.form.get('pto_balance', 0))
            emp.pto_accrual_rate = (
                float(request.form['pto_accrual_rate'])
                if request.form.get('pto_accrual_rate') else None
            )
            emp.pto_accrual_period = (
                PTOAccrualPeriod(request.form['pto_accrual_period'])
                if request.form.get('pto_accrual_period') else None
            )
            emp.standard_start_time = (
                datetime.strptime(request.form['standard_start_time'], '%H:%M').time()
                if request.form.get('standard_start_time') else None
            )
            emp.standard_end_time = (
                datetime.strptime(request.form['standard_end_time'], '%H:%M').time()
                if request.form.get('standard_end_time') else None
            )
            emp.working_days = ','.join(request.form.getlist('working_days')) if request.form.getlist('working_days') else None
            emp.notes = request.form.get('notes', '').strip() or None
            emp.is_active = 'is_active' in request.form
            db.session.commit()
            if _is_ajax():
                return jsonify({'success': True, 'message': 'Empleado actualizado exitosamente'})
            flash('Empleado actualizado exitosamente', 'success')
            return redirect(url_for('hr.employees', company_id=company_id))
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
        'hr/employee_form.html',
        company_id=company_id,
        employee=emp,
        users=users_available,
        EmployeeClass=EmployeeClass,
        PayPeriod=PayPeriod,
        PTOAccrualPeriod=PTOAccrualPeriod,
        form_data={},
    )


@hr.route('/<string:company_id>/hr/employees/<int:emp_id>/delete', methods=['POST'])
@login_required
def delete_employee(company_id, emp_id):
    company = resolve_company(company_id)
    company_id = company.id
    emp = Employee.query.filter_by(id=emp_id, company_id=company_id).first_or_404()
    try:
        emp.is_deleted = True
        db.session.commit()
        if _is_ajax():
            return jsonify({'success': True, 'message': 'Empleado eliminado'})
        flash('Empleado eliminado', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(str(e))
        if _is_ajax():
            return jsonify({'success': False, 'message': 'Ocurrió un error en la base de datos'}), 500
        flash('Ocurrió un error en la base de datos', 'error')
    return redirect(url_for('hr.employees', company_id=company_id))


# ─────────────────────────────────────────────────────────────────────────────
#  LEAVE REQUESTS
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
#  WORK SCHEDULES
# ─────────────────────────────────────────────────────────────────────────────

@hr.route('/<string:company_id>/hr/schedules')
@login_required
def schedules(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    return render_template(
        'hr/schedules.html',
        company_id=company_id
    )

from datetime import timedelta

@hr.route('/<string:company_id>/hr/api/schedules/events')
@login_required
def schedule_events(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    if not start_str or not end_str:
        return jsonify([])

    start_date = datetime.strptime(start_str[:10], '%Y-%m-%d').date()
    end_date = datetime.strptime(end_str[:10], '%Y-%m-%d').date()

    employees = Employee.query.filter_by(company_id=company_id, is_active=True).all()
    
    deviations = WorkSchedule.query.filter(
        WorkSchedule.company_id == company_id,
        WorkSchedule.date >= start_date,
        WorkSchedule.date <= end_date,
        WorkSchedule.is_deleted == False
    ).all()
    
    dev_map = {}
    for d in deviations:
        dev_map[(d.employee_id, d.date)] = d
        
    leaves = LeaveRequest.query.filter(
        LeaveRequest.company_id == company_id,
        LeaveRequest.status == LeaveStatus.approved,
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date
    ).all()
    
    leave_map = {}
    for l in leaves:
        curr = l.start_date
        while curr <= l.end_date:
            leave_map[(l.employee_id, curr)] = l
            curr += timedelta(days=1)
            
    events = []
    
    for emp in employees:
        if not emp.working_days:
            continue
        wd_list = [int(x) for x in emp.working_days.split(',')]
        
        curr_date = start_date
        while curr_date <= end_date:
            is_working_day = curr_date.weekday() in wd_list
            
            leave = leave_map.get((emp.id, curr_date))
            dev = dev_map.get((emp.id, curr_date))
            
            if leave:
                events.append({
                    'id': f'leave_{leave.id}_{curr_date.isoformat()}',
                    'title': f"{emp.first_name} ({leave.leave_type.value.title()})",
                    'start': curr_date.isoformat(),
                    'allDay': True,
                    'color': '#f59e0b',
                    'extendedProps': {
                        'type': 'leave',
                        'employeeName': emp.full_name,
                        'reason': leave.reason
                    }
                })
            else:
                if dev:
                    events.append({
                        'id': f'dev_{dev.id}',
                        'title': f"{emp.first_name} (Desviación)",
                        'start': f"{curr_date.isoformat()}T{dev.start_time.strftime('%H:%M:%S')}",
                        'end': f"{curr_date.isoformat()}T{dev.end_time.strftime('%H:%M:%S')}",
                        'color': '#ef4444',
                        'extendedProps': {
                            'type': 'deviation',
                            'employeeName': emp.full_name,
                            'notes': dev.notes
                        }
                    })
                elif is_working_day and emp.standard_start_time and emp.standard_end_time:
                    events.append({
                        'id': f'std_{emp.id}_{curr_date.isoformat()}',
                        'title': emp.first_name,
                        'start': f"{curr_date.isoformat()}T{emp.standard_start_time.strftime('%H:%M:%S')}",
                        'end': f"{curr_date.isoformat()}T{emp.standard_end_time.strftime('%H:%M:%S')}",
                        'color': '#10b981',
                        'extendedProps': {
                            'type': 'standard',
                            'employeeName': emp.full_name
                        }
                    })
            
            curr_date += timedelta(days=1)
            
    return jsonify(events)


@hr.route('/<string:company_id>/hr/schedules/create', methods=['GET', 'POST'])
@login_required
def create_schedule(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    all_employees = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.last_name).all()

    if request.method == 'POST':
        try:
            start_t = datetime.strptime(request.form['start_time'], '%H:%M').time()
            end_t = datetime.strptime(request.form['end_time'], '%H:%M').time()
            sched = WorkSchedule(
                company_id=company_id,
                employee_id=int(request.form['employee_id']),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                start_time=start_t,
                end_time=end_t,
                notes=request.form.get('notes', '').strip() or None,
            )
            db.session.add(sched)
            db.session.commit()
            if _is_ajax():
                return jsonify({'success': True, 'message': 'Desviación agregada'})
            flash('Desviación agregada', 'success')
            return redirect(url_for('hr.schedules', company_id=company_id))
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
        'hr/schedule_form.html',
        company_id=company_id,
        schedule=None,
        employees=all_employees,
        today=date.today().isoformat(),
        form_data=request.form if request.method == 'POST' else {},
    )


@hr.route('/<string:company_id>/hr/schedules/<int:sched_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_schedule(company_id, sched_id):
    company = resolve_company(company_id)
    company_id = company.id
    sched = WorkSchedule.query.filter_by(id=sched_id, company_id=company_id).first_or_404()
    all_employees = Employee.query.filter_by(company_id=company_id, is_active=True).order_by(Employee.last_name).all()

    if request.method == 'POST':
        try:
            start_t = datetime.strptime(request.form['start_time'], '%H:%M').time()
            end_t = datetime.strptime(request.form['end_time'], '%H:%M').time()
            
            sched.employee_id = int(request.form['employee_id'])
            sched.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            sched.start_time = start_t
            sched.end_time = end_t
            sched.notes = request.form.get('notes', '').strip() or None
            
            db.session.commit()
            if _is_ajax():
                return jsonify({'success': True, 'message': 'Desviación actualizada'})
            flash('Desviación actualizada', 'success')
            return redirect(url_for('hr.schedules', company_id=company_id))
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

    form_data = request.form if request.method == 'POST' else {
        'employee_id': sched.employee_id,
        'date': sched.date.strftime('%Y-%m-%d'),
        'start_time': sched.start_time.strftime('%H:%M'),
        'end_time': sched.end_time.strftime('%H:%M'),
        'notes': sched.notes
    }

    return render_template(
        'hr/schedule_form.html',
        company_id=company_id,
        schedule=sched,
        employees=all_employees,
        today=date.today().isoformat(),
        form_data=form_data,
    )


@hr.route('/<string:company_id>/hr/schedules/<int:sched_id>/delete', methods=['POST'])
@login_required
def delete_schedule(company_id, sched_id):
    company = resolve_company(company_id)
    company_id = company.id
    sched = WorkSchedule.query.filter_by(id=sched_id, company_id=company_id).first_or_404()
    try:
        sched.is_deleted = True
        db.session.commit()
        if _is_ajax():
            return jsonify({'success': True, 'message': 'Desviación eliminada'})
        flash('Desviación eliminada', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(str(e))
        if _is_ajax():
            return jsonify({'success': False, 'message': 'Ocurrió un error en la base de datos'}), 500
        flash('Ocurrió un error en la base de datos', 'error')
    return redirect(url_for('hr.schedules', company_id=company_id))


@hr.route('/<string:company_id>/hr/schedules/deviation/<int:sched_id>/view')
@login_required
def view_deviation(company_id, sched_id):
    company = resolve_company(company_id)
    company_id = company.id
    sched = WorkSchedule.query.filter_by(id=sched_id, company_id=company_id).first_or_404()
    return render_template(
        'hr/deviation_view.html',
        company_id=company_id,
        schedule=sched
    )
