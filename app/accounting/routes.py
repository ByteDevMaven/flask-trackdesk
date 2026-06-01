from datetime import datetime, UTC
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from app.models import Account, Project, Tag
from app.models.enums import AccountType
from . import accounting
from .services import AccountingService


@accounting.route('/<int:company_id>/accounting/')
@login_required
def index(company_id):
    data = AccountingService.get_dashboard_data(company_id)
    return render_template('accounting/dashboard.html', **data)


@accounting.route('/<int:company_id>/accounting/expenses/create', methods=['GET', 'POST'])
@login_required
def create_expense(company_id):
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            AccountingService.create_expense(company_id, request.form, request.files)

            if is_ajax:
                return jsonify({'success': True, 'message': 'Expense recorded successfully.'})

            flash('Expense recorded successfully!', 'success')
            return redirect(url_for('accounting.index', company_id=company_id))

        except ValueError as e:
            msg = str(e)
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'error')
        except Exception as e:
            msg = f'Error creating expense: {str(e)}'
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 500
            flash(msg, 'error')

    # GET
    expense_accounts = Account.query.filter_by(company_id=company_id).all()
    projects = Project.query.filter_by(company_id=company_id).all()
    tags = Tag.query.filter_by(company_id=company_id).all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(
            'accounting/partials/expense_form.html',
            company=company,
            accounts=expense_accounts,
            projects=projects,
            tags=tags,
            now=datetime.now(UTC),
        )

    return render_template(
        'accounting/expense_form.html',
        company=company,
        accounts=expense_accounts,
        projects=projects,
        tags=tags,
        now=datetime.now(UTC),
    )


@accounting.route('/<int:company_id>/accounting/projects/create', methods=['GET', 'POST'])
@login_required
def create_project(company_id):
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            AccountingService.create_project(company_id, request.form)

            if is_ajax:
                return jsonify({'success': True, 'message': 'Project created successfully.'})

            flash('Project created successfully.', 'success')
            return redirect(url_for('accounting.index', company_id=company_id))

        except ValueError as e:
            msg = str(e)
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'error')
            return redirect(url_for('accounting.create_project', company_id=company_id))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('accounting/partials/project_form.html', company=company)

    return render_template('accounting/project_form.html', company=company)


@accounting.route('/<int:company_id>/accounting/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account(company_id):
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            AccountingService.create_account(company_id, request.form)

            if is_ajax:
                return jsonify({'success': True, 'message': 'Cuenta creada con éxito.'})

            flash('Cuenta creada con éxito.', 'success')
            return redirect(url_for('accounting.chart_of_accounts', company_id=company_id))

        except ValueError as e:
            msg = str(e)
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'error')
            return redirect(url_for('accounting.chart_of_accounts', company_id=company_id))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('accounting/partials/account_form.html', company=company, AccountType=AccountType)

    return render_template('accounting/account_form.html', company=company, AccountType=AccountType)


@accounting.route('/<int:company_id>/accounting/ledger')
@login_required
def ledger(company_id):
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    entries = AccountingService.get_ledger_entries(company_id, search, start_date, end_date)
    projects = Project.query.filter_by(company_id=company_id).all()

    return render_template(
        'accounting/ledger.html',
        company=company,
        entries=entries,
        projects=projects,
        search=search,
        start_date=start_date,
        end_date=end_date
    )


@accounting.route('/<int:company_id>/accounting/accounts/generate-defaults', methods=['POST'])
@login_required
def generate_default_accounts(company_id):
    created_count = AccountingService.generate_default_accounts(company_id)

    if created_count > 0:
        flash(f'Se han generado {created_count} cuentas base con éxito.', 'success')
    else:
        flash('Todas las cuentas base ya existen en su catálogo.', 'info')

    return redirect(url_for('accounting.chart_of_accounts', company_id=company_id))


@accounting.route('/<int:company_id>/accounting/chart-of-accounts')
@login_required
def chart_of_accounts(company_id):
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    accounts = Account.query.filter_by(company_id=company_id).order_by(Account.type, Account.name).all()
    projects = Project.query.filter_by(company_id=company_id).all()

    return render_template(
        'accounting/chart_of_accounts.html',
        company=company,
        accounts=accounts,
        projects=projects
    )


@accounting.route('/<int:company_id>/accounting/reports')
@login_required
def reports(company_id):
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    report_type = request.args.get('report_type', 'income_statement').strip()
    export = request.args.get('export', '').strip()

    try:
        report_data, total = AccountingService.compute_report(company_id, report_type, start_date, end_date)
    except ValueError:
        flash("Invalid date format.", "error")
        return redirect(url_for('accounting.index', company_id=company_id))

    if not start_date:
        from datetime import datetime, UTC
        now = datetime.now(UTC)
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
    if not end_date:
        from datetime import datetime, UTC
        end_date = datetime.now(UTC).strftime('%Y-%m-%d')

    if export == 'csv':
        return AccountingService.export_report_csv(company_id, report_type, report_data, total, start_date, end_date)

    return render_template(
        'accounting/reports.html',
        company=company,
        start_date=start_date,
        end_date=end_date,
        report_type=report_type,
        report_data=report_data,
        total=total
    )


@accounting.route('/<int:company_id>/accounting/tags/create', methods=['GET', 'POST'])
@login_required
def create_tag(company_id):
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            AccountingService.create_tag(company_id, request.form)
            msg = "Etiqueta creada exitosamente"
            if is_ajax:
                return jsonify({'success': True, 'message': msg})
            flash(msg, "success")
        except ValueError as e:
            msg = str(e)
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, "error")

        return redirect(url_for('accounting.index', company_id=company_id))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tags = Tag.query.filter_by(company_id=company_id).all()
        return render_template('accounting/partials/tag_form.html', company=company, tags=tags)

    return redirect(url_for('accounting.index', company_id=company_id))


@accounting.route('/<int:company_id>/accounting/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(company_id, tag_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    AccountingService.delete_tag(company_id, tag_id)

    if is_ajax:
        return jsonify({'success': True, 'message': 'Etiqueta eliminada'})
    flash("Etiqueta eliminada", "success")
    return redirect(url_for('accounting.index', company_id=company_id))
