"""Project CRUD, tagging, and reporting service."""

from datetime import UTC, datetime

from flask_login import current_user
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models import db, Account, Expense, LedgerEntry, Project, Tag, Transaction
from app.models.document import Document
from app.models.enums import AccountType, DocumentType
from app.models.report import Report

from ._helpers import _get_period_bounds
from ._balance import (
    _active_expense_conditions,
    _active_ledger_conditions,
    _compute_balances_bulk,
    _expenses_by_account,
    _ledger_revenue_by_account,
    _period_expense_total,
    _period_revenue_total,
)


class ProjectService:

    # ── Projects ───────────────────────────────────────────────────────────

    @staticmethod
    def create_project(company_id: int, data) -> Project:
        name = data.get('name', '').strip()
        if not name:
            raise ValueError('El nombre del proyecto es requerido.')
        description = data.get('description', '').strip()
        budget_str = data.get('budget', '').strip()
        try:
            budget = float(budget_str) if budget_str else 0.0
        except ValueError:
            budget = 0.0
        project = Project(company_id=company_id, name=name, description=description, budget=budget)
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def update_project(company_id: int, project_id: int, data) -> Project:
        project = Project.query.filter_by(id=project_id, company_id=company_id).first_or_404()
        name = data.get('name', '').strip()
        if not name:
            raise ValueError('El nombre del proyecto es requerido.')
        project.name = name
        project.description = data.get('description', '').strip()
        budget_str = data.get('budget', '').strip()
        try:
            project.budget = float(budget_str) if budget_str else 0.0
        except ValueError:
            project.budget = 0.0
        status = data.get('status', 'active').strip()
        if status in ('active', 'completed', 'on_hold', 'cancelled'):
            project.status = status
        db.session.commit()
        return project

    @staticmethod
    def delete_project_safe(company_id: int, project_id: int) -> None:
        project = Project.query.filter_by(id=project_id, company_id=company_id).first_or_404()
        Expense.query.filter_by(project_id=project_id, company_id=company_id).update({'project_id': None})
        LedgerEntry.query.filter_by(project_id=project_id, company_id=company_id).update({'project_id': None})
        project.is_deleted = True
        project.deleted_at = datetime.now(UTC)
        project.status = 'cancelled'
        db.session.commit()

    @staticmethod
    def get_projects_list(company_id: int) -> list:
        projects = Project.query.filter_by(company_id=company_id).order_by(Project.name).all()
        
        result = []
        for p in projects:
            expense_total = _period_expense_total(company_id, project_id=p.id)
            income_total = _period_revenue_total(company_id, project_id=p.id)
            
            invoice_counts = db.session.query(
                Document.status,
                func.count(Document.id)
            ).filter(
                Document.project_id == p.id,
                Document.company_id == company_id,
                Document.type == DocumentType.invoice
            ).group_by(Document.status).all()
            
            invoices_by_status = {status.value: count for status, count in invoice_counts}
            total_invoices = sum(invoices_by_status.values())
            
            result.append({
                'project': p,
                'expense_total': expense_total,
                'income_total': income_total,
                'net': round(income_total - expense_total, 2),
                'budget_used_pct': round((expense_total / float(p.budget) * 100), 1) if p.budget and float(p.budget) > 0 else 0,
                'total_invoices': total_invoices,
                'invoices_by_status': invoices_by_status,
            })
        return result

    @staticmethod
    def get_project_detail(
        company_id: int,
        project_id: int,
        expense_page: int = 1,
        income_page: int = 1,
        invoice_page: int = 1,
        per_page: int = 8,
    ) -> dict:
        """Return full P&L breakdown for a project."""
        project = Project.query.filter_by(id=project_id, company_id=company_id).first_or_404()

        expense_stmt = (
            select(Expense)
            .options(joinedload(Expense.account))
            .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
            .where(
                Expense.company_id == company_id,
                Expense.project_id == project_id,
                _active_expense_conditions(),
            )
            .order_by(Expense.date.desc())
        )
        expense_pagination = db.paginate(
            expense_stmt,
            page=max(expense_page, 1),
            per_page=per_page,
            error_out=False,
        )
        expenses = (
            db.session.execute(
                expense_stmt
            )
            .unique()
            .scalars()
            .all()
        )

        income_query = (
            LedgerEntry.query
            .join(Account, LedgerEntry.account_id == Account.id)
            .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
            .filter(
                LedgerEntry.company_id == company_id,
                LedgerEntry.project_id == project_id,
                Account.type == AccountType.revenue,
                _active_ledger_conditions(),
            )
            .order_by(LedgerEntry.date.desc())
        )
        income_pagination = income_query.paginate(
            page=max(income_page, 1),
            per_page=per_page,
            error_out=False,
        )
        income_entries = income_query.all()

        total_expenses = round(sum(float(e.amount) for e in expenses), 2)
        total_income = round(
            sum(float(e.credit) - float(e.debit) for e in income_entries),
            2,
        )
        net = round(total_income - total_expenses, 2)
        budget = float(project.budget or 0)
        budget_remaining = round(budget - total_expenses, 2)

        monthly: dict = {}
        for e in expenses:
            key = e.date.strftime('%Y-%m') if e.date else 'N/A'
            monthly.setdefault(key, {'expense': 0.0, 'income': 0.0})
            monthly[key]['expense'] = round(monthly[key]['expense'] + float(e.amount), 2)
        for e in income_entries:
            key = e.date.strftime('%Y-%m') if e.date else 'N/A'
            monthly.setdefault(key, {'expense': 0.0, 'income': 0.0})
            monthly[key]['income'] = round(
                monthly[key]['income'] + float(e.credit) - float(e.debit), 2
            )

        all_ledger = (
            LedgerEntry.query
            .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
            .filter(
                LedgerEntry.project_id == project_id,
                LedgerEntry.company_id == company_id,
                _active_ledger_conditions(),
            )
            .order_by(LedgerEntry.date.desc())
            .limit(100)
            .all()
        )

        invoice_query = (
            Document.query
            .filter_by(project_id=project_id, company_id=company_id, type=DocumentType.invoice)
            .order_by(Document.issued_date.desc())
        )
        invoice_pagination = invoice_query.paginate(
            page=max(invoice_page, 1),
            per_page=per_page,
            error_out=False,
        )
        invoices = invoice_query.all()

        invoice_counts = db.session.query(
            Document.status,
            func.count(Document.id)
        ).filter(
            Document.project_id == project_id,
            Document.company_id == company_id,
            Document.type == DocumentType.invoice
        ).group_by(Document.status).all()

        invoices_by_status = {status.value: count for status, count in invoice_counts}
        total_invoices = sum(invoices_by_status.values())

        return {
            'project': project,
            'expenses': expense_pagination.items,
            'income_entries': income_pagination.items,
            'all_ledger': all_ledger,
            'invoices': invoice_pagination.items,
            'expense_pagination': expense_pagination,
            'income_pagination': income_pagination,
            'invoice_pagination': invoice_pagination,
            'invoices_by_status': invoices_by_status,
            'total_invoices': total_invoices,
            'total_expenses': total_expenses,
            'total_income': total_income,
            'net': net,
            'budget': budget,
            'budget_remaining': budget_remaining,
            'monthly': monthly,
        }

    # ── Tags ───────────────────────────────────────────────────────────────

    @staticmethod
    def create_tag(company_id: int, data) -> Tag:
        name = data.get('name', '').strip()
        color_code = data.get('color_code', 'bg-slate-100 text-slate-700').strip()
        if not name:
            raise ValueError('El nombre de la etiqueta es requerido.')
        if Tag.query.filter_by(company_id=company_id, name=name).first():
            raise ValueError('La etiqueta ya existe.')
        tag = Tag(company_id=company_id, name=name, color_code=color_code)
        db.session.add(tag)
        db.session.commit()
        return tag

    @staticmethod
    def delete_tag(company_id: int, tag_id: int) -> None:
        tag = Tag.query.filter_by(id=tag_id, company_id=company_id).first_or_404()
        tag.is_deleted = True
        tag.deleted_at = datetime.now(UTC)
        db.session.commit()

    # ── Reports ────────────────────────────────────────────────────────────

    @staticmethod
    def compute_report(company_id: int, report_type: str,
                       start_date: str, end_date: str) -> tuple[dict, object]:
        start_dt, end_dt = _get_period_bounds(start_date, end_date)

        report_data: dict = {}
        total: object = 0.0

        if report_type == 'income_statement':
            report_data = {
                'revenue': _ledger_revenue_by_account(company_id, start_dt, end_dt),
                'expense': _expenses_by_account(company_id, start_dt, end_dt),
            }
            total_revenue = sum(report_data['revenue'].values())
            total_expense = sum(report_data['expense'].values())
            total = round(total_revenue - total_expense, 2)

        elif report_type == 'balance_sheet':
            entries = (
                LedgerEntry.query
                .join(Account, LedgerEntry.account_id == Account.id)
                .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
                .filter(
                    LedgerEntry.company_id == company_id,
                    LedgerEntry.date <= end_dt,
                    Account.type.in_([AccountType.asset, AccountType.liability, AccountType.equity]),
                    _active_ledger_conditions(),
                )
                .all()
            )

            report_data = {'asset': {}, 'liability': {}, 'equity': {}}
            for entry in entries:
                acc_type = entry.account.type.value
                acc_name = entry.account.name
                if acc_type == 'asset':
                    net = float(entry.debit) - float(entry.credit)
                else:
                    net = float(entry.credit) - float(entry.debit)
                report_data[acc_type][acc_name] = report_data[acc_type].get(acc_name, 0.0) + net

            net_income = round(
                _period_revenue_total(company_id, end_dt=end_dt)
                - _period_expense_total(company_id, end_dt=end_dt),
                2,
            )

            retained_key = 'Resultado del Período (Calculado)'
            report_data['equity'][retained_key] = (
                report_data['equity'].get(retained_key, 0.0) + net_income
            )

            total_asset = sum(report_data['asset'].values())
            total_liability = sum(report_data['liability'].values())
            total_equity = sum(report_data['equity'].values())

            total = {
                'assets': round(total_asset, 2),
                'liabilities': round(total_liability, 2),
                'equity': round(total_equity, 2),
                'liabilities_and_equity': round(total_liability + total_equity, 2),
            }

        elif report_type == 'cash_flow':
            net_income = round(
                _period_revenue_total(company_id, start_dt, end_dt)
                - _period_expense_total(company_id, start_dt, end_dt),
                2,
            )

            cash_like = ['caja', 'banco', 'cash']
            non_cash_asset_entries = (
                LedgerEntry.query
                .join(Account)
                .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
                .filter(
                    LedgerEntry.company_id == company_id,
                    LedgerEntry.date >= start_dt,
                    LedgerEntry.date <= end_dt,
                    Account.type == AccountType.asset,
                    ~db.or_(*[Account.name.ilike(f'%{k}%') for k in cash_like]),
                    _active_ledger_conditions(),
                )
                .all()
            )
            investing_change = sum(
                float(e.debit) - float(e.credit) for e in non_cash_asset_entries
            )

            liability_entries = (
                LedgerEntry.query
                .join(Account)
                .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
                .filter(
                    LedgerEntry.company_id == company_id,
                    LedgerEntry.date >= start_dt,
                    LedgerEntry.date <= end_dt,
                    Account.type.in_([AccountType.liability, AccountType.equity]),
                    _active_ledger_conditions(),
                )
                .all()
            )
            financing_change = sum(
                float(e.credit) - float(e.debit) for e in liability_entries
            )

            report_data = {
                'operating': {'Resultado neto del período': round(net_income, 2)},
                'investing': {'Cambio en activos no corrientes': round(-investing_change, 2)},
                'financing': {'Cambio en pasivos y patrimonio': round(financing_change, 2)},
            }
            total = round(net_income - investing_change + financing_change, 2)

        return report_data, total

    @staticmethod
    def export_report_excel(company_id: int, report_type: str,
                            report_data: dict, total,
                            start_date: str, end_date: str):
        
        headers = []
        rows = []

        if report_type == 'income_statement':
            headers = ['Tipo', 'Cuenta', 'Monto']
            for acc_name, amount in report_data.get('revenue', {}).items():
                rows.append(['Ingreso', acc_name, amount])
            for acc_name, amount in report_data.get('expense', {}).items():
                rows.append(['Gasto', acc_name, amount])
            rows.append([])
            rows.append(['Resultado Neto', '', total])

        elif report_type == 'balance_sheet':
            headers = ['Tipo', 'Cuenta', 'Monto']
            for acc_name, amount in report_data.get('asset', {}).items():
                rows.append(['Activo', acc_name, amount])
            for acc_name, amount in report_data.get('liability', {}).items():
                rows.append(['Pasivo', acc_name, amount])
            for acc_name, amount in report_data.get('equity', {}).items():
                rows.append(['Patrimonio', acc_name, amount])
            rows.append([])
            rows.append(['Total Activos', '', total['assets']])
            rows.append(['Total Pasivos + Patrimonio', '', total['liabilities_and_equity']])

        elif report_type == 'cash_flow':
            headers = ['Sección', 'Concepto', 'Monto']
            for sec, items in report_data.items():
                for concept, amount in items.items():
                    rows.append([sec.title(), concept, amount])
            rows.append([])
            rows.append(['Flujo Neto', '', total])

        rep = Report(
            company_id=company_id,
            title=f"{report_type.replace('_', ' ').title()} ({start_date} to {end_date})",
            report_type=report_type,
            generated_by=current_user.id,
        )
        db.session.add(rep)
        db.session.commit()

        from app.utils import export_excel_response
        return export_excel_response(f'{report_type}_{end_date}', headers, rows)
