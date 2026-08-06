from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import Account, Project, Tag, Transaction
from app.models.enums import AccountType, TransactionType
from app.utils import resolve_company

from .. import accounting
from ..services import AccountingService
from .common import _company_url_id, _is_ajax, _sidebar_ctx


@accounting.route('/<string:company_id>/accounting/loans')
@login_required
def loans_list(company_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    
    # Show all liability accounts, or those that have balances
    accounts = Account.query.filter_by(company_id=company_id, type=AccountType.liability, is_active=True).order_by(Account.name).all()
    balances = AccountingService.get_account_balances_bulk(company_id)
    
    return render_template(
        'accounting/loans.html',
        company=company,
        accounts=accounts,
        balances=balances,
        **_sidebar_ctx(company_id)
    )


@accounting.route('/<string:company_id>/accounting/loans/<int:account_id>/create', methods=['GET', 'POST'])
@login_required
def create_loan(company_id, account_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    account = Account.query.filter_by(id=account_id, company_id=company_id, type=AccountType.liability).first_or_404()
    
    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.record_loan(company_id, request.form, request.files)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Crédito registrado exitosamente.'})
            flash('Crédito registrado exitosamente.', 'success')
            return redirect(url_for('accounting.loans_list', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error: {e}'}), 500
            flash(f'Error: {e}', 'error')

    asset_accounts = Account.query.filter_by(company_id=company_id, type=AccountType.asset, is_active=True).order_by(Account.name).all()
    expense_accounts = Account.query.filter_by(company_id=company_id, type=AccountType.expense, is_active=True).order_by(Account.name).all()
    all_counterpart = asset_accounts + expense_accounts
    
    ctx = dict(
        company=company,
        account=account,
        counterpart_accounts=all_counterpart,
        now=datetime.now(UTC),
        **_sidebar_ctx(company_id)
    )
    if _is_ajax():
        return render_template('accounting/partials/loan_form.html', **ctx)
    return render_template('accounting/loan_form.html', **ctx)


@accounting.route('/<string:company_id>/accounting/loans/<int:account_id>/pay', methods=['GET', 'POST'])
@login_required
def pay_loan(company_id, account_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company
    company = Company.query.get_or_404(company_id)
    account = Account.query.filter_by(id=account_id, company_id=company_id, type=AccountType.liability).first_or_404()
    
    if request.method == 'POST':
        is_ajax = _is_ajax()
        try:
            AccountingService.record_loan_payment(company_id, request.form, request.files)
            if is_ajax:
                return jsonify({'success': True, 'message': 'Pago registrado exitosamente.'})
            flash('Pago registrado exitosamente.', 'success')
            return redirect(url_for('accounting.loans_list', company_id=company_id))
        except ValueError as e:
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(str(e), 'error')
        except Exception as e:
            if is_ajax:
                return jsonify({'success': False, 'message': f'Error: {e}'}), 500
            flash(f'Error: {e}', 'error')

    asset_accounts = Account.query.filter_by(company_id=company_id, type=AccountType.asset, is_active=True).order_by(Account.name).all()
    
    ctx = dict(
        company=company,
        account=account,
        payment_accounts=asset_accounts,
        now=datetime.now(UTC),
        **_sidebar_ctx(company_id)
    )
    if _is_ajax():
        return render_template('accounting/partials/loan_payment_form.html', **ctx)
    return render_template('accounting/loan_payment_form.html', **ctx)


@accounting.route('/<string:company_id>/accounting/transaction/<int:txn_id>/view')
@login_required
def view_transaction(company_id, txn_id):
    from app.utils import resolve_company
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import Company, Transaction, Expense, AccountingAttachment
    company = Company.query.get_or_404(company_id)
    transaction = Transaction.query.filter_by(id=txn_id, company_id=company_id).first_or_404()

    attachments = []
    if transaction.transaction_type.value == 'expense':
        expense = Expense.query.filter_by(transaction_id=txn_id).first()
        if expense:
            attachments = AccountingAttachment.query.filter_by(reference_type='Expense', reference_id=expense.id, is_deleted=False).all()
    elif transaction.transaction_type.value == 'income':
        attachments = AccountingAttachment.query.filter_by(reference_type='Income', reference_id=txn_id, is_deleted=False).all()
        payment_entry = next((e for e in transaction.entries if e.reference_type == 'Payment'), None)
        if payment_entry:
            attachments += AccountingAttachment.query.filter_by(reference_type='Payment', reference_id=payment_entry.reference_id, is_deleted=False).all()
    else:
        attachments = AccountingAttachment.query.filter_by(reference_type='Journal', reference_id=txn_id, is_deleted=False).all()

    if _is_ajax():
        return render_template('accounting/partials/transaction_view.html', company=company, transaction=transaction, attachments=attachments)
    
    return render_template(
        'accounting/transaction_view.html',
        company=company,
        transaction=transaction,
        attachments=attachments,
        **_sidebar_ctx(company_id)
    )
