import os
import pandas as pd
import time
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
YOUTUBE_API_KEY = os.getenv("AIzaSyD3rGswjIk33bQKe-kNy8YnsG24HwDt028")

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey="AIzaSyD3rGswjIk33bQKe-kNy8YnsG24HwDt028")

def search_youtube_videos(query, max_results=15):
    """Search for YouTube videos related to the query."""
    try:
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results
        )
        response = request.execute()
        
        video_data = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel_title = item["snippet"]["channelTitle"]
            published_at = item["snippet"]["publishedAt"]

            video_data.append({
                "video_id": video_id,
                "title": title,
                "channel": channel_title,
                "published_at": published_at,
                "video_url": f"https://www.youtube.com/watch?v={video_id}"
            })
        
        return video_data
    
    except Exception as e:
        print(f"An error occurred while searching videos: {e}")
        return []

def get_video_transcript(video_id):
    """Fetch transcript for a given YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry["text"] for entry in transcript])  # Combine text into one string
        return transcript_text
    
    except TranscriptsDisabled:
        print(f"❌ No transcript available for video: {video_id}")
        return None
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None

# Example usage
product_name = "iPhone 15 Pro Review"
videos = search_youtube_videos(product_name, max_results=15)

# Fetch transcripts
video_transcripts = []
for video in videos:
    print(f"Fetching transcript for video: {video['video_id']}...")
    transcript = get_video_transcript(video["video_id"])
    
    if transcript:
        video["transcript"] = transcript
        video_transcripts.append(video)
    
    time.sleep(1)  # Prevent hitting API rate limits

# Save transcripts to CSV
df_transcripts = pd.DataFrame(video_transcripts)
df_transcripts.to_csv("youtube_transcripts.csv", index=False)
print("✅ YouTube transcripts saved successfully.")
