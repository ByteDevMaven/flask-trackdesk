import sqlite3

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='documents'")
print("documents:", cursor.fetchone()[0])
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='document_items'")
print("document_items:", cursor.fetchone()[0])

conn.close()
