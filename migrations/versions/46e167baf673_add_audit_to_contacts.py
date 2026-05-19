"""add_audit_to_contacts

Revision ID: 46e167baf673
Revises: 0c2495f8e36b
Create Date: 2026-05-18 22:13:37.662248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46e167baf673'
down_revision = '0c2495f8e36b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('contacts', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('contacts', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('contacts', 'updated_at')
    op.drop_column('contacts', 'created_at')

