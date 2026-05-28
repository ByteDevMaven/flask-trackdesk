import sqlite3

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

cursor.execute('PRAGMA foreign_keys=off;')

child_tables = ['document_items', 'purchase_order_items', 'stock_movements', 'payments']

for t in child_tables:
    # Get table sql
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'")
    row = cursor.fetchone()
    if not row:
        continue
    sql = row[0]
    
    # Check if they have _old references
    if '_old' in sql:
        # Get indexes
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{t}' AND sql IS NOT NULL")
        indexes = [r[0] for r in cursor.fetchall()]
        
        # Replace _old
        new_sql = sql.replace('documents_old', 'documents')
        new_sql = new_sql.replace('inventory_items_old', 'inventory_items')
        new_sql = new_sql.replace('purchase_orders_old', 'purchase_orders')
        
        cursor.execute(f"ALTER TABLE {t} RENAME TO {t}_old")
        cursor.execute(new_sql)
        cursor.execute(f"INSERT INTO {t} SELECT * FROM {t}_old")
        cursor.execute(f"DROP TABLE {t}_old")
        
        # Recreate indexes
        for idx_sql in indexes:
            # Need to replace the table name in index creation too if it changed, but it shouldn't have changed, it's just the index name.
            cursor.execute(idx_sql)
            
        print(f"Fixed old references and restored indexes for {t}")

conn.commit()
conn.close()
