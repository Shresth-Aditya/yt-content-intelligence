import time
import sys

from config import get_niche_queries
from db.pipeline_run_repository import start_pipeline_run
from db.pipeline_state_repository import (
    has_discovery_run_for_date,
    mark_discovery_run_for_date
)
from logger import setup_logger
from workflows.pipeline_stats import PipelineStats
from workflows.pipeline_steps import (
    discover_process_new_videos,
    finalize_pipeline_run_and_generate_summary,
    process_existing_video_metrics
)
from utils.time_utils import (
    get_previous_day_window,
    get_snapshot_date,
    get_snapshot_time
)

logger = setup_logger()


def get_exit_code_for_status(status):
    return 0 if status == "success" else 1


def run_pipeline():

    snapshot_date = get_snapshot_date()
    snapshot_time = get_snapshot_time()
    window = get_previous_day_window()
    niche_queries = get_niche_queries()

    started_at = time.perf_counter()
    stats = PipelineStats()
    run_id = None
    run_date = None

    try:
        run_id, run_date = start_pipeline_run()

        logger.info(
            "Processing video metrics run_id=%s snapshot_date=%s snapshot_time=%s",
            run_id,
            snapshot_date,
            snapshot_time
        )

        process_existing_video_metrics(
            snapshot_date=snapshot_date,
            run_id=run_id,
            stats=stats
        )

        if has_discovery_run_for_date(snapshot_date):
            logger.info(
                "Skipping discovery; it already ran for snapshot_date=%s",
                snapshot_date
            )
        else:
            if not niche_queries:
                raise ValueError("No niche queries configured")

            discover_process_new_videos(
                window=window,
                snapshot_date=snapshot_date,
                snapshot_time=snapshot_time,
                niche_queries=niche_queries,
                run_id=run_id,
                stats=stats
            )
            mark_discovery_run_for_date(snapshot_date)

    except Exception:
        stats.mark_failed()
        logger.exception("Pipeline failed with an unhandled error")
        raise

    finally:
        execution_time_seconds = time.perf_counter() - started_at

        try:
            finalize_pipeline_run_and_generate_summary(
                run_id=run_id,
                execution_time_seconds=execution_time_seconds,
                stats=stats,
                snapshot_date=snapshot_date,
                snapshot_time=snapshot_time,
                window=window,
                run_date=run_date
            )
        except Exception:
            stats.mark_failed()
            logger.exception("Failed to finalize pipeline run")
            raise

    return stats.status


if __name__ == "__main__":
    try:
        status = run_pipeline()
    except Exception:
        sys.exit(1)

    sys.exit(get_exit_code_for_status(status))
