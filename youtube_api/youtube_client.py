import os

from dotenv import load_dotenv
import requests

from logger import setup_logger

logger = setup_logger()

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"


def fetch_channel_videos(
    channel_id,
    published_after,
    published_before
):

    logger.info(
        "Fetching videos from %s to %s",
        published_after,
        published_before
    )

    url = f"{BASE_URL}/search"

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

    raw_data = response.json()
    logger.debug("Channel videos API response: %s", raw_data)
    logger.info(
        "Fetched %d videos for channel ID: %s",
        len(raw_data.get("items", [])),
        channel_id
    )

    return raw_data


def fetch_video_statistics(video_ids):

    logger.info(
        "Fetching statistics for %d video(s)",
        len(video_ids)
    )

    url = f"{BASE_URL}/videos"

    params = {
        "key": YOUTUBE_API_KEY,
        "id": ",".join(video_ids),
        "part": "statistics"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )
    response.raise_for_status()

    raw_data = response.json()
    logger.debug("Video statistics API response: %s", raw_data)
    logger.info(
        "Fetched statistics for %d video(s)",
        len(raw_data.get("items", []))
    )

    return raw_data


def search_videos_for_niche(
    niche,
    published_after,
    published_before,
    max_results_per_page=50,
    max_pages=1
):

    logger.info(
        "Searching videos for niche=%s from %s to %s",
        niche,
        published_after,
        published_before
    )

    url = f"{BASE_URL}/search"
    items = []
    next_page_token = None

    for page_number in range(max_pages):

        params = {
            "key": YOUTUBE_API_KEY,
            "q": niche,
            "part": "snippet",
            "type": "video",
            "maxResults": max_results_per_page,
            "order": "date",
            "publishedAfter": published_after,
            "publishedBefore": published_before
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(
            url,
            params=params,
            timeout=30
        )
        response.raise_for_status()

        raw_data = response.json()
        page_items = raw_data.get("items", [])
        items.extend(page_items)

        logger.info(
            "Fetched %d videos for niche=%s on page %d",
            len(page_items),
            niche,
            page_number + 1
        )

        next_page_token = raw_data.get("nextPageToken")

        if not next_page_token:
            break

    return {
        "items": items
    }
