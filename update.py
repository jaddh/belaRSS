from reader import make_reader
from datetime import datetime

def update_app_feeds():
    print(f"[{datetime.now()}] Updating database...")
    from NLP import extract_entities
    reader = make_reader('db.sqlite')
    reader.update_feeds()
    extract_entities()
    print(f"[{datetime.now()}] Update completed.")

update_app_feeds()
