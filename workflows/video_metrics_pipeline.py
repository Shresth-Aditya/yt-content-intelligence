from db.video_repository import insert_video_daily_metrics
from youtube_api.youtube_client import fetch_video_statistics
from youtube_api.youtube_transformers import transform_video_statistics
from utils.time_utils import get_snapshot_time



def fetch_process_video_metrics(video_id, snapshot_date, run_id):

    metric_snapshot_time = get_snapshot_time()
    raw = fetch_video_statistics(video_id)
    transformed = transform_video_statistics(raw, snapshot_date, metric_snapshot_time)
    insert_video_daily_metrics(transformed, run_id)
    return len(transformed)
