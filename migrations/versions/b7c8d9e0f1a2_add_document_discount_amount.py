"""Add persisted general discount to documents."""
from alembic import op
import sqlalchemy as sa

revision = "b7c8d9e0f1a2"
down_revision = "a63c2982be42"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("documents") as batch_op:
        batch_op.add_column(sa.Column("discount_amount", sa.Numeric(12, 2), nullable=True))
    op.execute("UPDATE documents SET discount_amount = 0 WHERE discount_amount IS NULL")
    with op.batch_alter_table("documents") as batch_op:
        batch_op.alter_column("discount_amount", existing_type=sa.Numeric(12, 2), nullable=False)


def downgrade():
    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_column("discount_amount")