# belaRSS

belaRSS is a simple RSS reader application built with Flask. It allows users to add and manage feeds from various sources including Twitter, Telegram, and RSS.

## Features

- Add new feeds (Twitter, Telegram, RSS)
- View entries from feeds
- Filter entries by feed
- Pagination for entries
- Sidebar for easy navigation
- Update feeds periodically
- View a chart of the number of publications per hour for the last 48 hours

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/belaRSS.git
    cd belaRSS
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:
    ```bash
    python -c "from app import get_db; get_db().executescript(open('schema.sql').read())"
    ```

5. Run the application:
    ```bash
    python app.py
    ```

## API Endpoints

### Add a New Feed

- **URL:** `/add_feed`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "type": "rss" | "twitter" | "telegram",
        "title": "Feed Title",
        "url": "Feed URL"
    }
    ```
- **Response:**
    - Success: `201 Created`
        ```json
        {
            "message": "Feed added successfully"
        }
        ```
    - Error: `400 Bad Request`
        ```json
        {
            "message": "Error message"
        }
        ```

## Templates

### `index.html`

The base template that includes the sidebar and main content area.

### `entries.html`

Template to display entries with pagination.

### `add_feed.html`

Form to add a new feed.

## Static Files

### `styles.css`

Custom styles for the application, including the sidebar.

## Database

### `create_feed_view.sql`

SQL script to create a view that includes feed data along with the count of entries.

## Running the Application

To run the application, execute the following command:
```bash
python app.py
```

The application will be available at `http://localhost:5000`.

## License

This project is licensed under the MIT License.

## To commit to git: 
1. git add .
2. git commit -m "message"
3. git push origin main


## Crontab 

```
@reboot cd /home/jaddh/belaRSS/RSSHub && /home/jaddh/.local/share/pnpm/pnpm start pnmp
0 * * * * cd /home/jaddh/belaRSS && /home/jaddh/belaRSS/.venv/bin/python update.py
@reboot cd /home/jaddh/belaRSS && /home/jaddh/belaRSS/.venv/bin/python app.py
```