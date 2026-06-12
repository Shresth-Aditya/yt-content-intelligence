from psycopg2.extras import execute_values

from db.connection import get_connection, release_connection
from logger import setup_logger

logger = setup_logger()


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


def upsert_dim_channels(channels, run_id):

    if not channels:
        return

    conn = get_connection()

    try:

        query = """
            INSERT INTO dim_channels (
                channel_id,
                channel_name,
                description,
                run_id,
                source_bronze_id
            )
            VALUES %s
            ON CONFLICT (channel_id)
            DO UPDATE SET
                channel_name = COALESCE(
                    NULLIF(EXCLUDED.channel_name, ''),
                    dim_channels.channel_name
                ),
                description = COALESCE(
                    NULLIF(EXCLUDED.description, ''),
                    dim_channels.description
                ),
                run_id = EXCLUDED.run_id,
                source_bronze_id = EXCLUDED.source_bronze_id
        """

        data = [
            (
                channel["channel_id"],
                channel["channel_name"],
                channel["description"],
                run_id,
                channel["source_bronze_id"]
            )
            for channel in channels
        ]

        with conn.cursor() as cursor:
            execute_values(cursor, query, data)

        conn.commit()

        logger.info(
            "Upserted %d channels into dim_channels",
            len(channels)
        )

    finally:
        release_connection(conn)
