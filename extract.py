import requests
from dotenv import load_dotenv
import os
from logger import setup_logger
from datetime import (
    datetime,
    timedelta,
    timezone
)

logger = setup_logger()

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_today_midnight_utc():
    """
    Convert today's 12 AM IST to UTC
    """

    return (
        datetime.now(timezone.utc)
        .replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        - timedelta(hours=5, minutes=30)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_channel_videos(channel_id):

    published_after = (
        get_today_midnight_utc()
    )

    logger.info(
        "Fetching videos after %s",
        published_after
    )

    url = f"https://www.googleapis.com/youtube/v3/search"
    
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "maxResults": 50,
        "order": "date",
        "type": "video",
        "publishedAfter": published_after
    }
    
    response = requests.get(url, params=params)
    logger.debug("API Response: %s", response.json())
    logger.info("Fetched %d videos for channel ID: %s", len(response.json().get("items", [])), channel_id)
    return response.json()