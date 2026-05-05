# channel_discovery.py
import os
import requests
from logger import setup_logger

logger = setup_logger()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"

def discover_channel_ids_from_niche(niche, max_results=20):
    url = f"{BASE_URL}/search"
    
    params = {
        "key": YOUTUBE_API_KEY,
        "q": niche,
        "part": "snippet",
        "type": "video",
        "maxResults": max_results
    }

    response = requests.get(url, params=params)
    logger.debug("Channel discovery API Response: %s", response.json())
    data = response.json()
    logger.info("Discovered %d channels for niche: %s", len(data.get("items", [])), niche)
    channel_ids = list({
        item["snippet"]["channelId"]
        for item in data.get("items", [])
    })

    return channel_ids

def filter_channels_by_subscribers(channel_ids, min_subscribers=10000):
    if not channel_ids:
        return []

    url = f"{BASE_URL}/channels"

    params = {
        "key": YOUTUBE_API_KEY,
        "part": "statistics",
        "id": ",".join(channel_ids)
    }

    response = requests.get(url, params=params)
    data = response.json()
    logger.debug("Channel stats API Response: %s", data)
    filtered = []

    for item in data.get("items", []):
        subs = int(item["statistics"].get("subscriberCount", 0))
        if subs >= min_subscribers:
            filtered.append(item["id"])

    return filtered


def get_channel_ids_for_niche(niche):
    """
    Combined function:
    niche → filtered channel_ids
    """
    channel_ids = discover_channel_ids_from_niche(niche)
    channel_ids = filter_channels_by_subscribers(channel_ids)

    return channel_ids