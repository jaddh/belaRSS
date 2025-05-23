import sqlite3

DB_PATH = 'db.sqlite'  # Path to your SQLite DB file

def update_twitter_feeds(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update URLs that match the old Twitter feed pattern
    cursor.execute("""
        UPDATE entries
        SET feed = REPLACE(feed, '/twitter/user/', '/twitter/media/')
        WHERE feed LIKE 'http://localhost:1200/twitter/user/%'
    """)

    conn.commit()
    print(f"Updated {conn.total_changes} Twitter feed URLs.")
    conn.close()

if __name__ == "__main__":
    update_twitter_feeds(DB_PATH)

