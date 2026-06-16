"""Expand notifications

Revision ID: b7c9a2d4e8f1
Revises: 9f8e7d6c5b4a
Create Date: 2026-06-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'b7c9a2d4e8f1'
down_revision = '9f8e7d6c5b4a'
branch_labels = None
depends_on = None


def _column_exists(bind, table_name, column_name):
    return column_name in [column['name'] for column in inspect(bind).get_columns(table_name)]


def upgrade():
    bind = op.get_bind()
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        if not _column_exists(bind, 'notifications', 'company_id'):
            batch_op.add_column(sa.Column('company_id', sa.Integer(), nullable=True))
        if not _column_exists(bind, 'notifications', 'created_by_id'):
            batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        if not _column_exists(bind, 'notifications', 'title'):
            batch_op.add_column(sa.Column('title', sa.String(length=255), server_default='Notificacion', nullable=False))
        if not _column_exists(bind, 'notifications', 'body'):
            batch_op.add_column(sa.Column('body', sa.String(length=2048), nullable=True))
        if not _column_exists(bind, 'notifications', 'link_url'):
            batch_op.add_column(sa.Column('link_url', sa.String(length=512), nullable=True))
        if not _column_exists(bind, 'notifications', 'priority'):
            batch_op.add_column(sa.Column('priority', sa.String(length=20), server_default='normal', nullable=False))
        if not _column_exists(bind, 'notifications', 'channel'):
            batch_op.add_column(sa.Column('channel', sa.String(length=50), server_default='in_app', nullable=False))
        if not _column_exists(bind, 'notifications', 'read_at'):
            batch_op.add_column(sa.Column('read_at', sa.DateTime(), nullable=True))
        if not _column_exists(bind, 'notifications', 'expires_at'):
            batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=True))
        if not _column_exists(bind, 'notifications', 'is_popup'):
            batch_op.add_column(sa.Column('is_popup', sa.Boolean(), server_default=sa.false(), nullable=False))

    op.execute("UPDATE notifications SET title = COALESCE(NULLIF(title, ''), 'Notificacion')")
    op.execute("UPDATE notifications SET body = COALESCE(body, message)")
    op.execute("UPDATE notifications SET status = COALESCE(NULLIF(status, ''), 'unread')")
    op.execute("UPDATE notifications SET sent_at = COALESCE(sent_at, created_at)")

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        if not _has_index(bind, 'notifications', 'ix_notifications_company_id'):
            batch_op.create_index(batch_op.f('ix_notifications_company_id'), ['company_id'], unique=False)
        if not _has_index(bind, 'notifications', 'ix_notifications_created_by_id'):
            batch_op.create_index(batch_op.f('ix_notifications_created_by_id'), ['created_by_id'], unique=False)
        if not _has_index(bind, 'notifications', 'ix_notifications_priority'):
            batch_op.create_index(batch_op.f('ix_notifications_priority'), ['priority'], unique=False)
        if not _has_index(bind, 'notifications', 'ix_notifications_channel'):
            batch_op.create_index(batch_op.f('ix_notifications_channel'), ['channel'], unique=False)
        if not _has_index(bind, 'notifications', 'ix_notifications_read_at'):
            batch_op.create_index(batch_op.f('ix_notifications_read_at'), ['read_at'], unique=False)
        if not _has_index(bind, 'notifications', 'ix_notifications_expires_at'):
            batch_op.create_index(batch_op.f('ix_notifications_expires_at'), ['expires_at'], unique=False)
        if not _has_index(bind, 'notifications', 'ix_notifications_is_popup'):
            batch_op.create_index(batch_op.f('ix_notifications_is_popup'), ['is_popup'], unique=False)
        batch_op.create_foreign_key('fk_notifications_company_id_companies', 'companies', ['company_id'], ['id'])
        batch_op.create_foreign_key('fk_notifications_created_by_id_users', 'users', ['created_by_id'], ['id'])


def downgrade():
    bind = op.get_bind()
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        for fk_name in ('fk_notifications_created_by_id_users', 'fk_notifications_company_id_companies'):
            try:
                batch_op.drop_constraint(fk_name, type_='foreignkey')
            except Exception:
                pass
        for index_name in (
            'ix_notifications_is_popup',
            'ix_notifications_expires_at',
            'ix_notifications_read_at',
            'ix_notifications_channel',
            'ix_notifications_priority',
            'ix_notifications_created_by_id',
            'ix_notifications_company_id',
        ):
            if _has_index(bind, 'notifications', index_name):
                batch_op.drop_index(index_name)
        for column_name in (
            'is_popup',
            'expires_at',
            'read_at',
            'channel',
            'priority',
            'link_url',
            'body',
            'title',
            'created_by_id',
            'company_id',
        ):
            if _column_exists(bind, 'notifications', column_name):
                batch_op.drop_column(column_name)


def _has_index(bind, table_name, index_name):
    return index_name in [index['name'] for index in inspect(bind).get_indexes(table_name)]
