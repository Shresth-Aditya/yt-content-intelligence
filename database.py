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

def start_pipeline_run():

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                INSERT INTO pipeline_runs (
                    status
                )
                VALUES (%s)
                RETURNING run_id, run_date
            """, (
                "running",
            ))

            run_id, run_date = cursor.fetchone()

        conn.commit()
        return run_id, run_date

    finally:
        release_connection(conn)

def finish_pipeline_run(
    run_id,
    execution_time_seconds,
    videos_processed,
    status
):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                UPDATE pipeline_runs
                SET
                    execution_time_seconds = %s,
                    videos_processed = %s,
                    status = %s
                WHERE run_id = %s
                RETURNING run_date
            """, (
                execution_time_seconds,
                videos_processed,
                status,
                run_id
            ))

            row = cursor.fetchone()

        conn.commit()

        if row is None:
            raise ValueError(f"Pipeline run {run_id} does not exist")

        return row[0]

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
                RETURNING run_id, run_date
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

def get_all_existing_video_ids():

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT video_id
                FROM dim_videos
            """)

            rows = cursor.fetchall()

        return [row[0] for row in rows]

    finally:
        release_connection(conn)
