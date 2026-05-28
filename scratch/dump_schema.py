import sqlite3

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

for t in ['documents', 'inventory_items', 'purchase_orders']:
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'")
    print(f'-- {t} --')
    print(cursor.fetchone()[0])

conn.close()
