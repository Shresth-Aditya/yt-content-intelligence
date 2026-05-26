# channel_discovery.py
import os
from typing import Counter
import requests
from logger import setup_logger
from database import insert_channels
from dotenv import load_dotenv

load_dotenv()
logger = setup_logger()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"


def discover_channel_ids_from_niche(
    niche,
    max_results_per_page=50,
    max_pages=2
):
    """
    Search videos for a niche
    Extract unique channel IDs across multiple pages
    """

    url = f"{BASE_URL}/search"
    unique_channel_ids = set()
    next_page_token = None
    total_videos = 0

    try:

        for page_number in range(max_pages):

            params = {
                "key": YOUTUBE_API_KEY,
                "q": niche,
                "part": "snippet",
                "type": "video",
                "maxResults": max_results_per_page
            }

            # Add page token after first page
            if next_page_token:
                params["pageToken"] = next_page_token

            response = requests.get(
                url,
                params=params
            )

            response.raise_for_status()

            data = response.json()

            items = data.get("items", [])

            total_videos += len(items)

            # Extract channel IDs
            for item in items:

                channel_id = item["snippet"]["channelId"]

                unique_channel_ids.add(
                    channel_id
                )

            logger.info(
                "Page %d fetched with %d videos",
                page_number + 1,
                len(items)
            )

            # Get next page token
            next_page_token = data.get(
                "nextPageToken"
            )

            # Stop if no more pages
            if not next_page_token:

                logger.info(
                    "No more pages available"
                )

                break

        logger.info(
            "Discovered %d unique channels from %d videos for niche: %s",
            len(unique_channel_ids),
            total_videos,
            niche
        )

        return list(unique_channel_ids)

    except Exception as e:

        logger.error(
            "Error in channel discovery: %s",
            str(e)
        )

        return []

def fetch_channel_metadata(channel_ids):
    """
    Step 2:
    Fetch channel statistics + metadata
    """

    if not channel_ids:
        return []

    url = f"{BASE_URL}/channels"

    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet,statistics",
        "id": ",".join(channel_ids)
    }

    try:

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        items = data.get("items", [])

        logger.info(
            "Fetched metadata for %d channels",
            len(items)
        )

        channels = []

        for item in items:

            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})

            channel_data = {

                "channel_id": item["id"],

                "channel_name": snippet.get(
                    "title",
                    ""
                ),

                "description": snippet.get(
                    "description",
                    ""
                ),

                "subscribers": int(
                    stats.get(
                        "subscriberCount",
                        0
                    )
                ),

                "total_views": int(
                    stats.get(
                        "viewCount",
                        0
                    )
                ),

                "video_count": int(
                    stats.get(
                        "videoCount",
                        0
                    )
                )
            }

            channels.append(channel_data)

        return channels

    except Exception as e:

        logger.error(
            "Error fetching channel metadata: %s",
            str(e)
        )

        return []

def filter_channels_by_subscribers(
    channels,
    min_subscribers=10000
):
    """
    Filter channels by subscriber count
    """

    if not channels:

        logger.warning(
            "No channels received for filtering"
        )

        return []

    filtered = []

    for channel in channels:

        subscribers = channel[
            "subscribers"
        ]

        logger.debug(
            "Channel %s → %d subscribers",
            channel["channel_name"],
            subscribers
        )

        if subscribers >= min_subscribers:

            filtered.append(channel)

    logger.info(
        "%d/%d channels passed subscriber filter (%d subs)",
        len(filtered),
        len(channels),
        min_subscribers
    )

    return filtered


def get_channel_ids_for_niche(
    niche,
    max_results=20,
    min_subscribers=10000
):
    """
    Full pipeline:

    niche
        ↓
    search videos
        ↓
    extract channels
        ↓
    fetch metadata
        ↓
    filter channels
        ↓
    store in sqlite
    """

    logger.info(
        "Starting channel discovery for niche: %s",
        niche
    )

    # Step 1
    channel_ids = (
        discover_channel_ids_from_niche(
            niche=niche,
            max_results=max_results
        )
    )

    logger.info(
        "Proceeding to metadata stage"
    )

    # Step 2
    channels = fetch_channel_metadata(
        channel_ids
    )

    logger.info(
        "Proceeding to filtering stage"
    )

    # Step 3
    filtered_channels = (
        filter_channels_by_subscribers(
            channels,
            min_subscribers=min_subscribers
        )
    )

    # Step 4
    insert_channels(
        filtered_channels,
        niche
    )

    logger.info(
        "Stored %d channels into SQLite",
        len(filtered_channels)
    )

    return filtered_channels
