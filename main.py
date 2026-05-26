from extract import (
    get_video_statistics,
    search_videos_for_niche
)
from transform import (
    transform_discovered_videos,
    transform_video_statistics
)
from load import (
    insert_video_daily_metrics,
    upsert_dim_channels,
    upsert_dim_videos
)
from logger import setup_logger
from database import (
    get_all_existing_video_ids,
    finish_pipeline_run,
    start_pipeline_run
)
from datetime import (
    datetime,
    time as datetime_time,
    timedelta
)
from zoneinfo import ZoneInfo
import os
import time

logger = setup_logger()

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")
DEFAULT_NICHE_QUERIES = [
    "Python",
    "Python Tutorial",
    "Python Programming",
    "Python Automation",
    "Python Selenium",
    "Python Pytest",
    "Python FastAPI",
    # "Python Django",
    # "Python Flask",
    # "Python Data Science",
    # "Python Machine Learning",
    # "Python AI",
    # "Python Pandas",
    # "Python NumPy",
    # "Python Data Engineering",
    # "Python Web Scraping",
    # "Python Backend Development",
    # "Python APIs",
    # "Python Projects",
    # "Python Developer"
]

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

def get_snapshot_date():

    return datetime.now(IST).date().isoformat()

def get_snapshot_time():

    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

def get_niche_queries():

    raw_queries = os.getenv("NICHE_QUERIES")

    if not raw_queries:
        return DEFAULT_NICHE_QUERIES

    queries = [
        query.strip()
        for query in raw_queries.split(",")
        if query.strip()
    ]

    return queries or DEFAULT_NICHE_QUERIES

def run_pipeline_for_video(video_id, snapshot_date, snapshot_time, run_id):

    raw = get_video_statistics(video_id)
    transformed = transform_video_statistics(raw, snapshot_date, snapshot_time)
    insert_video_daily_metrics(transformed, run_id)
    return len(transformed)

def discover_new_videos_for_niche(niche, window, snapshot_date, snapshot_time, run_id):

    raw = search_videos_for_niche(
        niche,
        window["published_after"],
        window["published_before"]
    )
    transformed = transform_discovered_videos(raw, niche)

    upsert_dim_channels(transformed["channels"], run_id)
    upsert_dim_videos(transformed["videos"], run_id)

    metrics_inserted = 0

    for video in transformed["videos"]:
        metrics_inserted += run_pipeline_for_video(
            video["video_id"],
            snapshot_date,
            snapshot_time,
            run_id
        )

    return {
        "videos_discovered": len(transformed["videos"]),
        "metrics_inserted": metrics_inserted
    }

def write_markdown_summary(metrics):

    summary = f"""# Daily YouTube Pipeline Summary

| Metric | Value |
| --- | --- |
| Run ID | {metrics["run_id"]} |
| Status | {metrics["status"]} |
| Videos processed | {metrics["videos_processed"]} |
| New videos discovered | {metrics["new_videos_discovered"]} |
| Video errors | {metrics["video_errors"]} |
| Discovery errors | {metrics["discovery_errors"]} |
| Execution time seconds | {metrics["execution_time_seconds"]:.2f} |
| Run date | {metrics["run_date"]} |
| Snapshot date | {metrics["snapshot_date"]} |
| Snapshot time | {metrics["snapshot_time"]} |
| Logical date | {metrics["logical_date"]} |
| Published after | {metrics["published_after"]} |
| Published before | {metrics["published_before"]} |
"""

    with open("pipeline_summary.md", "w", encoding="utf-8") as file:
        file.write(summary)

def run_pipeline():

    started_at = time.perf_counter()
    videos_processed = 0
    new_videos_discovered = 0
    video_errors = 0
    discovery_errors = 0
    status = "success"
    run_id = None
    run_date = None

    snapshot_date = get_snapshot_date()
    snapshot_time = get_snapshot_time()
    window = get_previous_day_window()
    niche_queries = get_niche_queries()
    run_id, run_date = start_pipeline_run()

    logger.info(
        "Processing video metrics run_id=%s snapshot_date=%s snapshot_time=%s",
        run_id,
        snapshot_date,
        snapshot_time
    )

    try:
        video_ids = get_all_existing_video_ids()
        logger.info(
            "Loaded %d videos from database",
            len(video_ids)
        )

        for video_id in video_ids:
            logger.info(f"\nProcessing video: {video_id}")

            try:
                videos_processed += run_pipeline_for_video(
                    video_id,
                    snapshot_date,
                    snapshot_time,
                    run_id
                )
            except Exception as e:
                video_errors += 1
                status = "partial_success"
                logger.error(f"Error with {video_id}: {e}")

        logger.info(
            "Discovering new videos for logical_date=%s, published_after=%s, published_before=%s",
            window["logical_date"],
            window["published_after"],
            window["published_before"]
        )

        for niche in niche_queries:
            logger.info(f"\nDiscovering new videos for niche: {niche}")

            try:
                discovery_result = discover_new_videos_for_niche(
                    niche,
                    window,
                    snapshot_date,
                    snapshot_time,
                    run_id
                )
                new_videos_discovered += discovery_result["videos_discovered"]
                videos_processed += discovery_result["metrics_inserted"]
            except Exception as e:
                discovery_errors += 1
                status = "partial_success"
                logger.error(f"Error discovering videos for {niche}: {e}")

    except Exception:
        status = "failed"
        raise

    finally:
        execution_time_seconds = time.perf_counter() - started_at

        if run_id is not None:
            run_date = finish_pipeline_run(
                run_id,
                execution_time_seconds,
                videos_processed,
                status
            )

        write_markdown_summary({
            "run_id": run_id,
            "status": status,
            "videos_processed": videos_processed,
            "new_videos_discovered": new_videos_discovered,
            "video_errors": video_errors,
            "discovery_errors": discovery_errors,
            "execution_time_seconds": execution_time_seconds,
            "run_date": run_date,
            "snapshot_date": snapshot_date,
            "snapshot_time": snapshot_time,
            "logical_date": window["logical_date"],
            "published_after": window["published_after"],
            "published_before": window["published_before"]
        })

        logger.info(
            "Pipeline run %s finished with status=%s, videos_processed=%d, new_videos_discovered=%d",
            run_id,
            status,
            videos_processed,
            new_videos_discovered
        )

if __name__ == "__main__":
    run_pipeline()
