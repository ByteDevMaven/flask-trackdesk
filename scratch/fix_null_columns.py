import sqlite3

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

# Fix null values in inventory_items for NOT NULL columns
cursor.execute("UPDATE inventory_items SET cost_price = 0 WHERE cost_price IS NULL")
cursor.execute("UPDATE inventory_items SET price = 0 WHERE price IS NULL")
cursor.execute("UPDATE inventory_items SET discount = 0 WHERE discount IS NULL")
cursor.execute("UPDATE inventory_items SET quantity = 0 WHERE quantity IS NULL")

# Fix document_items nulls
cursor.execute("UPDATE document_items SET quantity = 1 WHERE quantity IS NULL")
cursor.execute("UPDATE document_items SET unit_price = 0 WHERE unit_price IS NULL")
cursor.execute("UPDATE document_items SET discount = 0 WHERE discount IS NULL")
cursor.execute("UPDATE document_items SET description = '' WHERE description IS NULL")
cursor.execute("UPDATE document_items SET document_id = (SELECT MIN(id) FROM documents) WHERE document_id IS NULL")

# Fix documents nulls
cursor.execute("UPDATE documents SET total_amount = 0 WHERE total_amount IS NULL")

# Fix payments nulls
cursor.execute("UPDATE payments SET amount = 0 WHERE amount IS NULL")
cursor.execute("UPDATE payments SET payment_date = CURRENT_TIMESTAMP WHERE payment_date IS NULL")

# Fix expenses nulls  
cursor.execute("UPDATE expenses SET amount = 0 WHERE amount IS NULL")

# Fix projects nulls
cursor.execute("UPDATE projects SET budget = 0 WHERE budget IS NULL")

# Fix ledger_entries nulls
cursor.execute("UPDATE ledger_entries SET debit = 0 WHERE debit IS NULL")
cursor.execute("UPDATE ledger_entries SET credit = 0 WHERE credit IS NULL")

# Fix audit_logs nulls
cursor.execute("UPDATE audit_logs SET action = 'unknown' WHERE action IS NULL")
cursor.execute("UPDATE audit_logs SET table_name = 'unknown' WHERE table_name IS NULL")

# Fix accounts nulls
cursor.execute("UPDATE accounts SET balance = 0 WHERE balance IS NULL")

conn.commit()

# Report
for t in ['inventory_items', 'document_items', 'documents', 'payments', 'expenses', 'projects', 'ledger_entries', 'accounts']:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"{t}: {cursor.fetchone()[0]} rows")

conn.close()
print("Done fixing nulls!")
