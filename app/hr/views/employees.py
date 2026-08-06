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
