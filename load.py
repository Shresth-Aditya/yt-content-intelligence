from logger import setup_logger
from database import (
    get_connection,
    release_connection
)
from psycopg2.extras import execute_values
from logger import setup_logger

logger = setup_logger()

def create_videos_table():

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,
                    channel_id TEXT,
                    title TEXT,
                    description TEXT,
                    published_at TIMESTAMP,
                    FOREIGN KEY (channel_id)
                        REFERENCES channels(channel_id)
                )
            """)

        conn.commit()

    finally:
        release_connection(conn)

def insert_videos(videos):

    if not videos:
        return

    conn = get_connection()

    try:

        query = """
            INSERT INTO videos (
                video_id,
                channel_id,
                title,
                description,
                published_at
            )
            VALUES %s
            ON CONFLICT (video_id)
            DO NOTHING
        """

        data = [
            (
                video["video_id"],
                video["channel_id"],
                video["title"],
                video["description"],
                video["published_at"]
            )
            for video in videos
        ]

        with conn.cursor() as cursor:
            execute_values(cursor, query, data)

        conn.commit()

        logger.info(
            "Inserted %d videos into database",
            len(videos)
        )

    finally:
        release_connection(conn)