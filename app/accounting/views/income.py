from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import Account, Project, Tag, Transaction
from app.models.enums import AccountType, TransactionType
from app.utils import resolve_company

from .. import accounting
from ..services import AccountingService
from .common import _company_url_id, _is_ajax, _sidebar_ctx


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
            AccountingService.record_income(company_id, request.form, request.files)
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
    from app.models import AccountingAttachment

    ctx = dict(
        company=company,
        revenue_accounts=revenue_accounts,
        asset_accounts=asset_accounts,
        projects=projects,
        transaction=None,
        existing_attachments=[],
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
            AccountingService.update_income(company_id, txn_id, request.form, request.files)
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
    
    from app.models import AccountingAttachment
    existing_attachments = AccountingAttachment.query.filter_by(
        reference_type='Income',
        reference_id=transaction.id,
        is_deleted=False
    ).all()

    ctx = dict(
        company=company,
        transaction=transaction,
        revenue_accounts=revenue_accounts,
        asset_accounts=asset_accounts,
        projects=projects,
        debit_entry=debit_entry,
        credit_entry=credit_entry,
        existing_attachments=existing_attachments,
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
