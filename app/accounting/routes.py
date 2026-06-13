from app.utils import resolve_company
from datetime import datetime, UTC
from flask import make_response, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from app.models import Account, Project, Tag, Transaction
from app.models.enums import AccountType, TransactionType
from . import accounting
from .services import AccountingService


# ─── Sidebar helper ───────────────────────────────────────────────────────────

def _sidebar_ctx(company_id: int) -> dict:
    return {
        'company_id': company_id,
        'AccountType': AccountType,
    }


def _company_url_id(company) -> str:
    """URL segment for company-scoped routes (slug preferred, else numeric id)."""
    return company.slug if company.slug else str(company.id)


def _is_ajax() -> bool:
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


# ─── Dashboard ────────────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/')
@login_required
def index(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    data = AccountingService.get_dashboard_data(company_id)
    return render_template('accounting/dashboard.html', **data)


# ─── Expenses ─────────────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/expenses')
@login_required
def expenses_list(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    search = request.args.get('search', '').strip()
    account_id = request.args.get('account_id', '').strip()
    status = request.args.get('status', '').strip()
    category = request.args.get('category', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', 1, type=int)

    pagination = AccountingService.get_expenses(
        company_id,
        search=search,
        account_id=int(account_id) if account_id else None,
        status=status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
    )

    export = request.args.get('export', '').strip()
    if export == 'excel':
        export_pagination = AccountingService.get_expenses(
            company_id, search=search, account_id=int(account_id) if account_id else None,
            status=status, category=category, start_date=start_date, end_date=end_date, page=1, per_page=100000
        )
        headers = ['Fecha', 'Descripción', 'Vendedor', 'Cuenta', 'Categoría', 'Estado', 'Monto']
        rows = [
            [
                exp.date.strftime('%Y-%m-%d') if exp.date else '',
                exp.description,
                exp.vendor_display,
                exp.account.name if exp.account else '',
                exp.category or '',
                exp.status.value,
                exp.amount
            ] for exp in export_pagination.items
        ]
        from app.utils import export_excel_response
        return export_excel_response(f'Gastos_{company.name}', headers, rows)

    accounts = (
        Account.query
        .filter_by(company_id=company_id, is_active=True, type=AccountType.expense)
        .order_by(Account.code, Account.name)
        .all()
    )
    projects = Project.query.filter_by(company_id=company_id).all()
    from app.models.enums import ExpenseStatus
    return render_template(
        'accounting/expenses.html',
        company=company,
        pagination=pagination,
        expenses=pagination.items,
        accounts=accounts,
        projects=projects,
        ExpenseStatus=ExpenseStatus,
        search=search,
        account_id=account_id,
        status=status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        **_sidebar_ctx(company_id),
    )


@accounting.route('/<string:company_id>/accounting/expenses/create', methods=['GET', 'POST'])
@login_required
def create_expense(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.create_expense(company_id, request.form, request.files)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Gasto registrado exitosamente.'})
            flash('Gasto registrado exitosamente.', 'success')
            return redirect(url_for('accounting.expenses_list', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error: {e}'}), 500
            flash(f'Error: {e}', 'error')

    expense_accounts = (
        Account.query
        .filter_by(company_id=company_id, is_active=True, type=AccountType.expense)
        .order_by(Account.code, Account.name)
        .all()
    )
    projects = Project.query.filter_by(company_id=company_id).all()
    tags = Tag.query.filter_by(company_id=company_id).all()
    from app.models.enums import ExpenseStatus

    ctx = dict(
        company=company,
        accounts=expense_accounts,
        projects=projects,
        tags=tags,
        expense=None,
        ExpenseStatus=ExpenseStatus,
        now=datetime.now(UTC),
        **_sidebar_ctx(company_id),
    )

    if _is_ajax():
        return render_template('accounting/partials/expense_form.html', **ctx)
    return render_template('accounting/expense_form.html', **ctx)


@accounting.route('/<string:company_id>/accounting/expenses/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(company_id, expense_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company, Expense
    company = Company.query.get_or_404(company_id)
    expense = Expense.query.filter_by(id=expense_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.update_expense(company_id, expense_id, request.form, request.files)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Gasto actualizado exitosamente.'})
            flash('Gasto actualizado exitosamente.', 'success')
            return redirect(url_for('accounting.expenses_list', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error: {e}'}), 500
            flash(f'Error: {e}', 'error')

    expense_accounts = (
        Account.query
        .filter_by(company_id=company_id, is_active=True, type=AccountType.expense)
        .order_by(Account.code, Account.name)
        .all()
    )
    projects = Project.query.filter_by(company_id=company_id).all()
    tags = Tag.query.filter_by(company_id=company_id).all()
    from app.models.enums import ExpenseStatus

    ctx = dict(
        company=company,
        expense=expense,
        accounts=expense_accounts,
        projects=projects,
        tags=tags,
        ExpenseStatus=ExpenseStatus,
        now=datetime.now(UTC),
        **_sidebar_ctx(company_id),
    )

    if _is_ajax():
        return render_template('accounting/partials/expense_form.html', **ctx)
    return render_template('accounting/expense_form.html', **ctx)


@accounting.route('/<string:company_id>/accounting/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(company_id, expense_id):
    company = resolve_company(company_id)
    company_id = company.id
    is_ajax = _is_ajax()
    try:
        AccountingService.delete_expense(company_id, expense_id)
        if is_ajax:
            return jsonify({'success': True, 'message': 'Gasto eliminado.'})
        flash('Gasto eliminado.', 'success')
    except Exception as e:
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(str(e), 'error')
    return redirect(url_for('accounting.expenses_list', company_id=company_id))


# ─── Income ───────────────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/income')
@login_required
def income_list(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', 1, type=int)

    pagination = AccountingService.get_income_transactions(
        company_id, search=search, start_date=start_date, end_date=end_date, page=page
    )

    export = request.args.get('export', '').strip()
    if export == 'excel':
        export_pagination = AccountingService.get_income_transactions(
            company_id, search=search, start_date=start_date, end_date=end_date, page=1, per_page=100000
        )
        headers = ['Fecha', 'Descripción', 'Cliente', 'Cuenta Ingreso', 'Referencia', 'Monto']
        rows = [
            [
                txn.date.strftime('%Y-%m-%d') if txn.date else '',
                txn.memo,
                txn.client_name or '',
                txn.entries[1].account.name if len(txn.entries) > 1 and txn.entries[1].account else '',
                txn.reference or '',
                txn.total_amount()
            ] for txn in export_pagination.items
        ]
        from app.utils import export_excel_response
        return export_excel_response(f'Ingresos_{company.name}', headers, rows)

    return render_template(
        'accounting/income.html',
        company=company,
        pagination=pagination,
        transactions=pagination.items,
        search=search,
        start_date=start_date,
        end_date=end_date,
        **_sidebar_ctx(company_id),
    )


@accounting.route('/<string:company_id>/accounting/income/create', methods=['GET', 'POST'])
@login_required
def create_income(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.record_income(company_id, request.form)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Ingreso registrado exitosamente.'})
            flash('Ingreso registrado exitosamente.', 'success')
            return redirect(url_for('accounting.income_list', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error: {e}'}), 500
            flash(f'Error: {e}', 'error')

    revenue_accounts = Account.query.filter_by(
        company_id=company_id, is_active=True, type=AccountType.revenue
    ).order_by(Account.code, Account.name).all()
    asset_accounts = Account.query.filter_by(
        company_id=company_id, is_active=True, type=AccountType.asset
    ).order_by(Account.code, Account.name).all()
    projects = Project.query.filter_by(company_id=company_id).all()

    ctx = dict(
        company=company,
        revenue_accounts=revenue_accounts,
        asset_accounts=asset_accounts,
        projects=projects,
        transaction=None,
        now=datetime.now(UTC),
        **_sidebar_ctx(company_id),
    )

    if _is_ajax():
        return render_template('accounting/partials/income_form.html', **ctx)
    return render_template('accounting/income_form.html', **ctx)


@accounting.route('/<string:company_id>/accounting/income/<int:txn_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_income(company_id, txn_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    transaction = Transaction.query.filter_by(id=txn_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.update_income(company_id, txn_id, request.form)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Ingreso actualizado exitosamente.'})
            flash('Ingreso actualizado exitosamente.', 'success')
            return redirect(url_for('accounting.income_list', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error: {e}'}), 500
            flash(f'Error: {e}', 'error')

    revenue_accounts = Account.query.filter_by(
        company_id=company_id, is_active=True, type=AccountType.revenue
    ).order_by(Account.code, Account.name).all()
    asset_accounts = Account.query.filter_by(
        company_id=company_id, is_active=True, type=AccountType.asset
    ).order_by(Account.code, Account.name).all()
    projects = Project.query.filter_by(company_id=company_id).all()

    # Parse existing entry data from the transaction
    debit_entry = next((e for e in transaction.entries if e.debit > 0), None)
    credit_entry = next((e for e in transaction.entries if e.credit > 0), None)

    ctx = dict(
        company=company,
        transaction=transaction,
        revenue_accounts=revenue_accounts,
        asset_accounts=asset_accounts,
        projects=projects,
        debit_entry=debit_entry,
        credit_entry=credit_entry,
        now=datetime.now(UTC),
        **_sidebar_ctx(company_id),
    )

    if _is_ajax():
        return render_template('accounting/partials/income_form.html', **ctx)
    return render_template('accounting/income_form.html', **ctx)


@accounting.route('/<string:company_id>/accounting/income/<int:txn_id>/delete', methods=['POST'])
@login_required
def delete_income(company_id, txn_id):
    company = resolve_company(company_id)
    company_id = company.id
    is_ajax = _is_ajax()
    try:
        AccountingService.delete_income_txn(company_id, txn_id)
        if is_ajax:
            return jsonify({'success': True, 'message': 'Ingreso anulado exitosamente.'})
        flash('Ingreso anulado exitosamente.', 'success')
    except ValueError as e:
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 400
        flash(str(e), 'error')
    except Exception as e:
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(str(e), 'error')
    return redirect(url_for('accounting.income_list', company_id=company_id))


# ─── Journal Entries ──────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/journal')
@login_required
def journal_list(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', 1, type=int)

    pagination = AccountingService.get_journal_entries(
        company_id, search=search, start_date=start_date, end_date=end_date, page=page
    )

    export = request.args.get('export', '').strip()
    if export == 'excel':
        export_pagination = AccountingService.get_journal_entries(
            company_id, search=search, start_date=start_date, end_date=end_date, page=1, per_page=100000
        )
        headers = ['Fecha', 'Tipo', 'Descripción', 'Referencia', 'Cuenta', 'Débito', 'Crédito']
        rows = []
        for txn in export_pagination.items:
            for entry in txn.entries:
                rows.append([
                    txn.date.strftime('%Y-%m-%d') if txn.date else '',
                    txn.transaction_type.label_es,
                    txn.memo,
                    txn.reference or '',
                    entry.account.name if entry.account else '',
                    entry.debit,
                    entry.credit
                ])
        from app.utils import export_excel_response
        return export_excel_response(f'Libro_Diario_{company.name}', headers, rows)

    balances = AccountingService.get_account_balances_bulk(company_id)

    from app.models import Expense
    expense_id_by_txn = {
        e.transaction_id: e.id
        for e in Expense.query.filter(
            Expense.company_id == company_id,
            Expense.transaction_id.isnot(None),
        ).all()
    }

    return render_template(
        'accounting/journal.html',
        company=company,
        company_url_id=_company_url_id(company),
        pagination=pagination,
        transactions=pagination.items,
        expense_id_by_txn=expense_id_by_txn,
        balances=balances,
        search=search,
        start_date=start_date,
        end_date=end_date,
        **_sidebar_ctx(company_id),
    )


@accounting.route('/<string:company_id>/accounting/journal/create', methods=['GET', 'POST'])
@login_required
def create_journal_entry(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    company_url_id = _company_url_id(company)

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.create_journal_entry(company_id, request.form)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Asiento contable creado.'})
            flash('Asiento contable creado.', 'success')
            return redirect(url_for('accounting.journal_list', company_id=company_url_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error: {e}'}), 500
            flash(f'Error: {e}', 'error')

    accounts = Account.query.filter_by(company_id=company_id, is_active=True).order_by(Account.type, Account.code, Account.name).all()
    ctx = dict(
        company=company,
        company_url_id=company_url_id,
        accounts=accounts,
        now=datetime.now(UTC),
        **_sidebar_ctx(company_id),
    )
    if _is_ajax():
        return render_template('accounting/partials/journal_form.html', **ctx)
    return render_template('accounting/journal_form.html', **ctx)


@accounting.route('/<string:company_id>/accounting/journal/<int:txn_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_journal_entry(company_id, txn_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company, Transaction
    company = Company.query.get_or_404(company_id)
    company_url_id = _company_url_id(company)
    transaction = Transaction.query.filter_by(id=txn_id, company_id=company_id).first_or_404()

    if transaction.transaction_type != TransactionType.journal:
        msg = (
            'Solo se pueden editar asientos manuales aquí. '
            'Edite gastos e ingresos desde Gastos o Ingresos.'
        )
        if _is_ajax():
            return jsonify({'success': False, 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('accounting.journal_list', company_id=company_url_id))

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            updated_txn = AccountingService.update_journal_entry(company_id, txn_id, request.form)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Asiento contable actualizado.'})
            flash('Asiento contable actualizado.', 'success')
            return redirect(url_for('accounting.journal_list', company_id=company_url_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error al actualizar: {str(e)}'}), 500
            flash(f'Error al actualizar el asiento: {str(e)}', 'error')
    
    # GET request or error recovery - render form with existing data
    accounts = Account.query.filter_by(company_id=company_id, is_active=True).order_by(Account.type, Account.code, Account.name).all()
    ctx = dict(
        company=company,
        company_url_id=company_url_id,
        accounts=accounts,
        transaction=transaction,
        now=datetime.now(UTC),
        **_sidebar_ctx(company_id),
    )
    if _is_ajax():
        return render_template('accounting/partials/journal_form.html', **ctx)
    return render_template('accounting/journal_form.html', **ctx)


@accounting.route('/<string:company_id>/accounting/journal/<int:txn_id>/void', methods=['POST'])
@login_required
def void_transaction(company_id, txn_id):
    company = resolve_company(company_id)
    company_id = company.id
    is_ajax = _is_ajax()
    reason = request.form.get('reason', '').strip()
    try:
        AccountingService.void_transaction(company_id, txn_id, reason)
        if is_ajax:
            return jsonify({'success': True, 'message': 'Transacción anulada.'})
        flash('Transacción anulada.', 'success')
    except (ValueError, Exception) as e:
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 400
        flash(str(e), 'error')
    return redirect(url_for('accounting.journal_list', company_id=company_id))


@accounting.route('/<string:company_id>/accounting/journal/<int:txn_id>/delete', methods=['POST'])
@login_required
def delete_journal_entry(company_id, txn_id):
    company = resolve_company(company_id)
    company_id = company.id
    is_ajax = _is_ajax()
    try:
        AccountingService.delete_journal_entry(company_id, txn_id)
        if is_ajax:
            return jsonify({'success': True, 'message': 'Asiento contable eliminado.'})
        flash('Asiento contable eliminado.', 'success')
    except (ValueError, Exception) as e:
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 400
        flash(str(e), 'error')
    return redirect(url_for('accounting.journal_list', company_id=company_id))


# ─── Ledger ───────────────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/ledger')
@login_required
def ledger(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    account_id_str = request.args.get('account_id', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    page = request.args.get('page', 1, type=int)

    ledger_data = AccountingService.get_ledger_page(
        company_id,
        account_id=int(account_id_str) if account_id_str else None,
        start_date=start_date,
        end_date=end_date,
        page=page,
    )

    export = request.args.get('export', '').strip()
    if export == 'excel':
        export_data = AccountingService.get_ledger_page(
            company_id, account_id=int(account_id_str) if account_id_str else None,
            start_date=start_date, end_date=end_date, page=1, per_page=100000
        )
        headers = ['Fecha', 'Cuenta', 'Transacción', 'Referencia', 'Débito', 'Crédito', 'Saldo Móvil']
        rows = []
        for entry in export_data['pagination'].items:
            rows.append([
                entry.transaction.date.strftime('%Y-%m-%d') if entry.transaction and entry.transaction.date else '',
                entry.account.name if entry.account else '',
                entry.transaction.memo if entry.transaction else '',
                entry.transaction.reference if entry.transaction else '',
                entry.debit,
                entry.credit,
                entry.running_balance
            ])
        from app.utils import export_excel_response
        return export_excel_response(f'Libro_Mayor_{company.name}', headers, rows)

    return render_template(
        'accounting/ledger.html',
        company=company,
        **ledger_data,
        **_sidebar_ctx(company_id),
    )


# ─── Chart of Accounts ────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/chart-of-accounts')
@login_required
def chart_of_accounts(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    accounts = Account.query.filter_by(company_id=company_id).order_by(Account.type, Account.code, Account.name).all()
    balances = AccountingService.get_account_balances_bulk(company_id)

    export = request.args.get('export', '').strip()
    if export == 'excel':
        headers = ['Código', 'Nombre', 'Tipo', 'Estado', 'Saldo']
        rows = []
        for acc in accounts:
            rows.append([
                acc.code or '',
                acc.name,
                acc.type.label_es,
                'Activa' if acc.is_active else 'Inactiva',
                balances.get(acc.id, 0.0)
            ])
        from app.utils import export_excel_response
        return export_excel_response(f'Catalogo_Cuentas_{company.name}', headers, rows)

    return render_template(
        'accounting/chart_of_accounts.html',
        company=company,
        accounts=accounts,
        balances=balances,
        **_sidebar_ctx(company_id),
    )


@accounting.route('/<string:company_id>/accounting/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.create_account(company_id, request.form)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Cuenta creada con éxito.'})
            flash('Cuenta creada con éxito.', 'success')
            return redirect(url_for('accounting.chart_of_accounts', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')

    if _is_ajax():
        return render_template('accounting/partials/account_form.html', company=company, account=None, AccountType=AccountType)
    return render_template('accounting/account_form.html', company=company, account=None, AccountType=AccountType)


@accounting.route('/<string:company_id>/accounting/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_account(company_id, account_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    account = Account.query.filter_by(id=account_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.update_account(company_id, account_id, request.form)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Cuenta actualizada.'})
            flash('Cuenta actualizada.', 'success')
            return redirect(url_for('accounting.chart_of_accounts', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')

    if _is_ajax():
        return render_template('accounting/partials/account_form.html', company=company, account=account, AccountType=AccountType)
    return render_template('accounting/account_form.html', company=company, account=account, AccountType=AccountType)


@accounting.route('/<string:company_id>/accounting/accounts/<int:account_id>/delete', methods=['POST'])
@login_required
def delete_account(company_id, account_id):
    company = resolve_company(company_id)
    company_id = company.id
    is_ajax = _is_ajax()
    try:
        AccountingService.delete_account_safe(company_id, account_id)
        if is_ajax:
            return jsonify({'success': True, 'message': 'Cuenta eliminada.'})
        flash('Cuenta eliminada.', 'success')
    except ValueError as e:
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 400
        flash(str(e), 'error')
    except Exception as e:
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(str(e), 'error')
    return redirect(url_for('accounting.chart_of_accounts', company_id=company_id))


@accounting.route('/<string:company_id>/accounting/accounts/generate-defaults', methods=['POST'])
@login_required
def generate_default_accounts(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    created_count = AccountingService.generate_default_accounts(company_id)
    if created_count > 0:
        flash(f'Se han generado {created_count} cuentas base con éxito.', 'success')
    else:
        flash('Todas las cuentas base ya existen en su catálogo.', 'info')
    return redirect(url_for('accounting.chart_of_accounts', company_id=company_id))


# ─── Trial Balance ────────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/trial-balance')
@login_required
def trial_balance(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    as_of_date = request.args.get('as_of', '').strip()
    data = AccountingService.get_trial_balance(company_id, as_of_date)

    export = request.args.get('export', '').strip()
    if export == 'excel':
        headers = ['Cuenta', 'Débito', 'Crédito']
        rows = []
        for line in data['rows']:
            rows.append([
                line['account'].name,
                line['debit'],
                line['credit'],
            ])
        rows.append(['Total', data['total_debit'], data['total_credit']])
        from app.utils import export_excel_response
        return export_excel_response(f'Balanza_de_Comprobacion_{company.name}', headers, rows)

    return render_template(
        'accounting/trial_balance.html',
        company=company,
        as_of_date=as_of_date,
        **data,
        **_sidebar_ctx(company_id),
    )


# ─── Reports ──────────────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/reports')
@login_required
def reports(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    report_type = request.args.get('report_type', 'income_statement').strip()
    export = request.args.get('export', '').strip()

    try:
        report_data, total = AccountingService.compute_report(company_id, report_type, start_date, end_date)
    except ValueError:
        flash('Formato de fecha inválido.', 'error')
        return redirect(url_for('accounting.index', company_id=company_id))

    if not start_date:
        now = datetime.now(UTC)
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now(UTC).strftime('%Y-%m-%d')

    if export == 'excel':
        return AccountingService.export_report_excel(company_id, report_type, report_data, total, start_date, end_date)

    if export == 'pdf':
        try:
            pdf_bytes, filename = AccountingService.export_report_pdf(
                company_id,
                report_type,
                report_data,
                total,
                start_date,
                end_date,
            )
        except ValueError as exc:
            flash(str(exc), 'error')
            return redirect(url_for('accounting.reports', company_id=_company_url_id(company), report_type=report_type, start_date=start_date, end_date=end_date))

        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return render_template(
        'accounting/reports.html',
        company=company,
        start_date=start_date,
        end_date=end_date,
        report_type=report_type,
        report_data=report_data,
        total=total,
        **_sidebar_ctx(company_id),
    )


# ─── Tags ─────────────────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/tags/create', methods=['GET', 'POST'])
@login_required
def create_tag(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.create_tag(company_id, request.form)
            msg = 'Etiqueta creada exitosamente'
            if is_ajax:
                return jsonify({'success': True, 'message': msg})
            flash(msg, 'success')
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        return redirect(url_for('accounting.index', company_id=company_id))

    if _is_ajax():
        tags = Tag.query.filter_by(company_id=company_id).all()
        return render_template('accounting/partials/tag_form.html', company=company, tags=tags)
    return redirect(url_for('accounting.index', company_id=company_id))


@accounting.route('/<string:company_id>/accounting/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(company_id, tag_id):
    company = resolve_company(company_id)
    company_id = company.id
    is_ajax = _is_ajax()
    AccountingService.delete_tag(company_id, tag_id)
    if is_ajax:
        return jsonify({'success': True, 'message': 'Etiqueta eliminada'})
    flash('Etiqueta eliminada', 'success')
    return redirect(url_for('accounting.index', company_id=company_id))


# ─── Projects ─────────────────────────────────────────────────────────────────

@accounting.route('/<string:company_id>/accounting/projects')
@login_required
def projects_list(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    projects_data = AccountingService.get_projects_list(company_id)

    export = request.args.get('export', '').strip()
    if export == 'excel':
        headers = ['Nombre', 'Estado', 'Ingresos', 'Gastos', 'Rentabilidad']
        rows = []
        for pdata in projects_data:
            p = pdata['project']
            rows.append([
                p.name,
                p.status.title() if isinstance(p.status, str) else p.status.value.title(),
                pdata['income_total'],
                pdata['expense_total'],
                pdata['net'],
            ])
        from app.utils import export_excel_response
        return export_excel_response(f'Proyectos_{company.name}', headers, rows)
    return render_template(
        'accounting/projects.html',
        company=company,
        projects_data=projects_data,
        **_sidebar_ctx(company_id),
    )


@accounting.route('/<string:company_id>/accounting/projects/<int:project_id>')
@login_required
def project_detail(company_id, project_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    expense_page = request.args.get('expense_page', 1, type=int)
    income_page = request.args.get('income_page', 1, type=int)
    invoice_page = request.args.get('invoice_page', 1, type=int)
    data = AccountingService.get_project_detail(
        company_id,
        project_id,
        expense_page=expense_page,
        income_page=income_page,
        invoice_page=invoice_page,
    )
    return render_template(
        'accounting/project_detail.html',
        company=company,
        **data,
        **_sidebar_ctx(company_id),
    )


@accounting.route('/<string:company_id>/accounting/projects/create', methods=['GET', 'POST'])
@login_required
def create_project(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.create_project(company_id, request.form)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Proyecto creado exitosamente.'})
            flash('Proyecto creado exitosamente.', 'success')
            return redirect(url_for('accounting.projects_list', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')

    if _is_ajax():
        return render_template('accounting/partials/project_form.html', company=company, project=None)
    return render_template('accounting/project_form.html', company=company, project=None)


@accounting.route('/<string:company_id>/accounting/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(company_id, project_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    project = Project.query.filter_by(id=project_id, company_id=company_id).first_or_404()

    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.update_project(company_id, project_id, request.form)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Proyecto actualizado exitosamente.'})
            flash('Proyecto actualizado exitosamente.', 'success')
            return redirect(url_for('accounting.projects_list', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')

    if _is_ajax():
        return render_template('accounting/partials/project_form.html', company=company, project=project)
    return render_template('accounting/project_form.html', company=company, project=project)


@accounting.route('/<string:company_id>/accounting/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(company_id, project_id):
    company = resolve_company(company_id)
    company_id = company.id
    is_ajax = _is_ajax()
    try:
        AccountingService.delete_project_safe(company_id, project_id)
        if is_ajax:
            return jsonify({'success': True, 'message': 'Proyecto eliminado.'})
        flash('Proyecto eliminado.', 'success')
    except Exception as e:
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(str(e), 'error')
    return redirect(url_for('accounting.projects_list', company_id=company_id))
