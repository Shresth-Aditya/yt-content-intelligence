from extract import get_channel_videos
from transform import transform_video_data
from load import create_videos_table, insert_videos
from logger import setup_logger
from database import (
    create_pipeline_runs_table,
    get_all_channel_ids,
    insert_pipeline_run
)
import time

logger = setup_logger()

def run_pipeline_for_channel(channel_id):
    raw = get_channel_videos(channel_id)
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

    try:
        channel_ids = get_all_channel_ids()
        logger.info(
            "Loaded %d channels from database",
            len(channel_ids)
        )

        for channel_id in channel_ids:
            logger.info(f"\nProcessing channel: {channel_id}")

            try:
                videos_processed += run_pipeline_for_channel(channel_id)
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
            "run_date": run_date
        })

        logger.info(
            "Pipeline run %s finished with status=%s, videos_processed=%d",
            run_id,
            status,
            videos_processed
        )

if __name__ == "__main__":
    run_pipeline()
