"""add pos register sessions

Revision ID: f6a7b8c9d0e1
Revises: 89ddd12bc651
Create Date: 2026-06-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = '89ddd12bc651'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name):
    return table_name in inspect(bind).get_table_names()


def _column_exists(bind, table_name, column_name):
    if not _table_exists(bind, table_name):
        return False
    return column_name in [column['name'] for column in inspect(bind).get_columns(table_name)]


def _index_exists(bind, table_name, index_name):
    if not _table_exists(bind, table_name):
        return False
    return index_name in [index['name'] for index in inspect(bind).get_indexes(table_name)]


def upgrade():
    bind = op.get_bind()

    if not _table_exists(bind, 'pos_register_sessions'):
        op.create_table(
            'pos_register_sessions',
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('warehouse_id', sa.Integer(), nullable=True),
            sa.Column('register_name', sa.String(length=100), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('opening_amount', sa.Numeric(12, 2), nullable=False),
            sa.Column('expected_cash_amount', sa.Numeric(12, 2), nullable=True),
            sa.Column('closing_amount', sa.Numeric(12, 2), nullable=True),
            sa.Column('opened_at', sa.DateTime(), nullable=False),
            sa.Column('closed_at', sa.DateTime(), nullable=True),
            sa.Column('notes', sa.String(length=1024), nullable=True),
            sa.Column('closing_notes', sa.String(length=1024), nullable=True),
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('is_deleted', sa.Boolean(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.CheckConstraint('opening_amount >= 0', name='check_pos_register_opening_non_negative'),
            sa.CheckConstraint('closing_amount IS NULL OR closing_amount >= 0', name='check_pos_register_closing_non_negative'),
            sa.CheckConstraint("status IN ('open', 'closed')", name='check_pos_register_status'),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    with op.batch_alter_table('pos_register_sessions', schema=None) as batch_op:
        for column_name in ['company_id', 'user_id', 'warehouse_id', 'status', 'opened_at', 'closed_at']:
            index_name = batch_op.f(f'ix_pos_register_sessions_{column_name}')
            if not _index_exists(bind, 'pos_register_sessions', index_name):
                batch_op.create_index(index_name, [column_name], unique=False)

    if not _table_exists(bind, 'pos_cash_movements'):
        op.create_table(
            'pos_cash_movements',
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('register_session_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('movement_type', sa.String(length=20), nullable=False),
            sa.Column('amount', sa.Numeric(12, 2), nullable=False),
            sa.Column('reason', sa.String(length=255), nullable=False),
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('is_deleted', sa.Boolean(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.CheckConstraint('amount > 0', name='check_pos_cash_movement_amount_positive'),
            sa.CheckConstraint("movement_type IN ('cash_in', 'cash_out')", name='check_pos_cash_movement_type'),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
            sa.ForeignKeyConstraint(['register_session_id'], ['pos_register_sessions.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    with op.batch_alter_table('pos_cash_movements', schema=None) as batch_op:
        for column_name in ['company_id', 'register_session_id', 'user_id', 'movement_type']:
            index_name = batch_op.f(f'ix_pos_cash_movements_{column_name}')
            if not _index_exists(bind, 'pos_cash_movements', index_name):
                batch_op.create_index(index_name, [column_name], unique=False)

    with op.batch_alter_table('payments', schema=None) as batch_op:
        if not _column_exists(bind, 'payments', 'pos_register_session_id'):
            batch_op.add_column(sa.Column('pos_register_session_id', sa.Integer(), nullable=True))
        index_name = batch_op.f('ix_payments_pos_register_session_id')
        if not _index_exists(bind, 'payments', index_name):
            batch_op.create_index(index_name, ['pos_register_session_id'], unique=False)


def downgrade():
    bind = op.get_bind()
    with op.batch_alter_table('payments', schema=None) as batch_op:
        index_name = batch_op.f('ix_payments_pos_register_session_id')
        if _index_exists(bind, 'payments', index_name):
            batch_op.drop_index(index_name)
        if _column_exists(bind, 'payments', 'pos_register_session_id'):
            batch_op.drop_column('pos_register_session_id')

    if _table_exists(bind, 'pos_cash_movements'):
        op.drop_table('pos_cash_movements')

    if _table_exists(bind, 'pos_register_sessions'):
        op.drop_table('pos_register_sessions')
