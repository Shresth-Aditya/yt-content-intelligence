from db.pipeline_run_repository import finish_pipeline_run
from db.video_repository import get_all_existing_video_ids
from logger import setup_logger
from workflows.pipeline_summary import write_markdown_summary
from workflows.video_discovery_pipeline import discover_process_new_videos_for_niche
from workflows.video_metrics_pipeline import fetch_process_video_metrics

logger = setup_logger()


def process_existing_video_metrics(
    snapshot_date,
    run_id,
    stats
):

    video_ids = get_all_existing_video_ids()
    logger.info(
        "Loaded %d videos from database",
        len(video_ids)
    )

    if not video_ids:
        logger.warning("No existing videos found; skipping existing video metrics step")
        return

    for video_id in video_ids:
        logger.info(f"\nProcessing video: {video_id}")

        try:
            stats.videos_processed += fetch_process_video_metrics(
                video_id,
                snapshot_date,
                run_id
            )
        except Exception as e:
            stats.video_errors += 1
            stats.mark_partial_success()
            logger.error(f"Error with {video_id}: {e}")


def discover_process_new_videos(
    window,
    snapshot_date,
    niche_queries,
    run_id,
    stats
):

    logger.info(
        "Discovering new videos for logical_date=%s, published_after=%s, published_before=%s",
        window["logical_date"],
        window["published_after"],
        window["published_before"]
    )

    for niche in niche_queries:
        logger.info(f"\nDiscovering new videos for niche: {niche}")

        try:
            discovery_result = discover_process_new_videos_for_niche(
                niche,
                window,
                snapshot_date,
                run_id
            )
            stats.new_videos_discovered += discovery_result["videos_discovered"]
            stats.videos_processed += discovery_result["metrics_inserted"]
        except Exception as e:
            stats.discovery_errors += 1
            stats.mark_partial_success()
            logger.error(f"Error discovering videos for {niche}: {e}")
            

def finalize_pipeline_run_and_generate_summary(
    run_id,
    execution_time_seconds,
    stats,
    snapshot_date,
    snapshot_time,
    window,
    run_date
):

    if run_id is not None:
        run_date = finish_pipeline_run(
            run_id,
            execution_time_seconds,
            stats.videos_processed,
            stats.status
        )

    write_markdown_summary({
        "run_id": run_id,
        "status": stats.status,
        "videos_processed": stats.videos_processed,
        "new_videos_discovered": stats.new_videos_discovered,
        "video_errors": stats.video_errors,
        "discovery_errors": stats.discovery_errors,
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
        stats.status,
        stats.videos_processed,
        stats.new_videos_discovered
    )
