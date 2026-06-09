from db.video_repository import insert_video_daily_metrics
from youtube_api.youtube_client import fetch_video_statistics
from youtube_api.youtube_transformers import transform_video_statistics
from utils.time_utils import get_snapshot_time


VIDEO_METRICS_BATCH_SIZE = 50


def chunk_video_ids(video_ids):
    for index in range(0, len(video_ids), VIDEO_METRICS_BATCH_SIZE):
        yield video_ids[index:index + VIDEO_METRICS_BATCH_SIZE]


def fetch_process_video_metrics(video_ids, snapshot_date, run_id):

    metric_snapshot_time = get_snapshot_time()
    raw = fetch_video_statistics(video_ids)
    transformed = transform_video_statistics(raw, snapshot_date, metric_snapshot_time)
    insert_video_daily_metrics(transformed, run_id)
    return len(transformed)
