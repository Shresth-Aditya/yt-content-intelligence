from db.channel_repository import upsert_dim_channels
from db.video_repository import get_existing_video_ids, upsert_dim_videos
from workflows.video_metrics_pipeline import fetch_process_video_metrics
from youtube_api.youtube_client import search_videos_for_niche
from youtube_api.youtube_transformers import transform_discovered_videos


def discover_process_new_videos_for_niche(
    niche,
    window,
    snapshot_date,
    run_id
):

    raw = search_videos_for_niche(
        niche,
        window["published_after"],
        window["published_before"]
    )
    transformed = transform_discovered_videos(raw, niche)

    existing_video_ids = set(get_existing_video_ids(
        video["video_id"]
        for video in transformed["videos"]
    ))
    
    new_videos = [
        video
        for video in transformed["videos"]
        if video["video_id"] not in existing_video_ids
    ]

    upsert_dim_channels(transformed["channels"], run_id)
    upsert_dim_videos(new_videos, run_id)

    metrics_inserted = 0

    for video in new_videos:
        metrics_inserted += fetch_process_video_metrics(
            video["video_id"],
            snapshot_date,
            run_id
        )

    return {
        "videos_discovered": len(new_videos),
        "metrics_inserted": metrics_inserted
    }
