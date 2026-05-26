from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required
from datetime import datetime, UTC
from werkzeug.utils import secure_filename
import os
import uuid

from app.models import db, Company, Account, Expense, LedgerEntry, Project
from app.models.enums import AccountType
from . import accounting


def _allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf','png','jpg','jpeg','webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _save_receipt(file):
    """Save uploaded receipt file; returns relative URL path or None."""
    if not file or file.filename == '':
        return None
    if not _allowed_file(file.filename):
        return None

    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', ''), 'receipts')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, unique_name))

    return f"uploads/receipts/{unique_name}"


@accounting.route('/<int:company_id>/accounting/')
@login_required
def index(company_id):
    company = Company.query.get_or_404(company_id)

    accounts = Account.query.filter_by(company_id=company.id).all()
    projects = Project.query.filter_by(company_id=company.id).all()
    expenses = Expense.query.filter_by(company_id=company.id).order_by(Expense.date.desc()).limit(10).all()

    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(company_id=company.id).scalar() or 0.0
    total_projects = len(projects)
    total_accounts = len(accounts)

    # Group totals by account type for the summary cards
    type_totals = {}
    for acc in accounts:
        key = acc.type.value
        type_totals[key] = type_totals.get(key, 0.0) + (acc.balance or 0.0)

    # Pre-compute expense count per project in one query to avoid N+1
    expense_count_rows = (
        db.session.query(Expense.project_id, db.func.count(Expense.id))
        .filter(Expense.company_id == company.id, Expense.project_id.isnot(None))
        .group_by(Expense.project_id)
        .all()
    )
    expense_counts = {row[0]: row[1] for row in expense_count_rows}

    return render_template(
        'accounting/dashboard.html',
        company=company,
        accounts=accounts,
        expenses=expenses,
        projects=projects,
        total_expenses=total_expenses,
        total_projects=total_projects,
        total_accounts=total_accounts,
        type_totals=type_totals,
        expense_counts=expense_counts,
    )


