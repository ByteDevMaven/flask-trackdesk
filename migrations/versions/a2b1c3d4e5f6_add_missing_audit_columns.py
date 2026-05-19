"""add_missing_audit_columns

Revision ID: a2b1c3d4e5f6
Revises: 46e167baf673
Create Date: 2026-05-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2b1c3d4e5f6'
down_revision = '46e167baf673'
branch_labels = None
depends_on = None


def upgrade():
    # Add updated_at to stock_movements
    op.add_column('stock_movements', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Add created_at and updated_at to roles
    op.add_column('roles', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('roles', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Add created_at and updated_at to permissions
    op.add_column('permissions', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('permissions', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Add created_at and updated_at to purchase_order_items
    op.add_column('purchase_order_items', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('purchase_order_items', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('purchase_order_items', 'updated_at')
    op.drop_column('purchase_order_items', 'created_at')
    
    op.drop_column('permissions', 'updated_at')
    op.drop_column('permissions', 'created_at')
    
    op.drop_column('roles', 'updated_at')
    op.drop_column('roles', 'created_at')
    
    op.drop_column('stock_movements', 'updated_at')
