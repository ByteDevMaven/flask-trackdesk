"""add_description_to_role_and_permission

Revision ID: b3c4d5e6f7a8
Revises: a2b1c3d4e5f6
Create Date: 2026-05-24 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7a8'
down_revision = 'a2b1c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add description column to roles table
    op.add_column('roles', sa.Column('description', sa.String(), nullable=True))

    # Add description column to permissions table
    op.add_column('permissions', sa.Column('description', sa.String(), nullable=True))


def downgrade():
    op.drop_column('permissions', 'description')
    op.drop_column('roles', 'description')
