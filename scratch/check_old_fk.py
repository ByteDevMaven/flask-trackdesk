import sqlite3

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    if t[1] and ('REFERENCES clients' in t[1] or 'REFERENCES suppliers' in t[1]):
        print(f'Table {t[0]} has old references')

conn.close()
