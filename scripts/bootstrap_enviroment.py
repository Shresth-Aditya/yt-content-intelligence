# scripts/bootstrap_environment.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

sys.path.append(str(Path(__file__).resolve().parents[1]))

from logger import setup_logger

load_dotenv()
SOURCE_DB_URL = os.environ["SOURCE_DB_URL"]
TARGET_DB_URL = os.environ["TARGET_DB_URL"]

BATCH_SIZE = 1000
logger = setup_logger()


def copy_table(
    source_cursor,
    target_cursor,
    table_name,
    columns,
    conflict_columns=None
):
    column_list = ", ".join(columns)
    total_rows_copied = 0

    logger.info(
        "Starting copy for table=%s columns=%s conflict_columns=%s",
        table_name,
        column_list,
        conflict_columns
    )

    source_cursor.execute(
        f"""
        SELECT {column_list}
        FROM {table_name}
        """
    )

    while True:
        rows = source_cursor.fetchmany(BATCH_SIZE)

        if not rows:
            break

        insert_sql = f"""
            INSERT INTO {table_name} (
                {column_list}
            )
            VALUES %s
        """

        if conflict_columns:
            conflict_cols = ", ".join(conflict_columns)

            insert_sql += f"""
                ON CONFLICT ({conflict_cols})
                DO NOTHING
            """

        execute_values(
            target_cursor,
            insert_sql,
            rows,
            page_size=BATCH_SIZE
        )

        total_rows_copied += len(rows)

        logger.info(
            "%s: copied batch_rows=%d total_rows_copied=%d",
            table_name,
            len(rows),
            total_rows_copied
        )

    logger.info(
        "Finished copy for table=%s total_rows_copied=%d",
        table_name,
        total_rows_copied
    )
    return total_rows_copied

def main():
    logger.info(
        "Starting bootstrap with batch_size=%d source_db_configured=%s target_db_configured=%s",
        BATCH_SIZE,
        bool(SOURCE_DB_URL),
        bool(TARGET_DB_URL)
    )

    source_conn = psycopg2.connect(SOURCE_DB_URL)
    target_conn = psycopg2.connect(TARGET_DB_URL)

    try:
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        total_rows_copied = 0

        logger.info("Copying dim_channels")

        total_rows_copied += copy_table(
            source_cursor,
            target_cursor,
            table_name="dim_channels",
            columns=[
                "channel_id",
                "channel_name",
                "description"
            ],
            conflict_columns=["channel_id"]
        )

        logger.info("Copying dim_videos")

        total_rows_copied += copy_table(
            source_cursor,
            target_cursor,
            table_name="dim_videos",
            columns=[
                "video_id",
                "title",
                "description",
                "published_at",
                "channel_id"
            ],
            conflict_columns=["video_id"]
        )

        logger.info("Copying fact_video_snapshots")

        total_rows_copied += copy_table(
            source_cursor,
            target_cursor,
            table_name="fact_video_snapshots",
            columns=[
                "video_id",
                "views",
                "likes",
                "comments",
                "snapshot_date"
            ],
            conflict_columns=[
                "video_id",
                "snapshot_date"
            ]
        )

        target_conn.commit()

        logger.info(
            "Bootstrap completed successfully total_rows_copied=%d",
            total_rows_copied
        )

    except Exception:
        target_conn.rollback()
        logger.exception("Bootstrap failed; rolled back target database changes")
        raise

    finally:
        source_conn.close()
        target_conn.close()
        logger.info("Closed source and target database connections")


if __name__ == "__main__":
    main()
