import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_channel_videos(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/search"
    
    params = {
        "key": API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "maxResults": 10,
        "order": "date"
    }
    
    response = requests.get(url, params=params)
    return response.json()