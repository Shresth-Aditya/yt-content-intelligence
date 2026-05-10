from extract import get_channel_videos
from transform import transform_video_data
from load import create_videos_table, insert_videos
from logger import setup_logger
from database import get_all_channel_ids

logger = setup_logger()

def run_pipeline_for_channel(channel_id):
    raw = get_channel_videos(channel_id)
    transformed = transform_video_data(raw,channel_id)
    insert_videos(transformed)

def run_pipeline():
    
    create_videos_table()  # only once

    channel_ids = get_all_channel_ids()
    logger.info(
        "Loaded %d channels from database",
        len(channel_ids)
    )

    for channel_id in channel_ids:
        logger.info(f"\nProcessing channel: {channel_id}")

        try:
            run_pipeline_for_channel(channel_id)
        except Exception as e:
            logger.error(f"Error with {channel_id}: {e}")

if __name__ == "__main__":
    run_pipeline()