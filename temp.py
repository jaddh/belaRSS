import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

# Execute the SQL query to count entries per day
query = """
    SELECT 
        DATE(published) AS date,
        COUNT(*) AS count
    FROM 
        entries
    GROUP BY 
        DATE(published)
    ORDER BY 
        date;
"""
cursor.execute(query)

# Fetch and print the results
rows = cursor.fetchall()
for row in rows:
    print(f"Date: {row[0]}, Count: {row[1]}")

# Clean up
cursor.close()
conn.close()