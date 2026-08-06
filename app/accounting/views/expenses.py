from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import Account, Project, Tag, Transaction
from app.models.enums import AccountType, TransactionType
from app.utils import resolve_company

from .. import accounting
from ..services import AccountingService
from .common import _company_url_id, _is_ajax, _sidebar_ctx


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
    from app.models import AccountingAttachment

    ctx = dict(
        company=company,
        accounts=expense_accounts,
        projects=projects,
        tags=tags,
        expense=None,
        ExpenseStatus=ExpenseStatus,
        existing_attachments=[],
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
    from app.models import AccountingAttachment

    existing_attachments = AccountingAttachment.query.filter_by(
        reference_type='Expense',
        reference_id=expense.id,
        is_deleted=False
    ).all()

    ctx = dict(
        company=company,
        expense=expense,
        accounts=expense_accounts,
        projects=projects,
        tags=tags,
        ExpenseStatus=ExpenseStatus,
        existing_attachments=existing_attachments,
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
