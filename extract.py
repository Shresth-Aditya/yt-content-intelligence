import requests
from dotenv import load_dotenv
import os
from logger import setup_logger

logger = setup_logger()

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_channel_videos(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/search"
    
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "maxResults": 10,
        "order": "date",
        "type": "video" 
    }
    
    response = requests.get(url, params=params)
    logger.debug("API Response: %s", response.json())
    logger.info("Fetched %d videos for channel ID: %s", len(response.json().get("items", [])), channel_id)
    return response.json()