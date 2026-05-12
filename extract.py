import requests
from dotenv import load_dotenv
import os
from logger import setup_logger

logger = setup_logger()

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_channel_videos(
    channel_id,
    published_after,
    published_before
):

    logger.info(
        "Fetching videos from %s to %s",
        published_after,
        published_before
    )

    url = f"https://www.googleapis.com/youtube/v3/search"
    
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "maxResults": 50,
        "order": "date",
        "type": "video",
        "publishedAfter": published_after,
        "publishedBefore": published_before
    }
    
    response = requests.get(
        url,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    logger.debug("API Response: %s", response.json())
    logger.info("Fetched %d videos for channel ID: %s", len(response.json().get("items", [])), channel_id)
    return response.json()
