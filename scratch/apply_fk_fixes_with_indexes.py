import sqlite3

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

cursor.execute('PRAGMA foreign_keys=off;')

tables = ['documents', 'inventory_items', 'purchase_orders']

for t in tables:
    # Get table sql
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'")
    row = cursor.fetchone()
    if not row:
        continue
    sql = row[0]
    
    if 'REFERENCES clients' in sql or 'REFERENCES suppliers' in sql:
        # Get indexes
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{t}' AND sql IS NOT NULL")
        indexes = [r[0] for r in cursor.fetchall()]
        
        new_sql = sql.replace('REFERENCES clients', 'REFERENCES contacts')
        new_sql = new_sql.replace('REFERENCES suppliers', 'REFERENCES contacts')
        
        cursor.execute(f"ALTER TABLE {t} RENAME TO {t}_old")
        cursor.execute(new_sql)
        cursor.execute(f"INSERT INTO {t} SELECT * FROM {t}_old")
        cursor.execute(f"DROP TABLE {t}_old")
        
        # Recreate indexes
        for idx_sql in indexes:
            cursor.execute(idx_sql)
            
        print(f"Fixed old references and restored indexes for {t}")

conn.commit()
conn.close()
