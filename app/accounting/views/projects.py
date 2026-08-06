from datetime import UTC, datetime

from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import Account, Project, Tag, Transaction
from app.models.enums import AccountType, TransactionType
from app.utils import resolve_company

from .. import accounting
from ..services import AccountingService
from .common import _company_url_id, _is_ajax, _sidebar_ctx


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
