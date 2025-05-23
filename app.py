# run a simple flask app
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
from flask import Flask, g, render_template, send_file, request, jsonify, redirect, url_for
import sqlite3
import json
from reader import make_reader
from datetime import datetime
import matplotlib.pyplot as plt
import requests
from shapely import wkt

reader = make_reader('db.sqlite')

app = Flask(__name__)

db = 'db.sqlite'

@app.template_filter('load_json')
def load_json_filter(s):
    return json.loads(s)

@app.template_filter('wkt_to_coord')
def wkt_to_coord(s):
    geometry = wkt.loads(s)
    return "{}, {}".format(geometry.y, geometry.x)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(db)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.route('/entries/<int:year>/<int:month>/<int:day>')
def entries(year=0, month=0, day=0):
    feed = request.args.get('feed_id', None)

    # If any component is zero, use today's date
    if year == 0 or month == 0 or day == 0:
        today = datetime.today()
        return redirect(url_for('entries', year=today.year, month=today.month, day=today.day))
        
    # Create date range for the selected day
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    date_start = f"{date_str} 00:00:00"
    date_end = f"{date_str} 23:59:59"

    # Get locations
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT label, geometry FROM locations WHERE geometry != 'POINT (38.996815 34.80207499999999)'")
    locations = {row['label']: row['geometry'] for row in cursor.fetchall()}

    # Get entries published on that day
    sql = """
        SELECT * FROM entries 
        WHERE datetime(published) BETWEEN ? AND ? 
        ORDER BY published DESC 
    """
    cursor.execute(sql, (date_start, date_end))
    entries = cursor.fetchall()

    return render_template('entries.html',
                           entries=entries,
                           locations=locations,
                           page="Entries", 
                           year = year, 
                           day = day, 
                           month = month)
        
@app.route('/feeds')
def feeds():
    # get feeds from feeds view
    cursor = get_db().cursor()
    # feed_meta is the name of the view
    feeds = cursor.execute('SELECT * FROM feed_meta ORDER BY entry_count DESC').fetchall()
    return render_template('feeds.html', 
                           feeds=feeds,
                           page = "Feeds")
    
@app.route('/search', methods=['GET'])
def search_form():
    return render_template('search_form.html', 
                           page = "Search")
    
@app.route('/search', methods=['POST'])
def search_results():
    query = request.form.get('query', '')
    keywords = [kw.strip() for kw in query.split(',') if kw.strip()]

    if not keywords:
        return 'No valid keywords provided.', 400

    cursor = get_db().cursor()

    # Build SQL query dynamically using OR conditions
    conditions = " OR ".join([
        "(title LIKE ? OR summary LIKE ? OR content LIKE ?)"
        for _ in keywords
    ])
    parameters = []
    for kw in keywords:
        wildcard = f"%{kw}%"
        parameters.extend([wildcard, wildcard, wildcard])

    sql = f"SELECT * FROM entries WHERE {conditions} ORDER BY published DESC LIMIT 100"
    cursor.execute(sql, parameters)
    results = cursor.fetchall()

    return render_template('entries.html',
                           feed=None,
                           entries=results,
                           locations={},
                           start=0,
                           limit=100,
                           total_entries=len(results),
                           next_start=0,
                           prev_start=0,
                           page="Search Results")

# update the feeds
# update the feeds
@app.route('/update')
def update():
    feed_url = request.args.get('feed')
    if feed_url:
        try:
            reader.update_feed(feed_url)
        except Exception as e:
            return f'Error updating feed {feed_url}: {str(e)}', 400
    else:
        reader.update_feeds()
        return 'All feeds updated!', 200

@app.route('/new_feed')
def new_feed():
    return render_template('new_feed.html', page = "New Feed") 

@app.route('/add_feed', methods=['POST'])
def add_feed():
    data = request.json
    feed_type = data.get('type')
    
    reader = make_reader('db.sqlite')
    
    if feed_type == 'rss':
        url = data.get('title')
    elif feed_type == 'twitter':
        url = "http://localhost:1200/twitter/user/{}".format(data.get('title'))
    elif feed_type == 'telegram':
        url = "http://localhost:1200/telegram/channel/{}".format(data.get('title'))
    elif feed_type == 'instagram':
        url = "http://localhost:1200/picnob/user/{}".format(data.get('title'))
    else:
        return jsonify({'message': 'Invalid feed type'}), 400
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({'message': 'Failed to add feed: ' + response.text}), 400
        print(reader.add_feed(url))
    except Exception as e:
        return jsonify({'message': 'Failed to add feed: '
                        + str(e)}), 400    
    
    return jsonify({'message': 'Feed added successfully'}), 201

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        


@app.route('/calendar/heatmap')
def heatmap_data():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    query = """
        SELECT 
            DATE(published) AS date,
            COUNT(*) AS count
        FROM 
            entries
        GROUP BY 
            DATE(published)
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Convert to UNIX timestamps for the JS heatmap
    heatmap_data = {}
    for date_str, count in rows:
        if date_str:
            ts = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
            heatmap_data[ts] = count

    return jsonify(heatmap_data)



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)


# This is a simple Flask app that runs a web server on port 5000.
