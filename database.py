import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)

def get_connection():
    return pool.getconn()

def release_connection(conn):
    pool.putconn(conn)

def create_channels_table():

    conn = get_connection()
    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    channel_name TEXT,
                    description TEXT,
                    subscribers BIGINT,
                    total_views BIGINT,
                    video_count INTEGER,
                    niche TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
    finally:
        release_connection(conn)

def create_pipeline_runs_table():

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id SERIAL PRIMARY KEY,
                    execution_time_seconds DOUBLE PRECISION,
                    videos_processed INTEGER,
                    status VARCHAR(20),
                    run_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
    finally:
        release_connection(conn)

def insert_pipeline_run(
    execution_time_seconds,
    videos_processed,
    status
):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                INSERT INTO pipeline_runs (
                    execution_time_seconds,
                    videos_processed,
                    status
                )
                VALUES (%s, %s, %s)
                RETURNING id, run_date
            """, (
                execution_time_seconds,
                videos_processed,
                status
            ))

            run_id, run_date = cursor.fetchone()

        conn.commit()
        return run_id, run_date

    finally:
        release_connection(conn)

def insert_channels(channels, niche):
    
    if not channels:
        return

    conn = get_connection()

    try:

        query = """
            INSERT INTO channels (
                channel_id,
                channel_name,
                description,
                subscribers,
                total_views,
                video_count,
                niche
            )
            VALUES %s
            ON CONFLICT (channel_id)
            DO UPDATE SET
                channel_name = EXCLUDED.channel_name,
                description = EXCLUDED.description,
                subscribers = EXCLUDED.subscribers,
                total_views = EXCLUDED.total_views,
                video_count = EXCLUDED.video_count,
                niche = EXCLUDED.niche
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

        with conn.cursor() as cursor:

            execute_values(cursor, query, data)

        conn.commit()

    finally:
        release_connection(conn)

def get_all_channel_ids():

    conn = get_connection()
    
    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT channel_id
                FROM channels
            """)

            rows = cursor.fetchall()

        return [row[0] for row in rows]

    finally:
        release_connection(conn)
