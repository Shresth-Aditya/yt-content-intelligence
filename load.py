from logger import setup_logger
from database import (
    get_connection,
    release_connection
)
from psycopg2.extras import execute_values
from logger import setup_logger

logger = setup_logger()

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

def insert_video_daily_metrics(metrics, run_id):

    if not metrics:
        return

    conn = get_connection()

    try:

        query = """
            INSERT INTO fact_video_daily_metrics (
                video_id,
                views,
                likes,
                comments,
                snapshot_date,
                snapshot_time,
                run_id
            )
            VALUES %s
            ON CONFLICT (video_id, snapshot_date)
            DO NOTHING
        """

        data = [
            (
                metric["video_id"],
                metric["views"],
                metric["likes"],
                metric["comments"],
                metric["snapshot_date"],
                metric["snapshot_time"],
                run_id
            )
            for metric in metrics
        ]

        with conn.cursor() as cursor:
            execute_values(cursor, query, data)

        conn.commit()

        logger.info(
            "Upserted %d video daily metric rows into database",
            len(metrics)
        )

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
                run_id
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
                run_id = EXCLUDED.run_id
        """

        data = [
            (
                channel["channel_id"],
                channel["channel_name"],
                channel["description"],
                run_id
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

def upsert_dim_videos(videos, run_id):

    if not videos:
        return

    conn = get_connection()

    try:

        query = """
            INSERT INTO dim_videos (
                video_id,
                title,
                description,
                published_at,
                channel_id,
                niche,
                run_id
            )
            VALUES %s
            ON CONFLICT (video_id)
            DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                published_at = EXCLUDED.published_at,
                channel_id = EXCLUDED.channel_id,
                niche = EXCLUDED.niche,
                run_id = EXCLUDED.run_id
        """

        data = [
            (
                video["video_id"],
                video["title"],
                video["description"],
                video["published_at"],
                video["channel_id"],
                video["niche"],
                run_id
            )
            for video in videos
        ]

        with conn.cursor() as cursor:
            execute_values(cursor, query, data)

        conn.commit()

        logger.info(
            "Upserted %d videos into dim_videos",
            len(videos)
        )

    finally:
        release_connection(conn)
