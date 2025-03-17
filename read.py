# read the sqlite file and print the top entreis 

import sqlite3

db = 'db.sqlite'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row  # Use Row factory to access columns by name

def get_top_entries():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries ORDER BY published DESC LIMIT 5')
    return cursor.fetchall()

entries = get_top_entries()

for entry in entries:
    entry = dict(entry)  # Convert Row object to dictionary
    print(entry["title"])  # Print the entry