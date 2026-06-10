"""
AccountingService — complete double-entry bookkeeping service.

Design rules (MUST be maintained):
  1. Every financial event creates exactly ONE Transaction row.
  2. Every Transaction contains >= 2 LedgerEntry rows whose
     total debits == total credits (balanced).
  3. Account balances are NEVER stored — always computed from LedgerEntry.
  4. Normal balance: Asset/Expense → debit; Liability/Equity/Revenue → credit.
"""

import io
import csv
import os
import uuid
from datetime import datetime, UTC
from decimal import Decimal

from flask import current_app, Response
from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.models import db, Company, Account, Expense, LedgerEntry, Project, Tag, Transaction
from app.models.enums import AccountType, ExpenseStatus, TransactionType, DocumentType, DocumentStatus
from app.models.document import Document
from app.models.report import Report


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _allowed_file(filename: str) -> bool:
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _save_receipt(file) -> str | None:
    """Save uploaded receipt; return relative URL or None."""
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


def _parse_date(date_str: str, default_now: bool = True) -> datetime:
    """Parse YYYY-MM-DD string → naive datetime. Falls back to now(UTC)."""
    if date_str:
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d')
        except ValueError:
            pass
    return datetime.now(UTC).replace(tzinfo=None) if default_now else None


def _make_naive(dt: datetime) -> datetime:
    """Strip timezone info so comparisons work with our stored naive datetimes."""
    if dt is None:
        return dt
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


def _get_period_bounds(start_date: str, end_date: str):
    """Return (start_dt, end_dt) as naive datetimes for the given period."""
    now = _make_naive(datetime.now(UTC))
    start_dt = _parse_date(start_date) if start_date else now.replace(day=1, hour=0, minute=0, second=0)
    raw_end = _parse_date(end_date) if end_date else now
    end_dt = raw_end.replace(hour=23, minute=59, second=59)
    return _make_naive(start_dt), _make_naive(end_dt)


# ─────────────────────────────────────────────────────────────────────────────
# Core balance computation
# ─────────────────────────────────────────────────────────────────────────────

def _active_ledger_conditions():
    """Ledger rows count only when unlinked or tied to a non-voided transaction."""
    return or_(
        LedgerEntry.transaction_id.is_(None),
        Transaction.is_voided.is_(False),
    )


def _active_expense_conditions():
    """Expense rows count only when unlinked or tied to a non-voided transaction."""
    return or_(
        Expense.transaction_id.is_(None),
        Transaction.is_voided.is_(False),
    )


