import sqlite3
from logger import setup_logger

logger = setup_logger()

def create_table():
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        published_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_videos(videos):
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()

    for video in videos:
        cursor.execute("""
        INSERT OR IGNORE INTO videos VALUES (?, ?, ?, ?)
        """, (
            video["video_id"],
            video["title"],
            video["description"],
            video["published_at"]
        ))
    
    conn.commit()
    conn.close()
    logger.info(f"Inserted {len(videos)} videos into the database")