from db.channel_repository import upsert_dim_channels
from db.video_repository import upsert_dim_videos
from workflows.video_metrics_pipeline import fetch_process_video_metrics
from youtube_api.youtube_client import search_videos_for_niche
from youtube_api.youtube_transformers import transform_discovered_videos


def discover_process_new_videos_for_niche(
    niche,
    window,
    snapshot_date,
    snapshot_time,
    run_id
):

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
        metrics_inserted += fetch_process_video_metrics(
            video["video_id"],
            snapshot_date,
            snapshot_time,
            run_id
        )

    return {
        "videos_discovered": len(transformed["videos"]),
        "metrics_inserted": metrics_inserted
    }