def _ledger_revenue_by_account(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> dict[str, float]:
    q = (
        LedgerEntry.query
        .join(Account, LedgerEntry.account_id == Account.id)
        .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .filter(
            LedgerEntry.company_id == company_id,
            Account.type == AccountType.revenue,
            _active_ledger_conditions(),
        )
    )
    if project_id is not None:
        q = q.filter(LedgerEntry.project_id == project_id)
    if start_dt is not None:
        q = q.filter(LedgerEntry.date >= _make_naive(start_dt))
    if end_dt is not None:
        q = q.filter(LedgerEntry.date <= _make_naive(end_dt))

    result: dict[str, float] = {}
    for entry in q.all():
        acc_name = entry.account.name
        net = float(entry.credit) - float(entry.debit)
        result[acc_name] = round(result.get(acc_name, 0.0) + net, 2)
    return result


def _merge_account_amounts(*parts: dict[str, float]) -> dict[str, float]:
    merged: dict[str, float] = {}
    for part in parts:
        for name, amount in part.items():
            merged[name] = round(merged.get(name, 0.0) + float(amount), 2)
    return {name: amount for name, amount in merged.items() if round(amount, 2) != 0}


def _registered_expenses_by_account(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> dict[str, float]:
    """Gastos registrados en el módulo Gastos (tabla expenses)."""
    account_label = func.coalesce(Account.name, 'Sin cuenta')
    q = (
        db.session.query(
            account_label,
            func.coalesce(func.sum(Expense.amount), 0),
        )
        .select_from(Expense)
        .outerjoin(Account, Expense.account_id == Account.id)
        .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
        .filter(
            Expense.company_id == company_id,
            _active_expense_conditions(),
        )
    )
    if project_id is not None:
        q = q.filter(Expense.project_id == project_id)
    if start_dt is not None:
        q = q.filter(Expense.date >= _make_naive(start_dt))
    if end_dt is not None:
        q = q.filter(Expense.date <= _make_naive(end_dt))

    return {
        name: round(float(amount), 2)
        for name, amount in q.group_by(account_label).all()
        if float(amount) > 0
    }


def _ledger_manual_expenses_by_account(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> dict[str, float]:
    """
    Débitos/créditos en cuentas de gasto desde asientos manuales u otros
    movimientos que no son gastos registrados (reference_type != 'Expense').
    """
    q = (
        LedgerEntry.query
        .join(Account, LedgerEntry.account_id == Account.id)
        .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .filter(
            LedgerEntry.company_id == company_id,
            Account.type == AccountType.expense,
            _active_ledger_conditions(),
            or_(
                LedgerEntry.reference_type.is_(None),
                LedgerEntry.reference_type != 'Expense',
            ),
        )
    )
    if project_id is not None:
        q = q.filter(LedgerEntry.project_id == project_id)
    if start_dt is not None:
        q = q.filter(LedgerEntry.date >= _make_naive(start_dt))
    if end_dt is not None:
        q = q.filter(LedgerEntry.date <= _make_naive(end_dt))

    result: dict[str, float] = {}
    for entry in q.all():
        acc_name = entry.account.name
        net = float(entry.debit) - float(entry.credit)
        result[acc_name] = round(result.get(acc_name, 0.0) + net, 2)
    return result


def _expenses_by_account(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> dict[str, float]:
    """Registered gastos + manual journal activity on expense accounts."""
    return _merge_account_amounts(
        _registered_expenses_by_account(company_id, start_dt, end_dt, project_id),
        _ledger_manual_expenses_by_account(company_id, start_dt, end_dt, project_id),
    )


def _period_expense_total(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> float:
    return round(
        sum(_expenses_by_account(company_id, start_dt, end_dt, project_id).values()),
        2,
    )


def _period_revenue_total(
    company_id: int,
    start_dt: datetime = None,
    end_dt: datetime = None,
    project_id: int = None,
) -> float:
    return round(
        sum(_ledger_revenue_by_account(company_id, start_dt, end_dt, project_id).values()),
        2,
    )


def _recent_active_expenses(company_id: int, limit: int = 10) -> list[Expense]:
    return (
        db.session.execute(
            select(Expense)
            .options(joinedload(Expense.account))
            .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
            .where(
                Expense.company_id == company_id,
                _active_expense_conditions(),
            )
            .order_by(Expense.date.desc())
            .limit(limit)
        )
        .unique()
        .scalars()
        .all()
    )


def _compute_account_balance(account: Account, as_of: datetime = None) -> float:
    """
    Compute the current balance of an account from LedgerEntry rows.

    Normal balance rules:
      - Asset / Expense:         balance = SUM(debit) - SUM(credit)
      - Liability / Equity / Revenue: balance = SUM(credit) - SUM(debit)

    Returns a positive number when the account has a balance in its normal
    direction, negative when it's reversed.
    """
    q = (
        db.session.query(
            func.coalesce(func.sum(LedgerEntry.debit), 0).label('total_debit'),
            func.coalesce(func.sum(LedgerEntry.credit), 0).label('total_credit'),
        )
        .select_from(LedgerEntry)
        .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.company_id == account.company_id,
            _active_ledger_conditions(),
        )
    )
    if as_of:
        q = q.filter(LedgerEntry.date <= _make_naive(as_of))

    row = q.one()
    total_debit = float(row.total_debit)
    total_credit = float(row.total_credit)

    if account.type in (AccountType.asset, AccountType.expense):
        return round(total_debit - total_credit, 2)
    else:  # liability, equity, revenue
        return round(total_credit - total_debit, 2)


def _compute_balances_bulk(company_id: int, account_type_filter=None, as_of: datetime = None) -> dict[int, float]:
    """
    Compute balances for ALL accounts of a company in one query.
    Returns {account_id: balance}.
    """
    q = (
        db.session.query(
            LedgerEntry.account_id,
            Account.type,
            func.coalesce(func.sum(LedgerEntry.debit), 0).label('d'),
            func.coalesce(func.sum(LedgerEntry.credit), 0).label('c'),
        )
        .select_from(LedgerEntry)
        .join(Account, LedgerEntry.account_id == Account.id)
        .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
        .filter(
            LedgerEntry.company_id == company_id,
            _active_ledger_conditions(),
        )
    )
    if account_type_filter:
        if isinstance(account_type_filter, (list, tuple)):
            q = q.filter(Account.type.in_(account_type_filter))
        else:
            q = q.filter(Account.type == account_type_filter)
    if as_of:
        q = q.filter(LedgerEntry.date <= _make_naive(as_of))

    q = q.group_by(LedgerEntry.account_id, Account.type)
    rows = q.all()

    result: dict[int, float] = {}
    for account_id, acct_type, d, c in rows:
        d, c = float(d), float(c)
        if acct_type in (AccountType.asset, AccountType.expense):
            result[account_id] = round(d - c, 2)
        else:
            result[account_id] = round(c - d, 2)
    return result


def _create_balanced_transaction(
    company_id: int,
    date: datetime,
    memo: str,
    transaction_type: TransactionType,
    entries: list[dict],  # [{'account_id', 'debit', 'credit', 'description', 'project_id', 'tags'}]
    reference: str = None,
    reference_type: str = None,
    reference_id: int = None,
) -> Transaction:
    """
    Create a Transaction + LedgerEntry rows atomically.
    Raises ValueError if entries do not balance (total debit ≠ total credit).
    """
    total_debit = round(sum(float(e.get('debit', 0)) for e in entries), 2)
    total_credit = round(sum(float(e.get('credit', 0)) for e in entries), 2)
    if total_debit != total_credit:
        raise ValueError(
            f"Journal entry is not balanced: total debit {total_debit} ≠ total credit {total_credit}"
        )

    created_by_id = None
    try:
        created_by_id = current_user.id if current_user.is_authenticated else None
    except Exception:
        pass

    txn = Transaction(
        company_id=company_id,
        date=_make_naive(date),
        memo=memo,
        reference=reference,
        transaction_type=transaction_type,
        created_by=created_by_id,
    )
    db.session.add(txn)
    db.session.flush()  # get txn.id

    for e in entries:
        entry = LedgerEntry(
            company_id=company_id,
            account_id=e['account_id'],
            transaction_id=txn.id,
            project_id=e.get('project_id'),
            date=_make_naive(date),
            description=e.get('description', memo),
            debit=round(float(e.get('debit', 0)), 2),
            credit=round(float(e.get('credit', 0)), 2),
            reference_type=reference_type,
            reference_id=reference_id,
            tags=e.get('tags', []),
        )
        db.session.add(entry)

    return txn


# ─────────────────────────────────────────────────────────────────────────────
# AccountingService
# ─────────────────────────────────────────────────────────────────────────────

class AccountingService:

    # ── Dashboard ──────────────────────────────────────────────────────────

    @staticmethod
    def get_dashboard_data(company_id: int) -> dict:
        company = Company.query.get_or_404(company_id)

        accounts = Account.query.filter_by(company_id=company_id, is_active=True).order_by(Account.type, Account.name).all()
        projects = Project.query.filter_by(company_id=company_id).all()
        expenses = _recent_active_expenses(company_id, limit=10)
        recent_transactions = (
            Transaction.query
            .filter_by(company_id=company_id, is_voided=False)
            .order_by(Transaction.date.desc())
            .limit(15)
            .all()
        )

        # Compute all balances in one query
        balances = _compute_balances_bulk(company_id)

        # KPI aggregations from ledger
        now = _make_naive(datetime.now(UTC))
        month_start = now.replace(day=1, hour=0, minute=0, second=0)

        def _period_expense_sum(start=None, end=None):
            return _period_expense_total(company_id, start_dt=start, end_dt=end)

        # Revenue = net credits on revenue accounts (matches reports)
        revenue_month = _period_revenue_total(company_id, month_start, now)
        expenses_month = _period_expense_sum(month_start, now)
        net_income_month = round(revenue_month - expenses_month, 2)

        total_revenue = _period_revenue_total(company_id)
        total_expenses = _period_expense_sum()
        net_income_all = round(total_revenue - total_expenses, 2)

        # Cash balance = balance of first asset account named 'Caja'/'Bancos'/'Cash'
        cash_account = Account.query.filter(
            Account.company_id == company_id,
            Account.name.ilike('%caja%') | Account.name.ilike('%banco%') | Account.name.ilike('%cash%')
        ).first()
        cash_balance = balances.get(cash_account.id, 0.0) if cash_account else 0.0

        # AR / AP
        ar_account = Account.query.filter(
            Account.company_id == company_id,
            Account.name.ilike('%cobrar%') | Account.name.ilike('%receivable%')
        ).first()
        ap_account = Account.query.filter(
            Account.company_id == company_id,
            Account.name.ilike('%pagar%') | Account.name.ilike('%payable%')
        ).first()
        ar_balance = balances.get(ar_account.id, 0.0) if ar_account else 0.0
        ap_balance = balances.get(ap_account.id, 0.0) if ap_account else 0.0

        # Project spend from active expenses only
        expense_stats = (
            db.session.query(Expense.project_id, func.sum(Expense.amount))
            .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
            .filter(
                Expense.company_id == company_id,
                Expense.project_id.isnot(None),
                _active_expense_conditions(),
            )
            .group_by(Expense.project_id)
            .all()
        )
        project_spent = {row[0]: float(row[1] or 0) for row in expense_stats}

        # Tag totals for active expenses
        tag_totals: dict[str, float] = {}
        active_expense_rows = (
            db.session.execute(
                select(Expense)
                .options(joinedload(Expense.tags))
                .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
                .where(
                    Expense.company_id == company_id,
                    _active_expense_conditions(),
                )
            )
            .unique()
            .scalars()
            .all()
        )
        for e in active_expense_rows:
            if not e.tags:
                tag_totals['Sin Etiqueta'] = tag_totals.get('Sin Etiqueta', 0.0) + float(e.amount)
            for t in e.tags:
                tag_totals[t.name] = tag_totals.get(t.name, 0.0) + float(e.amount)

        return {
            'company': company,
            'accounts': accounts,
            'expenses': expenses,
            'recent_transactions': recent_transactions,
            'projects': projects,
            'balances': balances,
            # KPIs
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_income_all': net_income_all,
            'revenue_month': revenue_month,
            'expenses_month': expenses_month,
            'net_income_month': net_income_month,
            'cash_balance': cash_balance,
            'ar_balance': ar_balance,
            'ap_balance': ap_balance,
            # Legacy helpers for dashboard template
            'type_totals': {
                'revenue': total_revenue,
                'expense': total_expenses,
                'asset': sum(v for aid, v in balances.items()
                             if Account.query.get(aid) and Account.query.get(aid).type == AccountType.asset),
            },
            'tag_totals': tag_totals,
            'project_spent': project_spent,
            'expense_counts': {row[0]: row[1] for row in (
                db.session.query(Expense.project_id, func.count(Expense.id))
                .outerjoin(Transaction, Expense.transaction_id == Transaction.id)
                .filter(
                    Expense.company_id == company_id,
                    Expense.project_id.isnot(None),
                    _active_expense_conditions(),
                )
                .group_by(Expense.project_id)
                .all()
            )},
        }

    # ── Account balance ─────────────────────────────────────────────────────

    @staticmethod
    def get_account_balance(account: Account, as_of: datetime = None) -> float:
        return _compute_account_balance(account, as_of=as_of)

    @staticmethod
    def get_account_balances_bulk(company_id: int, as_of: datetime = None) -> dict[int, float]:
        return _compute_balances_bulk(company_id, as_of=as_of)

    # ── Expenses ───────────────────────────────────────────────────────────

    @staticmethod
    def create_expense(company_id: int, data, files=None) -> Expense:
        """
        Record an expense.

        Double-entry:
          DR  Expense Account       (amount)
          CR  Cash / AP Account     (amount)
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

        date_str = data.get('date', '').strip()
        expense_date = _parse_date(date_str)

        description = data.get('description', '').strip()
        vendor_name = data.get('vendor_name', '').strip()
        category = data.get('category', '').strip()
        project_id_str = data.get('project_id', '').strip()
        project_id = int(project_id_str) if project_id_str else None
        supplier_id_str = data.get('supplier_id', '').strip()
        supplier_id = int(supplier_id_str) if supplier_id_str else None
        status_str = data.get('status', 'draft').strip()
        try:
            status = ExpenseStatus(status_str)
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

        # Resolve the credit (cash/AP) account
        cash_account = Account.query.filter(
            Account.company_id == company_id,
            Account.name.ilike('%caja%') | Account.name.ilike('%banco%') | Account.name.ilike('%cash%')
        ).first()
        if not cash_account:
            cash_account = Account.query.filter_by(company_id=company_id, type=AccountType.asset).first()
        if not cash_account:
            raise ValueError(
                'No se encontró una cuenta de efectivo (Caja/Bancos). '
                'Por favor genere las cuentas base primero.'
            )

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
        db.session.flush()  # get expense.id

        # Create balanced journal entry
        memo = description or f"Gasto — {expense_account.name}"
        txn = _create_balanced_transaction(
            company_id=company_id,
            date=expense_date,
            memo=memo,
            transaction_type=TransactionType.expense,
            entries=[
                {
                    'account_id': account_id,           # DR expense
                    'debit': amount,
                    'credit': 0.0,
                    'description': memo,
                    'project_id': project_id,
                    'tags': selected_tags,
                },
                {
                    'account_id': cash_account.id,       # CR cash
                    'debit': 0.0,
                    'credit': amount,
                    'description': memo,
                    'project_id': project_id,
                    'tags': [],
                },
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
    def delete_expense(company_id: int, expense_id: int) -> None:
        expense = Expense.query.filter_by(id=expense_id, company_id=company_id).first_or_404()

        # Void the linked transaction so it no longer affects balances
        if expense.transaction_id:
            txn = Transaction.query.get(expense.transaction_id)
            if txn and not txn.is_voided:
                txn.is_voided = True
                txn.voided_reason = 'Gasto eliminado'

        # Soft-delete: mark as deleted instead of removing the row
        expense.is_deleted = True
        expense.deleted_at = datetime.now(UTC)
        db.session.commit()

    # ── Income ─────────────────────────────────────────────────────────────

    @staticmethod
    def record_income(company_id: int, data) -> Transaction:
        """
        Record an income / revenue event.

        Double-entry:
          DR  Cash / AR Account     (amount)
          CR  Revenue Account       (amount)
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

        date_str = data.get('date', '').strip()
        income_date = _parse_date(date_str)
        description = data.get('description', '').strip()
        client_name = data.get('client_name', '').strip()
        project_id_str = data.get('project_id', '').strip()
        project_id = int(project_id_str) if project_id_str else None

        # Debit side: cash or AR
        debit_account_id_str = data.get('debit_account_id', '').strip()
        if debit_account_id_str:
            debit_account = Account.query.filter_by(id=int(debit_account_id_str), company_id=company_id).first()
        else:
            debit_account = Account.query.filter(
                Account.company_id == company_id,
                Account.name.ilike('%caja%') | Account.name.ilike('%banco%') | Account.name.ilike('%cash%')
            ).first()

        if not debit_account:
            raise ValueError('No se encontró una cuenta de efectivo o por cobrar.')
        if debit_account.type != AccountType.asset:
            raise ValueError('La cuenta de débito debe ser un activo (caja, banco o por cobrar).')

        memo = description or f"Ingreso — {revenue_account.name}"
        if client_name:
            memo = f"{memo} ({client_name})"

        txn = _create_balanced_transaction(
            company_id=company_id,
            date=income_date,
            memo=memo,
            transaction_type=TransactionType.income,
            entries=[
                {
                    'account_id': debit_account.id,      # DR cash/AR
                    'debit': amount,
                    'credit': 0.0,
                    'description': memo,
                    'project_id': project_id,
                    'tags': [],
                },
                {
                    'account_id': revenue_account_id,    # CR revenue
                    'debit': 0.0,
                    'credit': amount,
                    'description': memo,
                    'project_id': project_id,
                    'tags': [],
                },
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

    # ── Journal Entries ────────────────────────────────────────────────────

    @staticmethod
    def create_journal_entry(company_id: int, data) -> Transaction:
        """
        Manual multi-line journal entry.
        Expects form fields: memo, date, reference,
          lines[0][account_id], lines[0][debit], lines[0][credit], lines[0][description]
          lines[1][account_id], ... etc.
        """
        memo = data.get('memo', '').strip()
        if not memo:
            raise ValueError('El memo/descripción es requerido.')

        date_str = data.get('date', '').strip()
        entry_date = _parse_date(date_str)
        reference = data.get('reference', '').strip() or None

        # Parse lines — support up to 20 lines
        entries = []
        for i in range(20):
            acc_id_str = data.get(f'lines[{i}][account_id]', '').strip()
            if not acc_id_str:
                break
            debit_str = data.get(f'lines[{i}][debit]', '0').strip() or '0'
            credit_str = data.get(f'lines[{i}][credit]', '0').strip() or '0'
            line_desc = data.get(f'lines[{i}][description]', '').strip()

            try:
                acc_id = int(acc_id_str)
                debit = round(float(debit_str), 2)
                credit = round(float(credit_str), 2)
            except ValueError:
                raise ValueError(f'Línea {i + 1}: valores inválidos.')

            if debit < 0 or credit < 0:
                raise ValueError(f'Línea {i + 1}: los montos no pueden ser negativos.')
            if debit == 0 and credit == 0:
                raise ValueError(f'Línea {i + 1}: debe tener débito o crédito.')
            if debit > 0 and credit > 0:
                raise ValueError(f'Línea {i + 1}: no puede tener débito y crédito en la misma línea.')

            account = Account.query.filter_by(id=acc_id, company_id=company_id).first()
            if not account:
                raise ValueError(f'Línea {i + 1}: cuenta no encontrada.')

            entries.append({
                'account_id': acc_id,
                'debit': debit,
                'credit': credit,
                'description': line_desc or memo,
                'project_id': None,
                'tags': [],
            })

        if len(entries) < 2:
            raise ValueError('Un asiento contable requiere al menos 2 líneas.')

        txn = _create_balanced_transaction(
            company_id=company_id,
            date=entry_date,
            memo=memo,
            transaction_type=TransactionType.journal,
            entries=entries,
            reference=reference,
            reference_type='Journal',
        )

        db.session.commit()
        return txn

    @staticmethod
    def update_journal_entry(company_id: int, txn_id: int, data) -> Transaction:
        """
        Void old manual multi-line journal entry and create a new one with updated data.
        """
        old_txn = Transaction.query.filter_by(
            id=txn_id, company_id=company_id, transaction_type=TransactionType.journal
        ).first_or_404()

        if old_txn.is_voided:
            raise ValueError('No se puede editar una transacción que ya está anulada.')

        memo = data.get('memo', '').strip()
        if not memo:
            raise ValueError('El memo/descripción es requerido.')

        date_str = data.get('date', '').strip()
        entry_date = _parse_date(date_str)
        reference = data.get('reference', '').strip() or None

        # Parse lines — support up to 20 lines
        entries = []
        for i in range(20):
            acc_id_str = data.get(f'lines[{i}][account_id]', '').strip()
            if not acc_id_str:
                break
            debit_str = data.get(f'lines[{i}][debit]', '0').strip() or '0'
            credit_str = data.get(f'lines[{i}][credit]', '0').strip() or '0'
            line_desc = data.get(f'lines[{i}][description]', '').strip()

            try:
                acc_id = int(acc_id_str)
                debit = round(float(debit_str), 2)
                credit = round(float(credit_str), 2)
            except ValueError:
                raise ValueError(f'Línea {i + 1}: valores inválidos.')

            if debit < 0 or credit < 0:
                raise ValueError(f'Línea {i + 1}: los montos no pueden ser negativos.')
            if debit == 0 and credit == 0:
                raise ValueError(f'Línea {i + 1}: debe tener débito o crédito.')
            if debit > 0 and credit > 0:
                raise ValueError(f'Línea {i + 1}: no puede tener débito y crédito en la misma línea.')

            account = Account.query.filter_by(id=acc_id, company_id=company_id).first()
            if not account:
                raise ValueError(f'Línea {i + 1}: cuenta no encontrada.')

            entries.append({
                'account_id': acc_id,
                'debit': debit,
                'credit': credit,
                'description': line_desc or memo,
                'project_id': None,
                'tags': [],
            })

        if len(entries) < 2:
            raise ValueError('Un asiento contable requiere al menos 2 líneas.')

        # Void old transaction
        old_txn.is_voided = True
        old_txn.voided_reason = 'Replaced by edit'

        txn = _create_balanced_transaction(
            company_id=company_id,
            date=entry_date,
            memo=f"[EDIT] {memo}",
            transaction_type=TransactionType.journal,
            entries=entries,
            reference=reference,
            reference_type='Journal',
        )
        db.session.commit()
        return txn

    @staticmethod
    def get_journal_entries(company_id: int, search: str = '',
                            start_date: str = '', end_date: str = '',
                            page: int = 1, per_page: int = 30):
        q = (
            Transaction.query
            .filter_by(company_id=company_id, is_voided=False)
            .order_by(Transaction.date.desc(), Transaction.id.desc())
        )
        if search:
            q = q.filter(
                Transaction.memo.ilike(f'%{search}%') |
                Transaction.reference.ilike(f'%{search}%')
            )
        if start_date or end_date:
            start_dt, end_dt = _get_period_bounds(start_date, end_date)
            if start_date:
                q = q.filter(Transaction.date >= start_dt)
            if end_date:
                q = q.filter(Transaction.date <= end_dt)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def void_transaction(company_id: int, txn_id: int, reason: str = '') -> Transaction:
        txn = Transaction.query.filter_by(id=txn_id, company_id=company_id).first_or_404()
        if txn.is_voided:
            raise ValueError('Esta transacción ya está anulada.')
        txn.is_voided = True
        txn.voided_reason = reason or 'Anulado manualmente'
        db.session.commit()
        return txn

    # ── Ledger ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_ledger_entries(company_id: int, search: str = '',
                           start_date: str = '', end_date: str = '',
                           account_id: int = None) -> list:
        q = (
            LedgerEntry.query
            .join(Account, LedgerEntry.account_id == Account.id)
            .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
            .filter(
                LedgerEntry.company_id == company_id,
                _active_ledger_conditions(),
            )
        )

        if account_id:
            q = q.filter(LedgerEntry.account_id == account_id)

        if search:
            q = q.filter(
                LedgerEntry.description.ilike(f'%{search}%') |
                LedgerEntry.reference_type.ilike(f'%{search}%') |
                Account.name.ilike(f'%{search}%')
            )

        if start_date or end_date:
            start_dt, end_dt = _get_period_bounds(start_date, end_date)
            if start_date:
                q = q.filter(LedgerEntry.date >= start_dt)
            if end_date:
                q = q.filter(LedgerEntry.date <= end_dt)

        return q.order_by(LedgerEntry.date.desc(), LedgerEntry.id.desc()).all()

    # ── Trial Balance ──────────────────────────────────────────────────────

    @staticmethod
    def get_trial_balance(company_id: int, as_of_date: str = '') -> dict:
        """
        Returns a trial balance as of a given date.
        Also validates that total debits == total credits.
        """
        as_of = _parse_date(as_of_date, default_now=True) if as_of_date else None

        accounts = (
            Account.query
            .filter_by(company_id=company_id, is_active=True)
            .order_by(Account.type, Account.code, Account.name)
            .all()
        )

        rows = []
        total_debit = 0.0
        total_credit = 0.0

        for acct in accounts:
            bal = _compute_account_balance(acct, as_of=as_of)
            debit_col = round(bal, 2) if acct.normal_balance == 'debit' and bal >= 0 else 0.0
            credit_col = round(abs(bal), 2) if acct.normal_balance == 'credit' and bal >= 0 else 0.0

            # Reversed-balance accounts
            if acct.normal_balance == 'debit' and bal < 0:
                credit_col = round(abs(bal), 2)
            elif acct.normal_balance == 'credit' and bal < 0:
                debit_col = round(abs(bal), 2)

            if debit_col > 0 or credit_col > 0:
                rows.append({
                    'account': acct,
                    'debit': debit_col,
                    'credit': credit_col,
                })
                total_debit += debit_col
                total_credit += credit_col

        is_balanced = round(total_debit, 2) == round(total_credit, 2)
        return {
            'rows': rows,
            'total_debit': round(total_debit, 2),
            'total_credit': round(total_credit, 2),
            'is_balanced': is_balanced,
            'as_of': as_of or _make_naive(datetime.now(UTC)),
        }

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
            # Balance Sheet: cumulative up to end_dt
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
                else:  # liability, equity: credit increases
                    net = float(entry.credit) - float(entry.debit)
                report_data[acc_type][acc_name] = report_data[acc_type].get(acc_name, 0.0) + net

            # Add net income to retained earnings (revenue ledger − registered expenses)
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
            # Simplified indirect cash flow
            net_income = round(
                _period_revenue_total(company_id, start_dt, end_dt)
                - _period_expense_total(company_id, start_dt, end_dt),
                2,
            )

            # Investing / Financing: changes in asset/liability accounts (excluding cash)
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
    def export_report_csv(company_id: int, report_type: str,
                          report_data: dict, total,
                          start_date: str, end_date: str) -> Response:
        si = io.StringIO()
        cw = csv.writer(si)

        if report_type == 'income_statement':
            cw.writerow(['Tipo', 'Cuenta', 'Monto'])
            for acc_name, amount in report_data.get('revenue', {}).items():
                cw.writerow(['Ingreso', acc_name, f"{amount:.2f}"])
            for acc_name, amount in report_data.get('expense', {}).items():
                cw.writerow(['Gasto', acc_name, f"{amount:.2f}"])
            cw.writerow([])
            cw.writerow(['Resultado Neto', '', f"{total:.2f}"])

        elif report_type == 'balance_sheet':
            cw.writerow(['Tipo', 'Cuenta', 'Monto'])
            for acc_name, amount in report_data.get('asset', {}).items():
                cw.writerow(['Activo', acc_name, f"{amount:.2f}"])
            for acc_name, amount in report_data.get('liability', {}).items():
                cw.writerow(['Pasivo', acc_name, f"{amount:.2f}"])
            for acc_name, amount in report_data.get('equity', {}).items():
                cw.writerow(['Patrimonio', acc_name, f"{amount:.2f}"])
            cw.writerow([])
            cw.writerow(['Total Activos', '', f"{total['assets']:.2f}"])
            cw.writerow(['Total Pasivos + Patrimonio', '', f"{total['liabilities_and_equity']:.2f}"])

        elif report_type == 'cash_flow':
            cw.writerow(['Sección', 'Concepto', 'Monto'])
            for sec, items in report_data.items():
                for concept, amount in items.items():
                    cw.writerow([sec.title(), concept, f"{amount:.2f}"])
            cw.writerow([])
            cw.writerow(['Flujo Neto', '', f"{total:.2f}"])

        rep = Report(
            company_id=company_id,
            title=f"{report_type.replace('_', ' ').title()} ({start_date} to {end_date})",
            report_type=report_type,
            generated_by=current_user.id,
        )
        db.session.add(rep)
        db.session.commit()

        return Response(
            si.getvalue(),
            mimetype='text/csv',
            headers={'Content-disposition': f'attachment; filename={report_type}_{end_date}.csv'},
        )

    # ── Accounts ───────────────────────────────────────────────────────────

    @staticmethod
    def create_account(company_id: int, data) -> Account:
        name = data.get('name', '').strip()
        account_type = data.get('type', '').strip()
        description = data.get('description', '').strip()
        code = data.get('code', '').strip() or None

        if not name or not account_type:
            raise ValueError('El nombre y el tipo de cuenta son requeridos.')
        try:
            act_type_enum = AccountType(account_type)
        except ValueError:
            raise ValueError('Tipo de cuenta inválido.')

        account = Account(
            company_id=company_id,
            code=code,
            name=name,
            type=act_type_enum,
            description=description,
        )
        db.session.add(account)
        db.session.commit()
        return account

    @staticmethod
    def update_account(company_id: int, account_id: int, data) -> Account:
        account = Account.query.filter_by(id=account_id, company_id=company_id).first_or_404()
        name = data.get('name', '').strip()
        account_type = data.get('type', '').strip()
        if not name or not account_type:
            raise ValueError('Nombre y tipo son requeridos.')
        try:
            account.type = AccountType(account_type)
        except ValueError:
            raise ValueError('Tipo de cuenta inválido.')
        account.name = name
        account.code = data.get('code', '').strip() or account.code
        account.description = data.get('description', '').strip()
        account.is_active = data.get('is_active', 'true').lower() == 'true'
        db.session.commit()
        return account

    @staticmethod
    def generate_default_accounts(company_id: int) -> int:
        default_accounts = [
            {'code': '1100', 'name': 'Caja y Bancos',          'type': AccountType.asset,     'description': 'Efectivo y saldos bancarios.'},
            {'code': '1200', 'name': 'Cuentas por Cobrar',     'type': AccountType.asset,     'description': 'Derechos de cobro a clientes.'},
            {'code': '1300', 'name': 'Inventario',             'type': AccountType.asset,     'description': 'Mercancías para la venta.'},
            {'code': '1400', 'name': 'Activos Fijos',          'type': AccountType.asset,     'description': 'Maquinaria, equipos y mobiliario.'},
            {'code': '2100', 'name': 'Cuentas por Pagar',      'type': AccountType.liability, 'description': 'Obligaciones con proveedores.'},
            {'code': '2200', 'name': 'Obligaciones Fiscales',  'type': AccountType.liability, 'description': 'Impuestos pendientes.'},
            {'code': '2300', 'name': 'Préstamos por Pagar',    'type': AccountType.liability, 'description': 'Deudas bancarias a corto y largo plazo.'},
            {'code': '3100', 'name': 'Capital Social',         'type': AccountType.equity,    'description': 'Aportaciones de socios.'},
            {'code': '3200', 'name': 'Resultados Acumulados',  'type': AccountType.equity,    'description': 'Utilidades/pérdidas de ejercicios anteriores.'},
            {'code': '4100', 'name': 'Ventas de Servicios',    'type': AccountType.revenue,   'description': 'Ingresos por servicios.'},
            {'code': '4200', 'name': 'Ventas de Productos',    'type': AccountType.revenue,   'description': 'Ingresos por ventas de bienes.'},
            {'code': '5100', 'name': 'Costo de Ventas',        'type': AccountType.expense,   'description': 'Costo directo de bienes vendidos.'},
            {'code': '5200', 'name': 'Nóminas y Salarios',     'type': AccountType.expense,   'description': 'Remuneraciones al personal.'},
            {'code': '5300', 'name': 'Gastos de Alquiler',     'type': AccountType.expense,   'description': 'Arrendamiento de locales.'},
            {'code': '5400', 'name': 'Servicios Públicos',     'type': AccountType.expense,   'description': 'Electricidad, agua, internet.'},
            {'code': '5500', 'name': 'Gastos de Marketing',    'type': AccountType.expense,   'description': 'Publicidad y promoción.'},
            {'code': '5600', 'name': 'Gastos Financieros',     'type': AccountType.expense,   'description': 'Intereses y comisiones bancarias.'},
            {'code': '5900', 'name': 'Otros Gastos',           'type': AccountType.expense,   'description': 'Gastos diversos no clasificados.'},
        ]

        created_count = 0
        for def_acc in default_accounts:
            exists = Account.query.filter_by(
                company_id=company_id, name=def_acc['name'], type=def_acc['type']
            ).first()
            if not exists:
                db.session.add(Account(
                    company_id=company_id,
                    code=def_acc['code'],
                    name=def_acc['name'],
                    type=def_acc['type'],
                    description=def_acc['description'],
                    is_default=True,
                    is_active=True,
                ))
                created_count += 1

        if created_count > 0:
            db.session.commit()
        return created_count

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
        """Soft-delete a tag."""
        tag = Tag.query.filter_by(id=tag_id, company_id=company_id).first_or_404()
        tag.is_deleted = True
        tag.deleted_at = datetime.now(UTC)
        db.session.commit()

    # ── Ledger (paginated, with balances) ──────────────────────────────────

    @staticmethod
    def get_ledger_page(company_id: int, account_id: int = None,
                        start_date: str = '', end_date: str = '',
                        page: int = 1, per_page: int = 40):
        """
        Return a dict with:
          account, all_accounts, opening_balance, ending_balance, pagination
        ready to pass directly to the ledger template.
        """
        all_accounts = (
            Account.query
            .filter_by(company_id=company_id, is_active=True)
            .order_by(Account.type, Account.code, Account.name)
            .all()
        )

        if not account_id:
            return {
                'account': None,
                'all_accounts': all_accounts,
                'opening_balance': 0.0,
                'ending_balance': 0.0,
                'pagination': None,
                'start_date': start_date,
                'end_date': end_date,
            }

        account = Account.query.filter_by(id=account_id, company_id=company_id).first_or_404()

        # Period bounds
        now = _make_naive(datetime.now(UTC))
        if start_date:
            start_dt = _make_naive(_parse_date(start_date))
        else:
            start_dt = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_date:
            end_dt = _make_naive(_parse_date(end_date)).replace(hour=23, minute=59, second=59)
        else:
            end_dt = now.replace(hour=23, minute=59, second=59)

        # Opening balance = balance of the account BEFORE start_dt
        open_q = (
            db.session.query(
                func.coalesce(func.sum(LedgerEntry.debit), 0),
                func.coalesce(func.sum(LedgerEntry.credit), 0),
            )
            .select_from(LedgerEntry)
            .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
            .filter(
                LedgerEntry.account_id == account_id,
                LedgerEntry.company_id == company_id,
                LedgerEntry.date < start_dt,
                _active_ledger_conditions(),
            )
            .one()
        )
        open_d, open_c = float(open_q[0]), float(open_q[1])
        if account.type in (AccountType.asset, AccountType.expense):
            opening_balance = round(open_d - open_c, 2)
        else:
            opening_balance = round(open_c - open_d, 2)

        # Paginated entries for the period
        q = (
            LedgerEntry.query
            .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
            .filter(
                LedgerEntry.account_id == account_id,
                LedgerEntry.company_id == company_id,
                LedgerEntry.date >= start_dt,
                LedgerEntry.date <= end_dt,
                _active_ledger_conditions(),
            )
            .order_by(LedgerEntry.date.asc(), LedgerEntry.id.asc())
        )
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)

        # Ending balance = opening + net of ALL period entries (not just current page)
        period_all_q = (
            db.session.query(
                func.coalesce(func.sum(LedgerEntry.debit), 0),
                func.coalesce(func.sum(LedgerEntry.credit), 0),
            )
            .select_from(LedgerEntry)
            .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
            .filter(
                LedgerEntry.account_id == account_id,
                LedgerEntry.company_id == company_id,
                LedgerEntry.date >= start_dt,
                LedgerEntry.date <= end_dt,
                _active_ledger_conditions(),
            )
            .one()
        )
        per_d, per_c = float(period_all_q[0]), float(period_all_q[1])
        if account.type in (AccountType.asset, AccountType.expense):
            ending_balance = round(opening_balance + per_d - per_c, 2)
        else:
            ending_balance = round(opening_balance + per_c - per_d, 2)

        # Convert Decimal values to float for template arithmetic
        for entry in pagination.items:
            entry.debit = float(entry.debit)
            entry.credit = float(entry.credit)

        return {
            'account': account,
            'all_accounts': all_accounts,
            'opening_balance': opening_balance,
            'ending_balance': ending_balance,
            'pagination': pagination,
            'entries': pagination.items,
            'start_date': start_date or start_dt.strftime('%Y-%m-%d'),
            'end_date': end_date or end_dt.strftime('%Y-%m-%d'),
        }

    # ── Edit Expense ────────────────────────────────────────────────────────

    @staticmethod
    def update_expense(company_id: int, expense_id: int, data, files=None) -> 'Expense':
        """
        Edit an existing expense.
        Strategy: void the original transaction and create a new balanced one.
        """
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

        date_str = data.get('date', '').strip()
        expense_date = _parse_date(date_str)
        description = data.get('description', '').strip()
        vendor_name = data.get('vendor_name', '').strip()
        category = data.get('category', '').strip()
        project_id_str = data.get('project_id', '').strip()
        project_id = int(project_id_str) if project_id_str else None
        status_str = data.get('status', 'draft').strip()
        try:
            status = ExpenseStatus(status_str)
        except ValueError:
            status = ExpenseStatus.draft

        tag_ids = data.getlist('tags[]') if hasattr(data, 'getlist') else []
        selected_tags = (
            Tag.query.filter(Tag.id.in_([int(tid) for tid in tag_ids if tid])).all()
            if tag_ids else []
        )

        # Void old transaction
        if expense.transaction_id:
            old_txn = Transaction.query.get(expense.transaction_id)
            if old_txn and not old_txn.is_voided:
                old_txn.is_voided = True
                old_txn.voided_reason = f'Replaced by edit of Expense #{expense_id}'

        # Update receipt if new file
        if files and 'receipt_file' in files and files['receipt_file'].filename:
            new_receipt = _save_receipt(files['receipt_file'])
            if new_receipt:
                expense.receipt_url = new_receipt

        # Resolve cash account
        cash_account = Account.query.filter(
            Account.company_id == company_id,
            Account.name.ilike('%caja%') | Account.name.ilike('%banco%') | Account.name.ilike('%cash%')
        ).first()
        if not cash_account:
            cash_account = Account.query.filter_by(company_id=company_id, type=AccountType.asset).first()
        if not cash_account:
            raise ValueError('No se encontró una cuenta de efectivo. Genere las cuentas base primero.')

        # Update expense fields
        expense.account_id = account_id
        expense.amount = amount
        expense.date = expense_date
        expense.description = description
        expense.vendor_name = vendor_name
        expense.category = category
        expense.project_id = project_id
        expense.status = status
        expense.tags = selected_tags

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
        db.session.commit()
        return expense

    # ── Edit / Delete Income ────────────────────────────────────────────────

    @staticmethod
    def update_income(company_id: int, txn_id: int, data) -> 'Transaction':
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

        date_str = data.get('date', '').strip()
        income_date = _parse_date(date_str)
        description = data.get('description', '').strip()
        client_name = data.get('client_name', '').strip()
        project_id_str = data.get('project_id', '').strip()
        project_id = int(project_id_str) if project_id_str else None

        debit_account_id_str = data.get('debit_account_id', '').strip()
        if debit_account_id_str:
            debit_account = Account.query.filter_by(id=int(debit_account_id_str), company_id=company_id).first()
        else:
            debit_account = Account.query.filter(
                Account.company_id == company_id,
                Account.name.ilike('%caja%') | Account.name.ilike('%banco%') | Account.name.ilike('%cash%')
            ).first()
        if not debit_account:
            raise ValueError('No se encontró una cuenta de efectivo o por cobrar.')
        if debit_account.type != AccountType.asset:
            raise ValueError('La cuenta de débito debe ser un activo (caja, banco o por cobrar).')

        # Void old
        old_txn.is_voided = True
        old_txn.voided_reason = f'Replaced by edit'

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

    # ── Delete Account ──────────────────────────────────────────────────────

    @staticmethod
    def delete_account_safe(company_id: int, account_id: int) -> None:
        """
        Soft-delete an account (set is_active=False, is_deleted=True, deleted_at=now).
        Raises ValueError if the account has any non-voided ledger entries to prevent
        orphaning historical accounting data.
        """
        account = Account.query.filter_by(id=account_id, company_id=company_id).first_or_404()
        entry_count = (
            LedgerEntry.query
            .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
            .filter(
                LedgerEntry.account_id == account_id,
                LedgerEntry.company_id == company_id,
                _active_ledger_conditions(),
            )
            .count()
        )
        if entry_count > 0:
            raise ValueError(
                f'Esta cuenta tiene {entry_count} movimiento(s) contables y no puede eliminarse. '
                'Puede desactivarla en su lugar.'
            )
        account.is_active = False
        account.is_deleted = True
        account.deleted_at = datetime.now(UTC)
        db.session.commit()

    # ── Projects ────────────────────────────────────────────────────────────

    @staticmethod
    def update_project(company_id: int, project_id: int, data) -> 'Project':
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
        # Unlink expenses from this project so they aren't orphaned
        Expense.query.filter_by(project_id=project_id, company_id=company_id).update({'project_id': None})
        # Unlink ledger entries from this project
        LedgerEntry.query.filter_by(project_id=project_id, company_id=company_id).update({'project_id': None})
        # Soft-delete: mark the project as deleted instead of removing the row
        project.is_deleted = True
        project.deleted_at = datetime.now(UTC)
        project.status = 'cancelled'
        db.session.commit()

    @staticmethod
    def get_project_detail(company_id: int, project_id: int) -> dict:
        """Return full P&L breakdown for a project."""
        project = Project.query.filter_by(id=project_id, company_id=company_id).first_or_404()

        expenses = (
            db.session.execute(
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
            .unique()
            .scalars()
            .all()
        )

        income_entries = (
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
            .all()
        )

        total_expenses = round(sum(float(e.amount) for e in expenses), 2)
        total_income = round(
            sum(float(e.credit) - float(e.debit) for e in income_entries),
            2,
        )
        net = round(total_income - total_expenses, 2)
        budget = float(project.budget or 0)
        budget_remaining = round(budget - total_expenses, 2)

        # Monthly breakdown for chart
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

        # Active ledger entries for the project
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

        # Invoices associated with the project
        invoices = (
            Document.query
            .filter_by(project_id=project_id, company_id=company_id, type=DocumentType.invoice)
            .order_by(Document.issued_date.desc())
            .all()
        )

        # Count invoices by status
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
            'expenses': expenses,
            'income_entries': income_entries,
            'all_ledger': all_ledger,
            'invoices': invoices,
            'invoices_by_status': invoices_by_status,
            'total_invoices': total_invoices,
            'total_expenses': total_expenses,
            'total_income': total_income,
            'net': net,
            'budget': budget,
            'budget_remaining': budget_remaining,
            'monthly': monthly,
        }

    @staticmethod
    def get_projects_list(company_id: int) -> list:
        projects = Project.query.filter_by(company_id=company_id).order_by(Project.name).all()
        balances = _compute_balances_bulk(company_id)

        result = []
        for p in projects:
            expense_total = _period_expense_total(company_id, project_id=p.id)
            income_total = _period_revenue_total(company_id, project_id=p.id)
            
            # Count invoices by status
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

