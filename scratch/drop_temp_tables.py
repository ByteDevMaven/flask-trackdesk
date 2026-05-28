import sqlite3

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '_alembic_tmp_%'")
tables = cursor.fetchall()
for t in tables:
    cursor.execute(f'DROP TABLE {t[0]}')
    print(f'Dropped {t[0]}')

conn.commit()
conn.close()
