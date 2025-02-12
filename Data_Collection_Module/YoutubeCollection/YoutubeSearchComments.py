import os
import pandas as pd
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
YOUTUBE_API_KEY = os.getenv("AIzaSyD3rGswjIk33bQKe-kNy8YnsG24HwDt028")

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey="AIzaSyD3rGswjIk33bQKe-kNy8YnsG24HwDt028")

def search_youtube_videos(query, max_results=10):
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
    
    except HttpError as e:
        print(f"An error occurred: {e}")
        return []

def get_video_details(video_id):
    """Fetch additional details like views, likes, and comments for a given video."""
    try:
        request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        response = request.execute()
        
        if "items" in response:
            item = response["items"][0]
            stats = item["statistics"]

            return {
                "views": stats.get("viewCount", 0),
                "likes": stats.get("likeCount", 0),
                "comments": stats.get("commentCount", 0)
            }
        return {}

    except HttpError as e:
        print(f"An error occurred: {e}")
        return {}

def get_video_comments(video_id, max_comments=50):
    """Fetches up to 50 top-level comments from a YouTube video using pagination."""
    comments = []
    next_page_token = None
    comments_fetched = 0

    try:
        while comments_fetched < max_comments:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(50, max_comments - comments_fetched),
                textFormat="plainText",
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]["snippet"]
                comment_text = top_comment["textDisplay"]
                author = top_comment["authorDisplayName"]
                likes = top_comment["likeCount"]
                published_at = top_comment["publishedAt"]

                comments.append({
                    "video_id": video_id,
                    "author": author,
                    "comment": comment_text,
                    "likes": likes,
                    "published_at": published_at
                })

                comments_fetched += 1
                if comments_fetched >= max_comments:
                    break  # Stop if we reach the max limit

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break  # No more pages left

            time.sleep(1)  # Avoid hitting API rate limits

    except HttpError as e:
        print(f"Error fetching comments for video {video_id}: {e}")

    return comments

# Example usage
product_name = "iPhone 15 Pro Review"
videos = search_youtube_videos(product_name, max_results=5)

# Fetch extra details for each video
all_comments = []
for video in videos:
    print(f"Fetching data for video: {video['video_id']}...")
    video.update(get_video_details(video["video_id"]))
    
    # Fetch up to 50 comments per video
    comments = get_video_comments(video["video_id"], max_comments=50)
    all_comments.extend(comments)
    
    time.sleep(1)  # Avoid hitting API rate limits

# Save video details to CSV
df_videos = pd.DataFrame(videos)
df_videos.to_csv("Data_Collection_Module/YoutubeCollection/" + "youtube_product_reviews.csv", index=False)
print("YouTube video data saved successfully.")

# Save comments to CSV
df_comments = pd.DataFrame(all_comments)
df_comments.to_csv("Data_Collection_Module/YoutubeCollection/" + "youtube_comments.csv", index=False)
print("YouTube comments saved successfully.")