@accounting.route('/<int:company_id>/accounting/expenses/create', methods=['GET', 'POST'])
@login_required
def create_expense(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            account_id_str = request.form.get('account_id', '').strip()
            amount_str = request.form.get('amount', '').strip()

            if not account_id_str or not amount_str:
                msg = 'Account and amount are required.'
                if is_ajax:
                    return jsonify({'success': False, 'message': msg}), 400
                flash(msg, 'error')
                return redirect(url_for('accounting.create_expense', company_id=company.id))

            account_id = int(account_id_str)
            amount = float(amount_str)
            date_str = request.form.get('date', '').strip()
            description = request.form.get('description', '').strip()
            project_id_str = request.form.get('project_id', '').strip()
            project_id = int(project_id_str) if project_id_str else None
            expense_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now(UTC)

            # Handle receipt upload
            receipt_url = None
            if 'receipt_file' in request.files:
                receipt_url = _save_receipt(request.files['receipt_file'])

            expense = Expense(
                company_id=company.id,
                account_id=account_id,
                project_id=project_id,
                amount=amount,
                date=expense_date,
                description=description,
                receipt_url=receipt_url,
            )
            db.session.add(expense)
            db.session.flush()

            # Double-entry ledger
            cash_account = Account.query.filter_by(company_id=company.id, name='Caja y Bancos').first()
            if not cash_account:
                cash_account = Account.query.filter_by(company_id=company.id, type=AccountType.asset).first()

            # Update account balances directly for dashboard calculation
            account = Account.query.get(account_id)
            is_revenue = account and account.type.value == 'revenue'

            if account:
                account.balance = (account.balance or 0.0) + amount
            if cash_account:
                if is_revenue:
                    cash_account.balance = (cash_account.balance or 0.0) + amount
                else:
                    cash_account.balance = (cash_account.balance or 0.0) - amount

            if cash_account:
                if is_revenue:
                    debit_entry = LedgerEntry(
                        company_id=company.id,
                        account_id=cash_account.id,
                        project_id=project_id,
                        date=expense_date,
                        description=f"Cobro: {description}",
                        debit=amount,
                        credit=0.0,
                        reference_type='Income',
                        reference_id=expense.id,
                    )
                    credit_entry = LedgerEntry(
                        company_id=company.id,
                        account_id=account_id,
                        project_id=project_id,
                        date=expense_date,
                        description=f"Ingreso: {description}",
                        debit=0.0,
                        credit=amount,
                        reference_type='Income',
                        reference_id=expense.id,
                    )
                else:
                    debit_entry = LedgerEntry(
                        company_id=company.id,
                        account_id=account_id,
                        project_id=project_id,
                        date=expense_date,
                        description=f"Gasto: {description}",
                        debit=amount,
                        credit=0.0,
                        reference_type='Expense',
                        reference_id=expense.id,
                    )
                    credit_entry = LedgerEntry(
                        company_id=company.id,
                        account_id=cash_account.id,
                        project_id=project_id,
                        date=expense_date,
                        description=f"Pago por: {description}",
                        debit=0.0,
                        credit=amount,
                        reference_type='Expense',
                        reference_id=expense.id,
                    )
                db.session.add_all([debit_entry, credit_entry])

            db.session.commit()

            if is_ajax:
                return jsonify({'success': True, 'message': 'Expense recorded successfully.'})

            flash('Expense recorded successfully!', 'success')
            return redirect(url_for('accounting.index', company_id=company.id))

        except Exception as e:
            db.session.rollback()
            msg = f'Error creating expense: {str(e)}'
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 500
            flash(msg, 'error')

    # GET — check if this is a drawer/AJAX request
    expense_accounts = Account.query.filter_by(company_id=company.id).all()
    projects = Project.query.filter_by(company_id=company.id).all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(
            'accounting/partials/expense_form.html',
            company=company,
            accounts=expense_accounts,
            projects=projects,
            now=datetime.now(UTC),
        )

    return render_template(
        'accounting/expense_form.html',
        company=company,
        accounts=expense_accounts,
        projects=projects,
        now=datetime.now(UTC),
    )


@accounting.route('/<int:company_id>/accounting/projects/create', methods=['GET', 'POST'])
@login_required
def create_project(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        budget_str = request.form.get('budget', '').strip()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if not name:
            msg = 'Project name is required.'
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'error')
            return redirect(url_for('accounting.create_project', company_id=company.id))

        try:
            budget = float(budget_str) if budget_str else 0.0
        except ValueError:
            budget = 0.0

        project = Project(company_id=company.id, name=name, description=description, budget=budget)
        db.session.add(project)
        db.session.commit()

        if is_ajax:
            return jsonify({'success': True, 'message': 'Project created successfully.'})

        flash('Project created successfully.', 'success')
        return redirect(url_for('accounting.index', company_id=company.id))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('accounting/partials/project_form.html', company=company)

    return render_template('accounting/project_form.html', company=company)


@accounting.route('/<int:company_id>/accounting/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        account_type = request.form.get('type', '').strip()
        description = request.form.get('description', '').strip()
        balance_str = request.form.get('balance', '0.0').strip()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if not name or not account_type:
            msg = 'El nombre y el tipo de cuenta son requeridos.'
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'error')
            return redirect(url_for('accounting.chart_of_accounts', company_id=company.id))

        try:
            balance = float(balance_str) if balance_str else 0.0
            act_type_enum = AccountType(account_type)
        except ValueError:
            msg = 'Valores inválidos.'
            if is_ajax:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'error')
            return redirect(url_for('accounting.chart_of_accounts', company_id=company.id))

        account = Account(
            company_id=company.id,
            name=name,
            type=act_type_enum,
            description=description,
            balance=balance
        )
        db.session.add(account)
        db.session.commit()

        if is_ajax:
            return jsonify({'success': True, 'message': 'Cuenta creada con éxito.'})

        flash('Cuenta creada con éxito.', 'success')
        return redirect(url_for('accounting.chart_of_accounts', company_id=company.id))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('accounting/partials/account_form.html', company=company, AccountType=AccountType)

    return render_template('accounting/account_form.html', company=company, AccountType=AccountType)


