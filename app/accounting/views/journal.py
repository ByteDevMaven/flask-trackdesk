from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import Account, Project, Tag, Transaction
from app.models.enums import AccountType, TransactionType
from app.utils import resolve_company

from .. import accounting
from ..services import AccountingService
from .common import _company_url_id, _is_ajax, _sidebar_ctx


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
            AccountingService.create_journal_entry(company_id, request.form, request.files)
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
    from app.models import AccountingAttachment
    ctx = dict(
        company=company,
        company_url_id=company_url_id,
        accounts=accounts,
        existing_attachments=[],
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
            updated_txn = AccountingService.update_journal_entry(company_id, txn_id, request.form, request.files)
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
    
    from app.models import AccountingAttachment
    existing_attachments = AccountingAttachment.query.filter_by(
        reference_type='Journal',
        reference_id=transaction.id,
        is_deleted=False
    ).all()
    
    ctx = dict(
        company=company,
        company_url_id=company_url_id,
        accounts=accounts,
        transaction=transaction,
        existing_attachments=existing_attachments,
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


@accounting.route('/<string:company_id>/accounting/attachments/<int:att_id>/delete', methods=['POST'])
@login_required
def delete_attachment(company_id, att_id):
    company = resolve_company(company_id)
    company_id = company.id
    from app.models import AccountingAttachment, db
    
    attachment = AccountingAttachment.query.filter_by(id=att_id, company_id=company_id).first_or_404()
    attachment.is_deleted = True
    attachment.deleted_at = datetime.now(UTC)
    db.session.commit()
    
    if _is_ajax():
        return jsonify({'success': True, 'message': 'Archivo adjunto eliminado.'})
    flash('Archivo adjunto eliminado.', 'success')
    return redirect(request.referrer or url_for('accounting.index', company_id=company_id))
