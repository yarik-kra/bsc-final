import pandas as pd
import re

def clean_text(text):
    """Removes user mentions, links, emojis, excessive spaces, and irrelevant data from comments."""
    text = re.sub(r'@\w+', '', text)  # Remove usernames (e.g., @username)
    text = re.sub(r'http\S+|www\S+', '', text)  # Remove links (http, www)
    text = re.sub(r'[^a-zA-Z0-9.,!?\'" ]+', '', text)  # Keep only readable characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

def is_meaningful_comment(comment):
    """Checks if a comment is long enough and contains meaningful product-related words."""
    common_words = ["iphone", "apple", "battery", "upgrade", "camera", "quality", 
                    "performance", "screen", "review", "display", "charging", "phone", "android", "switch"]

    if len(comment.split()) < 6:  # Ignore very short comments
        return False
    
    comment_lower = comment.lower()
    return any(word in comment_lower for word in common_words)  # Keep comments with relevant words

def clean_youtube_comments(input_csv="youtube_comments.csv", output_csv="cleaned_youtube_comments.csv"):
    """Reads YouTube comments dataset, cleans it, and saves a new filtered CSV."""
    # Load dataset
    df = pd.read_csv(input_csv)

    # Apply cleaning functions
    df["cleaned_comment"] = df["comment"].apply(clean_text)
    df = df[df["cleaned_comment"].apply(is_meaningful_comment)]  # Keep only meaningful comments

    # Drop unnecessary columns and save
    df = df[["video_id", "cleaned_comment"]]
    df.to_csv(output_csv, index=False)

    print(f"✅ Cleaned comments saved to: {output_csv}")

# Run the script
if __name__ == "__main__":
    clean_youtube_comments()
