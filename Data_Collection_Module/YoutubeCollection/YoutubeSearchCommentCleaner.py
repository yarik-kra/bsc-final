import pandas as pd
import re

def clean_text(text):
    """Removes mentions, links, emojis, and extra spaces from comments."""
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'http\S+|www\S+', '', text)  # Remove links
    text = re.sub(r'[^a-zA-Z0-9.,!?\'" ]+', '', text)  # Keep only readable characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

def is_meaningful_comment(comment):
    """Checks if a comment is long enough and contains relevant keywords."""
    keywords = {"iphone", "apple", "battery", "upgrade", "camera", "quality", 
                "performance", "screen", "review", "display", "charging", "phone", "android", "switch"}

    if len(comment.split()) < 6:  # Ignore short comments
        return False
    
    return any(word in comment.lower() for word in keywords)

def clean_youtube_comments(input_csv="youtube_comments.csv", output_csv="cleaned_youtube_comments.csv"):
    """Cleans YouTube comments and saves filtered results to a new CSV."""
    df = pd.read_csv(input_csv)
    df["cleaned_comment"] = df["comment"].apply(clean_text)
    df = df[df["cleaned_comment"].apply(is_meaningful_comment)]
    df = df[["video_id", "cleaned_comment"]]
    df.to_csv(output_csv, index=False)
    print(f"Cleaned comments saved to: {output_csv}")

if __name__ == "__main__":
    clean_youtube_comments()
