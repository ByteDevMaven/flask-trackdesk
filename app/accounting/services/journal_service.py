"""Journal entries, ledger, and trial balance service."""
from datetime import UTC, datetime

from app.models import db, Account, LedgerEntry, Transaction
from app.models.enums import TransactionType

from ._helpers import _parse_date, _get_period_bounds, _make_naive
from ._balance import (
    _active_ledger_conditions,
    _compute_account_balance,
    _create_balanced_transaction,
)


def _parse_journal_lines(data, company_id: int) -> list[dict]:
    """Parse and validate multi-line journal form data into entry dicts."""
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
            'description': line_desc,
            'project_id': None,
            'tags': [],
        })

    if len(entries) < 2:
        raise ValueError('Un asiento contable requiere al menos 2 líneas.')
    return entries


class JournalService:

    # ── Journal CRUD ───────────────────────────────────────────────────────

    @staticmethod
    def create_journal_entry(company_id: int, data) -> Transaction:
        """
        Manual multi-line journal entry.
        Expects form fields: memo, date, reference,
          lines[N][account_id], lines[N][debit], lines[N][credit], lines[N][description]
        """
        memo = data.get('memo', '').strip()
        if not memo:
            raise ValueError('El memo/descripción es requerido.')

        entry_date = _parse_date(data.get('date', '').strip())
        reference = data.get('reference', '').strip() or None

        entries = _parse_journal_lines(data, company_id)
        for e in entries:
            if not e['description']:
                e['description'] = memo

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
        """Void old entry and post a corrected replacement."""
        old_txn = Transaction.query.filter_by(
            id=txn_id, company_id=company_id, transaction_type=TransactionType.journal
        ).first_or_404()
        if old_txn.is_voided:
            raise ValueError('No se puede editar una transacción que ya está anulada.')

        memo = data.get('memo', '').strip()
        if not memo:
            raise ValueError('El memo/descripción es requerido.')

        entry_date = _parse_date(data.get('date', '').strip())
        reference = data.get('reference', '').strip() or None

        entries = _parse_journal_lines(data, company_id)
        for e in entries:
            if not e['description']:
                e['description'] = memo

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

    @staticmethod
    def delete_journal_entry(company_id: int, txn_id: int) -> None:
        """Soft-delete a manual journal transaction."""
        txn = Transaction.query.filter_by(
            id=txn_id, company_id=company_id, transaction_type=TransactionType.journal
        ).first_or_404()
        txn.is_voided = True
        txn.voided_reason = 'Eliminado'
        txn.is_deleted = True
        txn.deleted_at = datetime.now(UTC)
        db.session.commit()

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

    @staticmethod
    def get_ledger_page(company_id: int, account_id: int = None,
                        start_date: str = '', end_date: str = '',
                        page: int = 1, per_page: int = 40) -> dict:
        """Return a full ledger page dict ready to pass to the template."""
        from sqlalchemy import func
        from app.models.enums import AccountType

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

        now = _make_naive(datetime.now(UTC))
        start_dt = (
            _make_naive(_parse_date(start_date))
            if start_date
            else now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        )
        end_dt = (
            _make_naive(_parse_date(end_date)).replace(hour=23, minute=59, second=59)
            if end_date
            else now.replace(hour=23, minute=59, second=59)
        )

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

    # ── Trial Balance ──────────────────────────────────────────────────────

    @staticmethod
    def get_trial_balance(company_id: int, as_of_date: str = '') -> dict:
        """Returns a trial balance as of a given date."""
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

            if acct.normal_balance == 'debit' and bal < 0:
                credit_col = round(abs(bal), 2)
            elif acct.normal_balance == 'credit' and bal < 0:
                debit_col = round(abs(bal), 2)

            if debit_col > 0 or credit_col > 0:
                rows.append({'account': acct, 'debit': debit_col, 'credit': credit_col})
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
