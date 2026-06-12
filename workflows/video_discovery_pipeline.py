from db.bronze_youtube_api_response_repository import insert_bronze_youtube_api_response
from db.channel_repository import upsert_dim_channels
from db.video_repository import get_existing_video_ids, upsert_dim_videos
from workflows.video_metrics_pipeline import chunk_video_ids, fetch_process_video_metrics
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
    source_bronze_id = insert_bronze_youtube_api_response(
        raw,
        run_id,
        snapshot_date,
        None
    )
    transformed = transform_discovered_videos(raw, niche, source_bronze_id)

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

    new_video_ids = [
        video["video_id"]
        for video in new_videos
    ]

    for video_id_batch in chunk_video_ids(new_video_ids):
        metrics_inserted += fetch_process_video_metrics(
            video_id_batch,
            snapshot_date,
            run_id
        )

    return {
        "videos_discovered": len(new_videos),
        "metrics_inserted": metrics_inserted
    }
