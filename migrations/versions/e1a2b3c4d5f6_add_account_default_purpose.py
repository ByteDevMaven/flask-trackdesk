"""Add account default purpose

Revision ID: e1a2b3c4d5f6
Revises: ddee51204bae
Create Date: 2026-06-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'e1a2b3c4d5f6'
down_revision = 'ddee51204bae'
branch_labels = None
depends_on = None


INVOICE_PAYMENT_REVENUE_PURPOSE = 'invoice_payment_revenue'


def _column_exists(bind, table_name, column_name):
    return column_name in [column['name'] for column in inspect(bind).get_columns(table_name)]


def _has_index(bind, table_name, index_name):
    return index_name in [index['name'] for index in inspect(bind).get_indexes(table_name)]


def _backfill_invoice_payment_revenue(bind):
    accounts = bind.execute(sa.text("""
        SELECT id, company_id, code, name, is_active, is_default
        FROM accounts
        WHERE type = 'revenue'
        ORDER BY company_id, code, name
    """)).mappings().all()

    selected_by_company = {}
    scores_by_company = {}
    for account in accounts:
        name = (account['name'] or '').lower()
        code = account['code'] or ''
        score = 0
        if account['is_active']:
            score += 10
        if 'ventas de productos' in name or 'product' in name or code == '4200':
            score += 100
        elif 'sales revenue' in name:
            score += 50
        if account['is_default']:
            score += 5

        company_id = account['company_id']
        if score > scores_by_company.get(company_id, -1):
            selected_by_company[company_id] = account['id']
            scores_by_company[company_id] = score

    for account_id in selected_by_company.values():
        bind.execute(
            sa.text("UPDATE accounts SET default_purpose = :purpose WHERE id = :account_id"),
            {'purpose': INVOICE_PAYMENT_REVENUE_PURPOSE, 'account_id': account_id},
        )


def upgrade():
    bind = op.get_bind()
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        if not _column_exists(bind, 'accounts', 'default_purpose'):
            batch_op.add_column(sa.Column('default_purpose', sa.String(length=50), nullable=True))
        if not _has_index(bind, 'accounts', 'ix_accounts_default_purpose'):
            batch_op.create_index(batch_op.f('ix_accounts_default_purpose'), ['default_purpose'], unique=False)

    _backfill_invoice_payment_revenue(bind)


def downgrade():
    bind = op.get_bind()
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        if _has_index(bind, 'accounts', 'ix_accounts_default_purpose'):
            batch_op.drop_index(batch_op.f('ix_accounts_default_purpose'))
        if _column_exists(bind, 'accounts', 'default_purpose'):
            batch_op.drop_column('default_purpose')
