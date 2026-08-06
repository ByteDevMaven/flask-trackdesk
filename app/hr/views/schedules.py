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


@hr.route('/<string:company_id>/hr/schedules')
@login_required
def schedules(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    return render_template(
        'hr/schedules.html',
        company_id=company_id
    )


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
