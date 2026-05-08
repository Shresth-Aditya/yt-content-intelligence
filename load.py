import sqlite3
from logger import setup_logger
from database import get_connection
from logger import setup_logger

logger = setup_logger()

def create_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        channel_id TEXT,
        title TEXT,
        description TEXT,
        published_at TEXT,
        FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
    )
    """)

    conn.commit()
    conn.close()


def insert_videos(videos):

    conn = get_connection()

    cursor = conn.cursor()
    for video in videos:

        cursor.execute("""
        INSERT OR IGNORE INTO videos
        VALUES (?, ?, ?, ?, ?)
        """, (

            video["video_id"],

            video["channel_id"],

            video["title"],

            video["description"],

            video["published_at"]
        ))

    conn.commit()
    conn.close()

    logger.info(
        "Inserted %d videos into database",
        len(videos)
    )