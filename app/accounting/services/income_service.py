"""Income (revenue) CRUD service."""
from app.models import db, Account, Transaction
from app.models.enums import AccountType, TransactionType

from ._helpers import _parse_date, _get_period_bounds
from ._balance import _create_balanced_transaction


class IncomeService:

    @staticmethod
    def record_income(company_id: int, data) -> Transaction:
        """
        Record an income / revenue event.

        Double-entry:
          DR  Cash / AR Account  (amount)
          CR  Revenue Account    (amount)
        """
        revenue_account_id_str = data.get('revenue_account_id', '').strip()
        amount_str = data.get('amount', '').strip()
        if not revenue_account_id_str or not amount_str:
            raise ValueError('Cuenta de ingresos y monto son requeridos.')
        try:
            revenue_account_id = int(revenue_account_id_str)
            amount = round(float(amount_str), 2)
        except ValueError:
            raise ValueError('Valores inválidos.')
        if amount <= 0:
            raise ValueError('El monto debe ser mayor a cero.')

        revenue_account = Account.query.filter_by(id=revenue_account_id, company_id=company_id).first()
        if not revenue_account:
            raise ValueError('Cuenta de ingresos no encontrada.')
        if revenue_account.type != AccountType.revenue:
            raise ValueError('La cuenta seleccionada debe ser una cuenta de ingresos.')

        income_date = _parse_date(data.get('date', '').strip())
        description = data.get('description', '').strip()
        client_name = data.get('client_name', '').strip()
        project_id = int(p) if (p := data.get('project_id', '').strip()) else None

        debit_account = _resolve_debit_account(company_id, data.get('debit_account_id', '').strip())

        memo = description or f"Ingreso — {revenue_account.name}"
        if client_name:
            memo = f"{memo} ({client_name})"

        txn = _create_balanced_transaction(
            company_id=company_id,
            date=income_date,
            memo=memo,
            transaction_type=TransactionType.income,
            entries=[
                {'account_id': debit_account.id, 'debit': amount, 'credit': 0.0,
                 'description': memo, 'project_id': project_id, 'tags': []},
                {'account_id': revenue_account_id, 'debit': 0.0, 'credit': amount,
                 'description': memo, 'project_id': project_id, 'tags': []},
            ],
            reference_type='Income',
        )
        db.session.commit()
        return txn

    @staticmethod
    def get_income_transactions(company_id: int, search: str = '',
                                start_date: str = '', end_date: str = '',
                                page: int = 1, per_page: int = 30):
        q = (
            Transaction.query
            .filter_by(company_id=company_id, transaction_type=TransactionType.income, is_voided=False)
            .order_by(Transaction.date.desc())
        )
        if search:
            q = q.filter(Transaction.memo.ilike(f'%{search}%'))
        if start_date or end_date:
            start_dt, end_dt = _get_period_bounds(start_date, end_date)
            if start_date:
                q = q.filter(Transaction.date >= start_dt)
            if end_date:
                q = q.filter(Transaction.date <= end_dt)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def update_income(company_id: int, txn_id: int, data) -> Transaction:
        """Void old income transaction and create a corrected one."""
        old_txn = Transaction.query.filter_by(
            id=txn_id, company_id=company_id, transaction_type=TransactionType.income
        ).first_or_404()

        revenue_account_id_str = data.get('revenue_account_id', '').strip()
        amount_str = data.get('amount', '').strip()
        if not revenue_account_id_str or not amount_str:
            raise ValueError('Cuenta de ingresos y monto son requeridos.')
        try:
            revenue_account_id = int(revenue_account_id_str)
            amount = round(float(amount_str), 2)
        except ValueError:
            raise ValueError('Valores inválidos.')
        if amount <= 0:
            raise ValueError('El monto debe ser mayor a cero.')

        revenue_account = Account.query.filter_by(id=revenue_account_id, company_id=company_id).first()
        if not revenue_account:
            raise ValueError('Cuenta de ingresos no encontrada.')
        if revenue_account.type != AccountType.revenue:
            raise ValueError('La cuenta seleccionada debe ser una cuenta de ingresos.')

        income_date = _parse_date(data.get('date', '').strip())
        description = data.get('description', '').strip()
        client_name = data.get('client_name', '').strip()
        project_id = int(p) if (p := data.get('project_id', '').strip()) else None

        debit_account = _resolve_debit_account(company_id, data.get('debit_account_id', '').strip())

        old_txn.is_voided = True
        old_txn.voided_reason = 'Replaced by edit'

        memo = description or f"Ingreso — {revenue_account.name}"
        if client_name:
            memo = f"{memo} ({client_name})"

        new_txn = _create_balanced_transaction(
            company_id=company_id,
            date=income_date,
            memo=f"[EDIT] {memo}",
            transaction_type=TransactionType.income,
            entries=[
                {'account_id': debit_account.id, 'debit': amount, 'credit': 0.0,
                 'description': memo, 'project_id': project_id, 'tags': []},
                {'account_id': revenue_account_id, 'debit': 0.0, 'credit': amount,
                 'description': memo, 'project_id': project_id, 'tags': []},
            ],
            reference_type='Income',
        )
        db.session.commit()
        return new_txn

    @staticmethod
    def delete_income_txn(company_id: int, txn_id: int) -> None:
        """Void an income transaction (soft delete)."""
        txn = Transaction.query.filter_by(
            id=txn_id, company_id=company_id, transaction_type=TransactionType.income
        ).first_or_404()
        if txn.is_voided:
            raise ValueError('Esta transacción ya está anulada.')
        txn.is_voided = True
        txn.voided_reason = 'Eliminado por el usuario'
        db.session.commit()


# ── Internal helper ────────────────────────────────────────────────────────

def _resolve_debit_account(company_id: int, debit_account_id_str: str) -> Account:
    if debit_account_id_str:
        account = Account.query.filter_by(
            id=int(debit_account_id_str), company_id=company_id
        ).first()
    else:
        account = Account.query.filter(
            Account.company_id == company_id,
            Account.name.ilike('%caja%') | Account.name.ilike('%banco%') | Account.name.ilike('%cash%')
        ).first()
    if not account:
        raise ValueError('No se encontró una cuenta de efectivo o por cobrar.')
    if account.type != AccountType.asset:
        raise ValueError('La cuenta de débito debe ser un activo (caja, banco o por cobrar).')
    return account
