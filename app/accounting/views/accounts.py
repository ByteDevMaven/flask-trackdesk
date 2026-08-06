from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import Account, Project, Tag, Transaction
from app.models.enums import AccountType, TransactionType
from app.utils import resolve_company

from .. import accounting
from ..services import AccountingService
from .common import _company_url_id, _is_ajax, _sidebar_ctx


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
