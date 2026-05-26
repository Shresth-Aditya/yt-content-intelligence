from logger import setup_logger

logger = setup_logger()

def transform_video_data(raw_data,channel_id):
    videos = []
    
    for item in raw_data.get("items", []):
        
        if item["id"]["kind"] != "youtube#video":
            continue  # skip playlists, channels
        
        snippet = item["snippet"]
        logger.debug("Processing item: %s", item)
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": snippet["title"],
            "channel_id": channel_id,
            "description": snippet["description"],
            "published_at": snippet["publishedAt"]
        })
    
    return videos

def transform_video_statistics(raw_data, snapshot_date,snapshot_time):
    metrics = []

    for item in raw_data.get("items", []):

        statistics = item.get("statistics", {})
        logger.debug("Processing video statistics item: %s", item)

        metrics.append({
            "video_id": item["id"],
            "views": int(statistics.get("viewCount", 0)),
            "likes": int(statistics.get("likeCount", 0)),
            "comments": int(statistics.get("commentCount", 0)),
            "snapshot_date": snapshot_date,
            "snapshot_time": snapshot_time
        })

    return metrics

def transform_discovered_videos(raw_data, niche):
    videos_by_id = {}
    channels_by_id = {}

    for item in raw_data.get("items", []):

        if item["id"]["kind"] != "youtube#video":
            continue

        snippet = item["snippet"]
        channel_id = snippet["channelId"]

        channels_by_id[channel_id] = {
            "channel_id": channel_id,
            "channel_name": snippet.get("channelTitle", channel_id),
            "description": ""
        }

        videos_by_id[item["id"]["videoId"]] = {
            "video_id": item["id"]["videoId"],
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "published_at": snippet["publishedAt"],
            "channel_id": channel_id,
            "niche": niche
        }

    return {
        "channels": list(channels_by_id.values()),
        "videos": list(videos_by_id.values())
    }
