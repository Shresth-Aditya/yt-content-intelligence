from extract import get_channel_videos
from transform import transform_video_data
from load import create_videos_table, insert_videos
from logger import setup_logger
from database import (
    create_pipeline_runs_table,
    get_all_channel_ids,
    insert_pipeline_run
)
from datetime import (
    datetime,
    time as datetime_time,
    timedelta
)
from zoneinfo import ZoneInfo
import time

logger = setup_logger()

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

def get_previous_day_window():
    """
    Build a closed IST daily window:
    yesterday 12 AM IST <= published_at < today 12 AM IST.
    """

    today_ist = datetime.now(IST).date()
    logical_date = today_ist - timedelta(days=1)

    window_start_ist = datetime.combine(
        logical_date,
        datetime_time.min,
        tzinfo=IST
    )
    window_end_ist = window_start_ist + timedelta(days=1)

    return {
        "logical_date": logical_date.isoformat(),
        "published_after": window_start_ist.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "published_before": window_end_ist.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def run_pipeline_for_channel(
    channel_id,
    published_after,
    published_before
):
    raw = get_channel_videos(
        channel_id,
        published_after,
        published_before
    )
    transformed = transform_video_data(raw,channel_id)
    insert_videos(transformed)
    return len(transformed)

def write_markdown_summary(metrics):

    summary = f"""# Daily YouTube Pipeline Summary

| Metric | Value |
| --- | --- |
| Run ID | {metrics["run_id"]} |
| Status | {metrics["status"]} |
| Videos processed | {metrics["videos_processed"]} |
| Channels processed | {metrics["channels_processed"]} |
| Channel errors | {metrics["channel_errors"]} |
| Execution time seconds | {metrics["execution_time_seconds"]:.2f} |
| Run date | {metrics["run_date"]} |
| Logical date | {metrics["logical_date"]} |
| Published after | {metrics["published_after"]} |
| Published before | {metrics["published_before"]} |
"""

    with open("pipeline_summary.md", "w", encoding="utf-8") as file:
        file.write(summary)

def run_pipeline():

    started_at = time.perf_counter()
    videos_processed = 0
    channels_processed = 0
    channel_errors = 0
    status = "success"

    create_pipeline_runs_table()
    create_videos_table()  # only once
    window = get_previous_day_window()

    logger.info(
        "Processing logical_date=%s, published_after=%s, published_before=%s",
        window["logical_date"],
        window["published_after"],
        window["published_before"]
    )

    try:
        channel_ids = get_all_channel_ids()
        logger.info(
            "Loaded %d channels from database",
            len(channel_ids)
        )

        for channel_id in channel_ids:
            logger.info(f"\nProcessing channel: {channel_id}")

            try:
                videos_processed += run_pipeline_for_channel(
                    channel_id,
                    window["published_after"],
                    window["published_before"]
                )
                channels_processed += 1
            except Exception as e:
                channel_errors += 1
                status = "partial_success"
                logger.error(f"Error with {channel_id}: {e}")

    except Exception:
        status = "failed"
        raise

    finally:
        execution_time_seconds = time.perf_counter() - started_at

        run_id, run_date = insert_pipeline_run(
            execution_time_seconds,
            videos_processed,
            status
        )

        write_markdown_summary({
            "run_id": run_id,
            "status": status,
            "videos_processed": videos_processed,
            "channels_processed": channels_processed,
            "channel_errors": channel_errors,
            "execution_time_seconds": execution_time_seconds,
            "run_date": run_date,
            "logical_date": window["logical_date"],
            "published_after": window["published_after"],
            "published_before": window["published_before"]
        })

        logger.info(
            "Pipeline run %s finished with status=%s, videos_processed=%d",
            run_id,
            status,
            videos_processed
        )

if __name__ == "__main__":
    run_pipeline()
