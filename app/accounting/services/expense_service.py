"""Expense CRUD service (create, read, update, delete)."""
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import db, Account, Expense, Tag, Transaction
from app.models.enums import AccountType, ExpenseStatus, TransactionType

from ._helpers import _parse_date, _get_period_bounds, _save_receipt
from ._balance import _active_expense_conditions, _create_balanced_transaction


class ExpenseService:

    @staticmethod
    def create_expense(company_id: int, data, files=None) -> Expense:
        """
        Record an expense.

        Double-entry:
          DR  Expense Account    (amount)
          CR  Cash / AP Account  (amount)
        """
        account_id_str = data.get('account_id', '').strip()
        amount_str = data.get('amount', '').strip()
        if not account_id_str or not amount_str:
            raise ValueError('Cuenta y monto son requeridos.')
        try:
            account_id = int(account_id_str)
            amount = round(float(amount_str), 2)
        except ValueError:
            raise ValueError('Valores de cuenta o monto inválidos.')
        if amount <= 0:
            raise ValueError('El monto debe ser mayor a cero.')

        expense_account = Account.query.filter_by(id=account_id, company_id=company_id).first()
        if not expense_account:
            raise ValueError('Cuenta de gasto no encontrada.')
        if expense_account.type != AccountType.expense:
            raise ValueError('La cuenta seleccionada debe ser una cuenta de gasto.')

        expense_date = _parse_date(data.get('date', '').strip())
        description = data.get('description', '').strip()
        vendor_name = data.get('vendor_name', '').strip()
        category = data.get('category', '').strip()
        project_id = int(p) if (p := data.get('project_id', '').strip()) else None
        supplier_id = int(s) if (s := data.get('supplier_id', '').strip()) else None

        try:
            status = ExpenseStatus(data.get('status', 'draft').strip())
        except ValueError:
            status = ExpenseStatus.draft

        tag_ids = data.getlist('tags[]') if hasattr(data, 'getlist') else []
        selected_tags = (
            Tag.query.filter(Tag.id.in_([int(tid) for tid in tag_ids if tid])).all()
            if tag_ids else []
        )

        receipt_url = None
        if files and 'receipt_file' in files:
            receipt_url = _save_receipt(files['receipt_file'])

        cash_account = _resolve_cash_account(company_id)

        expense = Expense(
            company_id=company_id,
            account_id=account_id,
            project_id=project_id,
            supplier_id=supplier_id,
            amount=amount,
            date=expense_date,
            description=description,
            vendor_name=vendor_name,
            category=category,
            receipt_url=receipt_url,
            status=status,
            tags=selected_tags,
        )
        db.session.add(expense)
        db.session.flush()

        if status != ExpenseStatus.draft:
            memo = description or f"Gasto — {expense_account.name}"
            txn = _create_balanced_transaction(
                company_id=company_id,
                date=expense_date,
                memo=memo,
                transaction_type=TransactionType.expense,
                entries=[
                    {'account_id': account_id, 'debit': amount, 'credit': 0.0,
                     'description': memo, 'project_id': project_id, 'tags': selected_tags},
                    {'account_id': cash_account.id, 'debit': 0.0, 'credit': amount,
                     'description': memo, 'project_id': project_id, 'tags': []},
                ],
                reference_type='Expense',
                reference_id=expense.id,
            )
            expense.transaction_id = txn.id

        db.session.commit()
        return expense

    @staticmethod
    def get_expenses(company_id: int, search: str = '', account_id: int = None,
                     status: str = '', category: str = '',
                     start_date: str = '', end_date: str = '',
                     page: int = 1, per_page: int = 30):
        stmt = (
            select(Expense)
            .options(joinedload(Expense.account))
            .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
            .where(
                Expense.company_id == company_id,
                _active_expense_conditions(),
            )
            .order_by(Expense.date.desc())
        )
        if search:
            stmt = stmt.where(
                Expense.description.ilike(f'%{search}%') |
                Expense.vendor_name.ilike(f'%{search}%') |
                Expense.category.ilike(f'%{search}%')
            )
        if account_id:
            stmt = stmt.where(Expense.account_id == account_id)
        if status:
            try:
                stmt = stmt.where(Expense.status == ExpenseStatus(status))
            except ValueError:
                pass
        if category:
            stmt = stmt.where(Expense.category.ilike(f'%{category}%'))
        if start_date or end_date:
            start_dt, end_dt = _get_period_bounds(start_date, end_date)
            if start_date:
                stmt = stmt.where(Expense.date >= start_dt)
            if end_date:
                stmt = stmt.where(Expense.date <= end_dt)
        return db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    @staticmethod
    def update_expense(company_id: int, expense_id: int, data, files=None) -> Expense:
        """Void old transaction and post a corrected balanced entry."""
        expense = Expense.query.filter_by(id=expense_id, company_id=company_id).first_or_404()

        account_id_str = data.get('account_id', '').strip()
        amount_str = data.get('amount', '').strip()
        if not account_id_str or not amount_str:
            raise ValueError('Cuenta y monto son requeridos.')
        try:
            account_id = int(account_id_str)
            amount = round(float(amount_str), 2)
        except ValueError:
            raise ValueError('Valores inválidos.')
        if amount <= 0:
            raise ValueError('El monto debe ser mayor a cero.')

        expense_account = Account.query.filter_by(id=account_id, company_id=company_id).first()
        if not expense_account:
            raise ValueError('Cuenta de gasto no encontrada.')
        if expense_account.type != AccountType.expense:
            raise ValueError('La cuenta seleccionada debe ser una cuenta de gasto.')

        expense_date = _parse_date(data.get('date', '').strip())
        description = data.get('description', '').strip()
        vendor_name = data.get('vendor_name', '').strip()
        category = data.get('category', '').strip()
        project_id = int(p) if (p := data.get('project_id', '').strip()) else None

        try:
            status = ExpenseStatus(data.get('status', 'draft').strip())
        except ValueError:
            status = ExpenseStatus.draft

        tag_ids = data.getlist('tags[]') if hasattr(data, 'getlist') else []
        selected_tags = (
            Tag.query.filter(Tag.id.in_([int(tid) for tid in tag_ids if tid])).all()
            if tag_ids else []
        )

        if expense.transaction_id:
            old_txn = Transaction.query.get(expense.transaction_id)
            if old_txn and not old_txn.is_voided:
                old_txn.is_voided = True
                old_txn.voided_reason = f'Replaced by edit of Expense #{expense_id}'

        if files and 'receipt_file' in files and files['receipt_file'].filename:
            new_receipt = _save_receipt(files['receipt_file'])
            if new_receipt:
                expense.receipt_url = new_receipt

        cash_account = _resolve_cash_account(company_id)

        expense.account_id = account_id
        expense.amount = amount
        expense.date = expense_date
        expense.description = description
        expense.vendor_name = vendor_name
        expense.category = category
        expense.project_id = project_id
        expense.status = status
        expense.tags = selected_tags

        if status != ExpenseStatus.draft:
            memo = description or f"Gasto — {expense_account.name}"
            txn = _create_balanced_transaction(
                company_id=company_id,
                date=expense_date,
                memo=f"[EDIT] {memo}",
                transaction_type=TransactionType.expense,
                entries=[
                    {'account_id': account_id, 'debit': amount, 'credit': 0.0,
                     'description': memo, 'project_id': project_id, 'tags': selected_tags},
                    {'account_id': cash_account.id, 'debit': 0.0, 'credit': amount,
                     'description': memo, 'project_id': project_id, 'tags': []},
                ],
                reference_type='Expense',
                reference_id=expense.id,
            )
            expense.transaction_id = txn.id
        else:
            expense.transaction_id = None

        db.session.commit()
        return expense

    @staticmethod
    def delete_expense(company_id: int, expense_id: int) -> None:
        expense = Expense.query.filter_by(id=expense_id, company_id=company_id).first_or_404()
        if expense.transaction_id:
            txn = Transaction.query.get(expense.transaction_id)
            if txn and not txn.is_voided:
                txn.is_voided = True
                txn.voided_reason = 'Gasto eliminado'
        expense.is_deleted = True
        expense.deleted_at = datetime.now(UTC)
        db.session.commit()


# ── Internal helper ────────────────────────────────────────────────────────

def _resolve_cash_account(company_id: int) -> Account:
    """Return the first cash/bank account for the company, or raise ValueError."""
    account = Account.query.filter(
        Account.company_id == company_id,
        Account.name.ilike('%caja%') | Account.name.ilike('%banco%') | Account.name.ilike('%cash%')
    ).first()
    if not account:
        account = Account.query.filter_by(company_id=company_id, type=AccountType.asset).first()
    if not account:
        raise ValueError(
            'No se encontró una cuenta de efectivo (Caja/Bancos). '
            'Por favor genere las cuentas base primero.'
        )
    return account
