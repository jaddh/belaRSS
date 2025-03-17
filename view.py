import sqlite3

def create_view():
    # Connect to the database
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    # SQL code to create the view
    create_view_sql = """
    CREATE VIEW feed_meta AS
    SELECT 
        feeds.*,
        COUNT(entries.id) AS entry_count
    FROM 
        feeds
    LEFT JOIN 
        entries ON feeds.url = entries.feed
    GROUP BY 
        feeds.url;
    """

    # Execute the SQL code
    cursor.execute(create_view_sql)
    conn.commit()

    # Close the connection
    conn.close()

if __name__ == "__main__":
    create_view()
