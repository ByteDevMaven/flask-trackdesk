"""unify_contacts

Revision ID: 0c2495f8e36b
Revises: 0e4aaddd35d0
Create Date: 2026-05-18 22:03:12.973090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c2495f8e36b'
down_revision = '0e4aaddd35d0'
branch_labels = None
depends_on = None


def upgrade():
    # Get connection
    bind = op.get_bind()
    
    from sqlalchemy import inspect
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    
    # 1. Create contacts table if not exists
    if 'contacts' not in tables:
        op.create_table('contacts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('identifier', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(), nullable=True),
            sa.Column('phone', sa.String(), nullable=True),
            sa.Column('address', sa.String(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    try:
        if 'clients' in tables and 'suppliers' in tables:
            # Get columns to check for optional fields
            client_cols = [c['name'] for c in inspector.get_columns('clients')]
            supplier_cols = [c['name'] for c in inspector.get_columns('suppliers')]
            
            # Helper to get column or fallback
            def get_col(col_name, cols):
                return col_name if col_name in cols else f"'' AS {col_name}"
            
            client_ident = get_col("identifier", client_cols)
            client_email = get_col("email", client_cols)
            client_phone = get_col("phone", client_cols)
            client_address = get_col("address", client_cols)
            
            supplier_ident = get_col("identifier", supplier_cols)
            supplier_email = get_col("email", supplier_cols)
            supplier_phone = get_col("phone", supplier_cols)
            supplier_address = get_col("address", supplier_cols)
            
            # Get max client ID to calculate offset
            result = bind.execute(sa.text("SELECT COALESCE(MAX(id), 0) FROM clients"))
            max_client_id = result.scalar()
            
            offset = max_client_id + 1000
            
            print(f"Migrating data with offset {offset}...")
            
            # Insert clients (ID preserved)
            bind.execute(sa.text(f"""
                INSERT INTO contacts (id, company_id, name, type, identifier, email, phone, address)
                SELECT id, company_id, name, 'customer', {client_ident.replace(' AS identifier', '')}, {client_email.replace(' AS email', '')}, {client_phone.replace(' AS phone', '')}, {client_address.replace(' AS address', '')} FROM clients
            """))
            
            # Insert suppliers (ID shifted)
            bind.execute(sa.text(f"""
                INSERT INTO contacts (id, company_id, name, type, identifier, email, phone, address)
                SELECT id + {offset}, company_id, name, 'supplier', {supplier_ident.replace(' AS identifier', '')}, {supplier_email.replace(' AS email', '')}, {supplier_phone.replace(' AS phone', '')}, {supplier_address.replace(' AS address', '')} FROM suppliers
            """))
            
            # Update inventory_items (supplier_id shifted)
            bind.execute(sa.text(f"""
                UPDATE inventory_items SET supplier_id = supplier_id + {offset} WHERE supplier_id IS NOT NULL
            """))
            
            # Update purchase_orders (supplier_id shifted)
            bind.execute(sa.text(f"""
                UPDATE purchase_orders SET supplier_id = supplier_id + {offset} WHERE supplier_id IS NOT NULL
            """))
            
            # Drop old tables
            op.drop_table('clients')
            op.drop_table('suppliers')
            
            print("Data migration completed successfully.")
        else:
            print("Old tables 'clients' or 'suppliers' not found, skipping data migration.")
        
    except Exception as e:
        print(f"Error during data migration: {str(e)}")
        raise e

def downgrade():
    # This is a complex destructive migration, downgrade is not easily supported without losing the 'type' distinction if we split them back, or we can just drop contacts.
    # Since it's a structural merge, we usually don't support clean downgrades without data loss.
    op.drop_table('contacts')

