"""consolidate_schema

Migrates suppliers -> contacts (type='supplier')
Migrates clients   -> contacts (type='customer')
Creates missing tables: accounts, contacts, projects, audit_logs, expenses, ledger_entries
Adds missing columns on existing tables
Drops suppliers and clients AFTER data is safely migrated

Revision ID: d1e2f3a4b5c6
Revises: 4c2584349c01
Create Date: 2026-05-27 07:17:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = '4c2584349c01'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name):
    return inspect(bind).has_table(table_name)


def _column_exists(bind, table_name, column_name):
    cols = [c['name'] for c in inspect(bind).get_columns(table_name)]
    return column_name in cols


def _index_exists(bind, table_name, index_name):
    indexes = [i['name'] for i in inspect(bind).get_indexes(table_name)]
    return index_name in indexes


def upgrade():
    bind = op.get_bind()

    # ──────────────────────────────────────────────────────────────
    # 1. CREATE contacts (if not exists)
    # ──────────────────────────────────────────────────────────────
    if not _table_exists(bind, 'contacts'):
        op.create_table('contacts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),  # 'customer' | 'supplier'
            sa.Column('identifier', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(), nullable=True),
            sa.Column('phone', sa.String(), nullable=True),
            sa.Column('address', sa.String(), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('contacts', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_contacts_company_id'), ['company_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_contacts_email'), ['email'], unique=False)
            batch_op.create_index(batch_op.f('ix_contacts_identifier'), ['identifier'], unique=False)
            batch_op.create_index(batch_op.f('ix_contacts_name'), ['name'], unique=False)
            batch_op.create_index(batch_op.f('ix_contacts_phone'), ['phone'], unique=False)

    # ──────────────────────────────────────────────────────────────
    # 2. MIGRATE suppliers -> contacts
    # ──────────────────────────────────────────────────────────────
    if _table_exists(bind, 'suppliers'):
        # Build a mapping: old supplier id -> new contact id
        # We insert suppliers as type='supplier' into contacts
        suppliers = bind.execute(text(
            "SELECT id, company_id, name, contact_email, phone, address, created_at, updated_at FROM suppliers"
        )).fetchall()

        # Track supplier_id -> contact_id for FK rewiring
        supplier_id_map = {}
        for row in suppliers:
            result = bind.execute(text(
                "INSERT INTO contacts (company_id, name, type, email, phone, address, created_at, updated_at) "
                "VALUES (:company_id, :name, 'supplier', :email, :phone, :address, :created_at, :updated_at)"
            ), {
                'company_id': row[1],
                'name': row[2],
                'email': row[3],
                'phone': row[4],
                'address': row[5],
                'created_at': row[6],
                'updated_at': row[7],
            })
            new_id = result.lastrowid
            supplier_id_map[row[0]] = new_id

        # Rewire inventory_items.supplier_id to new contact ids
        for old_id, new_id in supplier_id_map.items():
            bind.execute(text(
                "UPDATE inventory_items SET supplier_id = :new_id WHERE supplier_id = :old_id"
            ), {'new_id': new_id, 'old_id': old_id})

        # Rewire purchase_orders.supplier_id
        if _table_exists(bind, 'purchase_orders'):
            for old_id, new_id in supplier_id_map.items():
                bind.execute(text(
                    "UPDATE purchase_orders SET supplier_id = :new_id WHERE supplier_id = :old_id"
                ), {'new_id': new_id, 'old_id': old_id})

        # Drop suppliers table
        with op.batch_alter_table('suppliers', schema=None) as batch_op:
            if _index_exists(bind, 'suppliers', 'ix_suppliers_company_id'):
                batch_op.drop_index('ix_suppliers_company_id')
            if _index_exists(bind, 'suppliers', 'ix_suppliers_contact_email'):
                batch_op.drop_index('ix_suppliers_contact_email')
            if _index_exists(bind, 'suppliers', 'ix_suppliers_name'):
                batch_op.drop_index('ix_suppliers_name')
            if _index_exists(bind, 'suppliers', 'ix_suppliers_phone'):
                batch_op.drop_index('ix_suppliers_phone')
        op.drop_table('suppliers')

    # ──────────────────────────────────────────────────────────────
    # 3. MIGRATE clients -> contacts
    # ──────────────────────────────────────────────────────────────
    if _table_exists(bind, 'clients'):
        clients = bind.execute(text(
            "SELECT id, company_id, name, identifier, email, phone, address, created_at, updated_at FROM clients"
        )).fetchall()

        client_id_map = {}
        for row in clients:
            result = bind.execute(text(
                "INSERT INTO contacts (company_id, name, type, identifier, email, phone, address, created_at, updated_at) "
                "VALUES (:company_id, :name, 'customer', :identifier, :email, :phone, :address, :created_at, :updated_at)"
            ), {
                'company_id': row[1],
                'name': row[2],
                'identifier': row[3],
                'email': row[4],
                'phone': row[5],
                'address': row[6],
                'created_at': row[7],
                'updated_at': row[8],
            })
            new_id = result.lastrowid
            client_id_map[row[0]] = new_id

        # Rewire documents.client_id to new contact ids
        if _table_exists(bind, 'documents'):
            for old_id, new_id in client_id_map.items():
                bind.execute(text(
                    "UPDATE documents SET client_id = :new_id WHERE client_id = :old_id"
                ), {'new_id': new_id, 'old_id': old_id})

        # Drop clients table
        with op.batch_alter_table('clients', schema=None) as batch_op:
            if _index_exists(bind, 'clients', 'ix_clients_company_id'):
                batch_op.drop_index('ix_clients_company_id')
            if _index_exists(bind, 'clients', 'ix_clients_email'):
                batch_op.drop_index('ix_clients_email')
            if _index_exists(bind, 'clients', 'ix_clients_identifier'):
                batch_op.drop_index('ix_clients_identifier')
            if _index_exists(bind, 'clients', 'ix_clients_name'):
                batch_op.drop_index('ix_clients_name')
            if _index_exists(bind, 'clients', 'ix_clients_phone'):
                batch_op.drop_index('ix_clients_phone')
        op.drop_table('clients')

    # ──────────────────────────────────────────────────────────────
    # 4. CREATE projects (if not exists)
    # ──────────────────────────────────────────────────────────────
    if not _table_exists(bind, 'projects'):
        op.create_table('projects',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('budget', sa.Float(), nullable=True),
            sa.Column('status', sa.String(), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('projects', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_projects_company_id'), ['company_id'], unique=False)

    # ──────────────────────────────────────────────────────────────
    # 5. CREATE accounts (if not exists)
    # ──────────────────────────────────────────────────────────────
    if not _table_exists(bind, 'accounts'):
        op.create_table('accounts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('balance', sa.Float(), nullable=True),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('is_default', sa.Boolean(), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('accounts', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_accounts_company_id'), ['company_id'], unique=False)

    # ──────────────────────────────────────────────────────────────
    # 6. CREATE expenses (if not exists)
    # ──────────────────────────────────────────────────────────────
    if not _table_exists(bind, 'expenses'):
        op.create_table('expenses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=True),
            sa.Column('supplier_id', sa.Integer(), nullable=True),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('date', sa.DateTime(), nullable=True),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('receipt_url', sa.String(), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
            sa.ForeignKeyConstraint(['supplier_id'], ['contacts.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('expenses', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_expenses_account_id'), ['account_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_expenses_company_id'), ['company_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_expenses_project_id'), ['project_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_expenses_supplier_id'), ['supplier_id'], unique=False)

    # ──────────────────────────────────────────────────────────────
    # 7. CREATE ledger_entries (if not exists)
    # ──────────────────────────────────────────────────────────────
    if not _table_exists(bind, 'ledger_entries'):
        op.create_table('ledger_entries',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('account_id', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=True),
            sa.Column('date', sa.DateTime(), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('debit', sa.Float(), nullable=True),
            sa.Column('credit', sa.Float(), nullable=True),
            sa.Column('reference_type', sa.String(), nullable=True),
            sa.Column('reference_id', sa.Integer(), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('ledger_entries', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_ledger_entries_account_id'), ['account_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_ledger_entries_company_id'), ['company_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_ledger_entries_project_id'), ['project_id'], unique=False)

    # ──────────────────────────────────────────────────────────────
    # 8. CREATE audit_logs (if not exists)
    # ──────────────────────────────────────────────────────────────
    if not _table_exists(bind, 'audit_logs'):
        op.create_table('audit_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('action', sa.String(), nullable=True),
            sa.Column('table_name', sa.String(), nullable=True),
            sa.Column('record_id', sa.Integer(), nullable=True),
            sa.Column('old_data', sa.JSON(), nullable=True),
            sa.Column('new_data', sa.JSON(), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('audit_logs', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_audit_logs_action'), ['action'], unique=False)
            batch_op.create_index(batch_op.f('ix_audit_logs_company_id'), ['company_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_audit_logs_table_name'), ['table_name'], unique=False)
            batch_op.create_index(batch_op.f('ix_audit_logs_user_id'), ['user_id'], unique=False)

    # ──────────────────────────────────────────────────────────────
    # 9. ADD missing columns on existing tables (all guarded)
    # ──────────────────────────────────────────────────────────────
    def safe_add_columns(table, columns):
        with op.batch_alter_table(table, schema=None) as batch_op:
            for col_name, col_def in columns:
                if not _column_exists(bind, table, col_name):
                    batch_op.add_column(col_def)

    safe_add_columns('companies', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('document_items', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('document_sequences', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('documents', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('inventory_items', [
        ('cost_price', sa.Column('cost_price', sa.Float(), nullable=True)),
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('notifications', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('payments', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('permissions', [
        ('description', sa.Column('description', sa.String(), nullable=True)),
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
        ('created_at', sa.Column('created_at', sa.DateTime(), nullable=True)),
        ('updated_at', sa.Column('updated_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('purchase_order_items', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
        ('created_at', sa.Column('created_at', sa.DateTime(), nullable=True)),
        ('updated_at', sa.Column('updated_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('purchase_orders', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('reports', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('roles', [
        ('description', sa.Column('description', sa.String(), nullable=True)),
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
        ('created_at', sa.Column('created_at', sa.DateTime(), nullable=True)),
        ('updated_at', sa.Column('updated_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('stock_movements', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
        ('updated_at', sa.Column('updated_at', sa.DateTime(), nullable=True)),
    ])
    safe_add_columns('users', [
        ('is_deleted', sa.Column('is_deleted', sa.Boolean(), nullable=True)),
        ('deleted_at', sa.Column('deleted_at', sa.DateTime(), nullable=True)),
    ])


def downgrade():
    # Downgrade is intentionally not implemented — restoring
    # migrated suppliers/clients data from contacts would require
    # additional bookkeeping that is out of scope for this migration.
    raise NotImplementedError(
        "Downgrade from consolidate_schema is not supported. "
        "Restore from backup if needed."
    )
