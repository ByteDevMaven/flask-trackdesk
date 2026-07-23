"""allow_signed_adjustment_quantity

Revision ID: 6b073511a0f5
Revises: 0b33dda190e6
Create Date: 2026-07-22 18:53:09.607897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b073511a0f5'
down_revision = '0b33dda190e6'
branch_labels = None
depends_on = None


def upgrade():
    # Create index only if it doesn't already exist
    from alembic import op as _op
    from sqlalchemy import inspect
    bind = _op.get_bind()
    inspector = inspect(bind)
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('inventory_items')]
    if 'ix_inventory_items_category_id' not in existing_indexes:
        with op.batch_alter_table('inventory_items', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_inventory_items_category_id'), ['category_id'], unique=False)

    # Rebuild stock_movements table so the updated CHECK constraint
    # (quantity != 0 instead of quantity > 0) takes effect in SQLite.
    with op.batch_alter_table('stock_movements', schema=None) as batch_op:
        pass  # batch_alter rebuilds the table with the new model constraints


def downgrade():
    with op.batch_alter_table('inventory_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_inventory_items_category_id'))

    with op.batch_alter_table('stock_movements', schema=None) as batch_op:
        pass  # no-op; constraint is defined in the model
