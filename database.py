import sqlite3
DB_NAME = "youtube_pipeline.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_channels_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            channel_id TEXT PRIMARY KEY,
            channel_name TEXT,
            description TEXT,
            subscribers INTEGER,
            total_views INTEGER,
            video_count INTEGER,
            niche TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def insert_channels(channels, niche):

    if not channels:
        return

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT OR REPLACE INTO channels (
            channel_id,
            channel_name,
            description,
            subscribers,
            total_views,
            video_count,
            niche
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    data = [
        (
            ch["channel_id"],
            ch["channel_name"],
            ch["description"],
            ch["subscribers"],
            ch["total_views"],
            ch["video_count"],
            niche
        )
        for ch in channels
    ]

    cursor.executemany(query, data)

    conn.commit()
    conn.close()

def get_all_channel_ids():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT channel_id
        FROM channels
    """)

    rows = cursor.fetchall()

    conn.close()

    return [row[0] for row in rows]