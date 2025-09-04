import sqlite3

def get_db_connection():
    connection = sqlite3.connect("url_shortener.db")
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shortcode TEXT UNIQUE NOT NULL,
        original_url TEXT NOT NULL,
        expiry DATETIME
    )
    """)

 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clicks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        referrer TEXT,
        ip TEXT,
        FOREIGN KEY (link_id) REFERENCES links (id)
    )
    """)

    conn.commit()
    conn.close()
