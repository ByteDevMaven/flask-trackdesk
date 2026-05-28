import sqlite3

conn = sqlite3.connect('instance/trackdesk.db')
cursor = conn.cursor()

# Check for null identifiers in contacts
cursor.execute("SELECT id FROM contacts WHERE identifier IS NULL OR identifier = ''")
null_contacts = cursor.fetchall()

for row in null_contacts:
    contact_id = row[0]
    cursor.execute('UPDATE contacts SET identifier = ? WHERE id = ?', (f'UNKNOWN-{contact_id}', contact_id))

if null_contacts:
    conn.commit()
    print(f'Fixed {len(null_contacts)} contacts with null identifiers.')

# Drop alembic tmp table again if exists
cursor.execute('DROP TABLE IF EXISTS _alembic_tmp_contacts')
conn.commit()
conn.close()
