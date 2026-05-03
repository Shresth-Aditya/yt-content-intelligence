from extract import get_channel_videos
from transform import transform_video_data
from load import create_table, insert_videos

CHANNEL_ID = "UC8butISFwT-Wl7EV0hUK0BQ"

def run_pipeline():
    raw = get_channel_videos(CHANNEL_ID)
    transformed = transform_video_data(raw)

    create_table()
    insert_videos(transformed)

if __name__ == "__main__":
    run_pipeline()