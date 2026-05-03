from logger import setup_logger

logger = setup_logger()

def transform_video_data(raw_data):
    videos = []
    
    for item in raw_data.get("items", []):
        
        if item["id"]["kind"] != "youtube#video":
            continue  # skip playlists, channels
        
        snippet = item["snippet"]
        logger.debug("Processing item: %s", item)
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": snippet["title"],
            "description": snippet["description"],
            "published_at": snippet["publishedAt"]
        })
    
    return videos