@accounting.route('/<int:company_id>/accounting/ledger')
@login_required
def ledger(company_id):
    company = Company.query.get_or_404(company_id)
    
    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    query = LedgerEntry.query.filter_by(company_id=company.id)

    if search:
        query = query.join(Account).filter(
            db.or_(
                LedgerEntry.description.ilike(f'%{search}%'),
                LedgerEntry.reference_type.ilike(f'%{search}%'),
                Account.name.ilike(f'%{search}%')
            )
        )

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(LedgerEntry.date >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(LedgerEntry.date <= end_dt)
        except ValueError:
            pass

    entries = query.order_by(LedgerEntry.date.desc(), LedgerEntry.id.desc()).all()
    projects = Project.query.filter_by(company_id=company.id).all()
    
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
    company = Company.query.get_or_404(company_id)
    
    default_accounts = [
        {'name': 'Caja y Bancos', 'type': AccountType.asset, 'description': 'Cuenta principal de efectivo y saldos bancarios.'},
        {'name': 'Cuentas por Cobrar', 'type': AccountType.asset, 'description': 'Derechos de cobro a clientes por ventas a crédito.'},
        {'name': 'Inventario', 'type': AccountType.asset, 'description': 'Valor de las mercancías disponibles para la venta.'},
        {'name': 'Cuentas por Pagar', 'type': AccountType.liability, 'description': 'Obligaciones de pago con proveedores.'},
        {'name': 'Obligaciones Fiscales', 'type': AccountType.liability, 'description': 'Impuestos pendientes de pago.'},
        {'name': 'Capital Social', 'type': AccountType.equity, 'description': 'Aportaciones de los socios o propietarios.'},
        {'name': 'Resultados Acumulados', 'type': AccountType.equity, 'description': 'Ganancias o pérdidas acumuladas de ejercicios anteriores.'},
        {'name': 'Ventas de Servicios', 'type': AccountType.revenue, 'description': 'Ingresos generados por la prestación de servicios.'},
        {'name': 'Ventas de Productos', 'type': AccountType.revenue, 'description': 'Ingresos generados por la comercialización de bienes.'},
        {'name': 'Gastos de Alquiler', 'type': AccountType.expense, 'description': 'Pagos por arrendamiento de locales u oficinas.'},
        {'name': 'Servicios Públicos', 'type': AccountType.expense, 'description': 'Electricidad, agua, internet, telefonía, etc.'},
        {'name': 'Nóminas y Salarios', 'type': AccountType.expense, 'description': 'Remuneraciones al personal de la empresa.'},
        {'name': 'Gastos de Marketing', 'type': AccountType.expense, 'description': 'Publicidad, promoción y mercadeo.'},
        {'name': 'Otros Gastos', 'type': AccountType.expense, 'description': 'Gastos diversos no clasificados en otras cuentas.'},
    ]
    
    created_count = 0
    for def_acc in default_accounts:
        exists = Account.query.filter_by(
            company_id=company.id,
            name=def_acc['name'],
            type=def_acc['type']
        ).first()
        
        if not exists:
            account = Account(
                company_id=company.id,
                name=def_acc['name'],
                type=def_acc['type'],
                description=def_acc['description'],
                balance=0.0,
                is_default=True
            )
            db.session.add(account)
            created_count += 1
            
    if created_count > 0:
        db.session.commit()
        flash(f'Se han generado {created_count} cuentas base con éxito.', 'success')
    else:
        flash('Todas las cuentas base ya existen en su catálogo.', 'info')
        
    return redirect(url_for('accounting.chart_of_accounts', company_id=company.id))


@accounting.route('/<int:company_id>/accounting/chart-of-accounts')
@login_required
def chart_of_accounts(company_id):
    company = Company.query.get_or_404(company_id)
    accounts = Account.query.filter_by(company_id=company.id).order_by(Account.type, Account.name).all()
    projects = Project.query.filter_by(company_id=company.id).all()
    
    return render_template(
        'accounting/chart_of_accounts.html',
        company=company,
        accounts=accounts,
        projects=projects
    )
