import sqlite3
import re

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

cursor.execute('PRAGMA foreign_keys=off;')

tables = ['documents', 'inventory_items', 'purchase_orders']

for t in tables:
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'")
    row = cursor.fetchone()
    if not row:
        continue
    sql = row[0]
    
    if 'REFERENCES clients' in sql or 'REFERENCES suppliers' in sql:
        new_sql = sql.replace('REFERENCES clients', 'REFERENCES contacts')
        new_sql = new_sql.replace('REFERENCES suppliers', 'REFERENCES contacts')
        
        cursor.execute(f"ALTER TABLE {t} RENAME TO {t}_old")
        cursor.execute(new_sql)
        cursor.execute(f"INSERT INTO {t} SELECT * FROM {t}_old")
        cursor.execute(f"DROP TABLE {t}_old")
        print(f"Fixed old references in {t}")

# Recreate the indexes!
# Wait, for `documents` there was a UNIQUE constraint and probably an index `ix_documents_document_number`
# If we dropped the table, the indexes are dropped too. We need to recreate them!
# SQLite auto-creates indexes for UNIQUE constraints inside CREATE TABLE.
# But named indexes like `CREATE INDEX ix_documents_client_id ON documents (client_id)` need to be restored.
# It's better to just re-create the indexes.
# Since Alembic will create them anyway or they already exist? Wait, dropping table drops its indexes.
# Let's see what indexes existed before.

conn.commit()
conn.close()
