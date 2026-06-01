import io
import csv
import os
import uuid
from datetime import datetime, UTC

from flask import current_app, Response
from flask_login import current_user

from app.models import db, Company, Account, Expense, LedgerEntry, Project, Tag
from app.models.enums import AccountType
from app.models.report import Report


def _allowed_file(filename: str) -> bool:
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _save_receipt(file) -> str | None:
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


class AccountingService:

    # ── Dashboard ──────────────────────────────────────────────────────────

    @staticmethod
    def get_dashboard_data(company_id: int) -> dict:
        company = Company.query.get_or_404(company_id)

        accounts = Account.query.filter_by(company_id=company.id).all()
        projects = Project.query.filter_by(company_id=company.id).all()
        expenses = Expense.query.filter_by(company_id=company.id).order_by(Expense.date.desc()).limit(10).all()
        all_expenses = Expense.query.filter_by(company_id=company.id).all()

        total_expenses = float(db.session.query(db.func.sum(Expense.amount)).filter_by(company_id=company.id).scalar() or 0.0)

        type_totals: dict[str, float] = {}
        for acc in accounts:
            key = acc.type.value
            type_totals[key] = type_totals.get(key, 0.0) + float(acc.balance or 0.0)

        tag_totals: dict[str, float] = {}
        for e in all_expenses:
            if not e.tags:
                tag_totals['Sin Etiqueta'] = tag_totals.get('Sin Etiqueta', 0.0) + float(e.amount)
            for t in e.tags:
                tag_totals[t.name] = tag_totals.get(t.name, 0.0) + float(e.amount)

        expense_stats_rows = (
            db.session.query(
                Expense.project_id,
                db.func.count(Expense.id),
                db.func.sum(Expense.amount)
            )
            .filter(Expense.company_id == company.id, Expense.project_id.isnot(None))
            .group_by(Expense.project_id)
            .all()
        )
        expense_counts = {row[0]: row[1] for row in expense_stats_rows}
        project_spent = {row[0]: float(row[2] or 0.0) for row in expense_stats_rows}

        return {
            'company': company,
            'accounts': accounts,
            'expenses': expenses,
            'projects': projects,
            'total_expenses': total_expenses,
            'total_projects': len(projects),
            'total_accounts': len(accounts),
            'type_totals': type_totals,
            'tag_totals': tag_totals,
            'expense_counts': expense_counts,
            'project_spent': project_spent,
        }

    # ── Expenses ───────────────────────────────────────────────────────────

    @staticmethod
    def create_expense(company_id: int, data, files=None) -> Expense:
        account_id_str = data.get('account_id', '').strip()
        amount_str = data.get('amount', '').strip()

        if not account_id_str or not amount_str:
            raise ValueError('Account and amount are required.')

        account_id = int(account_id_str)
        amount = float(amount_str)
        date_str = data.get('date', '').strip()
        description = data.get('description', '').strip()
        project_id_str = data.get('project_id', '').strip()
        project_id = int(project_id_str) if project_id_str else None
        expense_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now(UTC)

        tag_ids = data.getlist('tags[]')
        selected_tags = Tag.query.filter(Tag.id.in_([int(tid) for tid in tag_ids if tid])).all() if tag_ids else []

        receipt_url = None
        if files and 'receipt_file' in files:
            receipt_url = _save_receipt(files['receipt_file'])

        expense = Expense(
            company_id=company_id,
            account_id=account_id,
            project_id=project_id,
            amount=amount,
            date=expense_date,
            description=description,
            receipt_url=receipt_url,
            tags=selected_tags,
        )
        db.session.add(expense)
        db.session.flush()

        # Double-entry ledger
        cash_account = Account.query.filter_by(company_id=company_id, name='Caja y Bancos').first()
        if not cash_account:
            cash_account = Account.query.filter_by(company_id=company_id, type=AccountType.asset).first()

        account = Account.query.get(account_id)
        is_revenue = account and account.type.value == 'revenue'

        if account:
            account.balance = float(account.balance or 0.0) + amount
        if cash_account:
            if is_revenue:
                cash_account.balance = float(cash_account.balance or 0.0) + amount
            else:
                cash_account.balance = float(cash_account.balance or 0.0) - amount

        if cash_account:
            if is_revenue:
                entries = [
                    LedgerEntry(company_id=company_id, account_id=cash_account.id, project_id=project_id,
                                date=expense_date, description=f"Cobro: {description}",
                                debit=amount, credit=0.0, reference_type='Income', reference_id=expense.id, tags=selected_tags),
                    LedgerEntry(company_id=company_id, account_id=account_id, project_id=project_id,
                                date=expense_date, description=f"Ingreso: {description}",
                                debit=0.0, credit=amount, reference_type='Income', reference_id=expense.id, tags=selected_tags),
                ]
            else:
                entries = [
                    LedgerEntry(company_id=company_id, account_id=account_id, project_id=project_id,
                                date=expense_date, description=f"Gasto: {description}",
                                debit=amount, credit=0.0, reference_type='Expense', reference_id=expense.id, tags=selected_tags),
                    LedgerEntry(company_id=company_id, account_id=cash_account.id, project_id=project_id,
                                date=expense_date, description=f"Pago por: {description}",
                                debit=0.0, credit=amount, reference_type='Expense', reference_id=expense.id, tags=selected_tags),
                ]
            db.session.add_all(entries)

        db.session.commit()
        return expense

    # ── Projects ───────────────────────────────────────────────────────────

    @staticmethod
    def create_project(company_id: int, data) -> Project:
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        budget_str = data.get('budget', '').strip()

        if not name:
            raise ValueError('Project name is required.')

        try:
            budget = float(budget_str) if budget_str else 0.0
        except ValueError:
            budget = 0.0

        project = Project(company_id=company_id, name=name, description=description, budget=budget)
        db.session.add(project)
        db.session.commit()
        return project

    # ── Accounts ───────────────────────────────────────────────────────────

    @staticmethod
    def create_account(company_id: int, data) -> Account:
        name = data.get('name', '').strip()
        account_type = data.get('type', '').strip()
        description = data.get('description', '').strip()
        balance_str = data.get('balance', '0.0').strip()

        if not name or not account_type:
            raise ValueError('El nombre y el tipo de cuenta son requeridos.')

        try:
            balance = float(balance_str) if balance_str else 0.0
            act_type_enum = AccountType(account_type)
        except ValueError:
            raise ValueError('Valores inválidos.')

        account = Account(
            company_id=company_id,
            name=name,
            type=act_type_enum,
            description=description,
            balance=balance
        )
        db.session.add(account)
        db.session.commit()
        return account

    @staticmethod
    def generate_default_accounts(company_id: int) -> int:
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
            exists = Account.query.filter_by(company_id=company.id, name=def_acc['name'], type=def_acc['type']).first()
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

        return created_count

    # ── Ledger ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_ledger_entries(company_id: int, search: str, start_date: str, end_date: str) -> list:
        query = LedgerEntry.query.filter_by(company_id=company_id)

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

        return query.order_by(LedgerEntry.date.desc(), LedgerEntry.id.desc()).all()

    # ── Reports ────────────────────────────────────────────────────────────

    @staticmethod
    def compute_report(company_id: int, report_type: str, start_date: str, end_date: str) -> tuple[dict, object]:
        if not start_date:
            now = datetime.now(UTC)
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now(UTC).strftime('%Y-%m-%d')

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

        report_data = {}
        total: object = 0.0

        if report_type == 'income_statement':
            entries = LedgerEntry.query.join(Account).filter(
                LedgerEntry.company_id == company_id,
                LedgerEntry.date >= start_dt,
                LedgerEntry.date <= end_dt,
                Account.type.in_([AccountType.revenue, AccountType.expense])
            ).all()

            report_data = {'revenue': {}, 'expense': {}}
            for entry in entries:
                acc_type = entry.account.type.value
                acc_name = entry.account.name
                net = float(entry.credit - entry.debit) if acc_type == 'revenue' else float(entry.debit - entry.credit)
                report_data[acc_type][acc_name] = report_data[acc_type].get(acc_name, 0.0) + net

            total_revenue = sum(report_data['revenue'].values())
            total_expense = sum(report_data['expense'].values())
            total = total_revenue - total_expense

        elif report_type == 'balance_sheet':
            entries = LedgerEntry.query.join(Account).filter(
                LedgerEntry.company_id == company_id,
                LedgerEntry.date <= end_dt,
                Account.type.in_([AccountType.asset, AccountType.liability, AccountType.equity])
            ).all()

            report_data = {'asset': {}, 'liability': {}, 'equity': {}}
            for entry in entries:
                acc_type = entry.account.type.value
                acc_name = entry.account.name
                net = float(entry.debit - entry.credit) if acc_type == 'asset' else float(entry.credit - entry.debit)
                report_data[acc_type][acc_name] = report_data[acc_type].get(acc_name, 0.0) + net

            # Calculate net income for retained earnings
            ni_entries = LedgerEntry.query.join(Account).filter(
                LedgerEntry.company_id == company_id,
                LedgerEntry.date <= end_dt,
                Account.type.in_([AccountType.revenue, AccountType.expense])
            ).all()
            net_income = 0.0
            for entry in ni_entries:
                if entry.account.type.value == 'revenue':
                    net_income += float(entry.credit - entry.debit)
                else:
                    net_income -= float(entry.debit - entry.credit)

            report_data['equity']['Retained Earnings (Calculated)'] = float(report_data['equity'].get('Retained Earnings (Calculated)', 0.0)) + net_income
            total_equity = sum(report_data['equity'].values())
            total_liability = sum(report_data['liability'].values())
            total_asset = sum(report_data['asset'].values())

            total = {
                'assets': float(total_asset),
                'liabilities_and_equity': float(total_liability) + float(total_equity)
            }

        return report_data, total

    @staticmethod
    def export_report_csv(company_id: int, report_type: str, report_data: dict, total, start_date: str, end_date: str) -> Response:
        si = io.StringIO()
        cw = csv.writer(si)

        if report_type == 'income_statement':
            cw.writerow(['Account Type', 'Account Name', 'Amount'])
            for acc_name, amount in report_data['revenue'].items():
                cw.writerow(['Revenue', acc_name, f"{amount:.2f}"])
            for acc_name, amount in report_data['expense'].items():
                cw.writerow(['Expense', acc_name, f"{amount:.2f}"])
            cw.writerow([])
            cw.writerow(['Net Income', '', f"{total:.2f}"])
        else:
            cw.writerow(['Account Type', 'Account Name', 'Amount'])
            for acc_name, amount in report_data['asset'].items():
                cw.writerow(['Asset', acc_name, f"{amount:.2f}"])
            for acc_name, amount in report_data['liability'].items():
                cw.writerow(['Liability', acc_name, f"{amount:.2f}"])
            for acc_name, amount in report_data['equity'].items():
                cw.writerow(['Equity', acc_name, f"{amount:.2f}"])
            cw.writerow([])
            cw.writerow(['Total Assets', '', f"{total['assets']:.2f}"])
            cw.writerow(['Total Liabilities & Equity', '', f"{total['liabilities_and_equity']:.2f}"])

        rep = Report(
            company_id=company_id,
            title=f"{report_type.replace('_', ' ').title()} ({start_date} to {end_date})",
            report_type=report_type,
            generated_by=current_user.id
        )
        db.session.add(rep)
        db.session.commit()

        return Response(
            si.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={report_type}_{end_date}.csv"}
        )

    # ── Tags ───────────────────────────────────────────────────────────────

    @staticmethod
    def create_tag(company_id: int, data) -> Tag:
        name = data.get('name', '').strip()
        color_code = data.get('color_code', 'bg-slate-100 text-slate-700').strip()

        if not name:
            raise ValueError("El nombre de la etiqueta es requerido")

        existing = Tag.query.filter_by(company_id=company_id, name=name).first()
        if existing:
            raise ValueError("La etiqueta ya existe")

        tag = Tag(company_id=company_id, name=name, color_code=color_code)
        db.session.add(tag)
        db.session.commit()
        return tag

    @staticmethod
    def delete_tag(company_id: int, tag_id: int) -> None:
        tag = Tag.query.filter_by(id=tag_id, company_id=company_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
