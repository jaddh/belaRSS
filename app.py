# run a simple flask app
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
from flask import Flask, g, render_template, send_file, request, jsonify
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

def get_top_entries(start=0, limit=10, feed=None):
    cursor = get_db().cursor()
    if feed:
        sql = "SELECT * FROM entries WHERE feed = '{}' ORDER BY published DESC LIMIT {} OFFSET {}".format(feed, limit, start)
    else:
        sql = 'SELECT * FROM entries ORDER BY published DESC LIMIT {} OFFSET {}'.format(limit, start)
    cursor.execute(sql)
    entries = cursor.fetchall()
    for entry in entries:
        entry_dict = dict(entry)
        if entry_dict.get('enclosures'):
            entry_dict['enclosures'] = json.loads(entry_dict['enclosures'])
        yield entry_dict

def update_feeds():
    with app.app_context():
        print('Updating feeds at ' + str(datetime.now()))
        reader.update_feeds()
        print('Feeds updated! at ' + str(datetime.now()))

@app.route('/<int:start>/<int:limit>')
def entries(start=0, limit=50):
    # if feed in url parameter, get the feed
    feed = request.args.get('feed_id', None)
    entries = list(get_top_entries(start, limit, feed))
    # also print the total number of entries in the database
    cursor = get_db().cursor()
    cursor.execute('SELECT COUNT(*) FROM entries')
    total_entries = cursor.fetchone()[0]
    print('Total entries: ' + str(total_entries))
    locations = cursor.execute("SELECT label, geometry from locations where geometry != 'POINT (38.996815 34.80207499999999)'")
    locations = {row['label']: row['geometry'] for row in locations}
    # render template from file index.html
    return render_template('entries.html',
                           feed=feed,
                           entries=entries,
                           locations = locations, 
                           start=start, 
                           limit=limit, 
                           total_entries=total_entries, 
                           next_start=start + limit, 
                           prev_start=start - limit,
                           page = "Entries")
        
@app.route('/feeds')
def feeds():
    # get feeds from feeds view
    cursor = get_db().cursor()
    # feed_meta is the name of the view
    feeds = cursor.execute('SELECT * FROM feed_meta ORDER BY entry_count DESC').fetchall()
    return render_template('feeds.html', 
                           feeds=feeds,
                           page = "Feeds")

# update the feeds
@app.route('/update')
def update():
    update_feeds()
    return 'Feeds updated!'

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
        
# route that returns a chart of the number of publications per hour for the last 7 days
@app.route('/chart')
def chart():
    cursor = get_db().cursor()
    cursor.execute('SELECT COUNT(*) as count, strftime("%Y-%m-%d %H", published) as hour FROM entries WHERE published > datetime("now", "-4 days") GROUP BY hour')
    rows = cursor.fetchall()
    # render chart in matplotlib

    hours = [row['hour'] for row in rows]
    counts = [row['count'] for row in rows]
    plt.bar(hours, counts)
    plt.xlabel('Hour')
    plt.ylabel('Number of publications')
    plt.title('Number of publications per hour for the last 48 hours')
    plt.xticks(rotation=45, ha='right', fontsize=3)
    plt.tight_layout()
    plt.savefig('cache/chart.png', dpi=300)
    plt.close()
    # return file to be opened in the browser
    return send_file('cache/chart.png', mimetype='image/png')



if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0", debug=True)
    except Exception as e:
        print(e)
        scheduler.shutdown()


# This is a simple Flask app that runs a web server on port 5000.
