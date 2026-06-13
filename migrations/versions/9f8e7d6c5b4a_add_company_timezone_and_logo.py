"""Add company timezone and logo

Revision ID: 9f8e7d6c5b4a
Revises: 6af85a17e660
Create Date: 2026-06-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '9f8e7d6c5b4a'
down_revision = '6af85a17e660'
branch_labels = None
depends_on = None


def _column_exists(bind, table_name, column_name):
    return column_name in [column['name'] for column in inspect(bind).get_columns(table_name)]


def upgrade():
    bind = op.get_bind()
    with op.batch_alter_table('companies', schema=None) as batch_op:
        if not _column_exists(bind, 'companies', 'logo_url'):
            batch_op.add_column(sa.Column('logo_url', sa.String(length=512), nullable=True))
        if not _column_exists(bind, 'companies', 'timezone'):
            batch_op.add_column(sa.Column('timezone', sa.String(length=50), server_default='UTC', nullable=False))


def downgrade():
    bind = op.get_bind()
    with op.batch_alter_table('companies', schema=None) as batch_op:
        if _column_exists(bind, 'companies', 'timezone'):
            batch_op.drop_column('timezone')
        if _column_exists(bind, 'companies', 'logo_url'):
            batch_op.drop_column('logo_url')
