import os
import re
import json
import spacy
from transformers import DebertaTokenizer

# Load NLP model
nlp = spacy.load("en_core_web_sm")  

# Load DeBERTa tokenizer
tokenizer = DebertaTokenizer.from_pretrained("microsoft/deberta-large")

# Define directory paths
DATA_DIR = "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/sentiment_ready_texts"
OUTPUT_FILE = "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/processed_dataset.json"

# Define cleaning patterns
REMOVE_PATTERNS = [
    r"you are using an out of date browser.*?",
    r"this sidebar will go away.*?",
    r"http\S+|www\S+",  # Remove URLs
    r"\s+",  # Normalize extra spaces
    r"\[.*?\]",  # Remove text inside square brackets (e.g., [deleted])
    r"^\W*$",  # Remove non-word characters (like "-----")
    r"^\d+$",  # Remove isolated numbers
    r"\b(thanks|hello|hi|goodbye|bye|ok|okay|hmm|huh|yeah|nope|idk)\b",  # Remove common chat noise
    r"\b(i guess|i think|i feel|maybe|perhaps|sort of|kind of|not sure)\b"  # Remove hesitation phrases
]

# **Expanded Sentiment Keywords**
SENTIMENT_KEYWORDS = [
    # Positive Sentiment
    "love", "like", "enjoy", "prefer", "awesome", "amazing", "fantastic", "great", "good", "excellent",
    "best", "wonderful", "outstanding", "positive", "pleasant", "satisfying", "impressive",
    "helpful", "recommend", "worth it", "game changer", "life saver", "highly recommend",

    # Negative Sentiment
    "hate", "dislike", "awful", "terrible", "horrible", "worst", "bad", "frustrating", "annoying",
    "disappointed", "not worth it", "waste of money", "waste of time", "regret", "useless",
    "poor", "flawed", "broken", "misleading", "deceptive", "overpriced", "not impressed",
    
    # Comparative Sentiment
    "better than", "worse than", "compared to", "versus", "faster", "slower", "cheaper", "more expensive",
    "higher quality", "lower quality", "stronger", "weaker", "lighter", "heavier", "more reliable",
    "less reliable", "more powerful", "less powerful", "more efficient", "less efficient",

    # Experience-based Sentiment
    "tried", "using", "experienced", "tested", "reviewed", "upgraded", "downgraded",
    "used for a while", "been using", "long-term use", "after a few weeks", "after a few months",
    "real-world use", "actual experience", "in daily use", "for my workflow", "day-to-day experience",
    
    # Opinion-related Sentiment
    "i think", "i believe", "i feel", "in my opinion", "imo", "from my perspective",
    "in my experience", "my take on this", "from what i've seen", "seems like", "feels like",
    "probably", "most likely", "definitely", "certainly", "absolutely", "undoubtedly",
    
    # Common Complaint & Praise Phrases
    "it sucks", "it rocks", "not worth it", "totally worth it", "i regret", "i don’t regret",
    "i’m happy with", "i’m disappointed in", "best purchase", "worst purchase", "would buy again",
    "never buying again", "customer service sucks", "customer service is great",
    
    # Specific Feature Sentiment (For Tech Reviews)
    "battery life is great", "battery drains fast", "camera is amazing", "camera is bad",
    "performance is solid", "performance is terrible", "design is sleek", "build quality is poor",
    "screen is bright", "screen is dull", "sound is clear", "sound is muffled"
]

# Function to clean text
def clean_text(text):
    """Remove system messages, ads, and normalize numbers."""
    for pattern in REMOVE_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    # Normalize currency values (remove commas in numbers like 1,599 -> 1599)
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)  

    text = re.sub(r"\s+", " ", text).strip()
    return text

# Function to filter sentences using keyword matching
def is_relevant(sentence):
    """Check if a sentence contains sentiment-related words."""
    return any(word in sentence.lower() for word in SENTIMENT_KEYWORDS)

# Function to merge short related sentences
def merge_short_sentences(sentences, min_length=40):
    """Merge short consecutive sentences that belong together."""
    merged_sentences = []
    buffer = ""

    for sentence in sentences:
        if len(sentence) < min_length:
            buffer += " " + sentence
        else:
            if buffer:
                merged_sentences.append(buffer.strip())
                buffer = ""
            merged_sentences.append(sentence)

    if buffer:
        merged_sentences.append(buffer.strip())

    return merged_sentences

# Function to split and filter sentences
def split_sentences(text):
    """Split discussions into individual sentences while preserving product context."""
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if is_relevant(sent.text.strip())]
    
    # Merge short relevant sentences to preserve context
    return merge_short_sentences(sentences)

# Process text files
def process_text_files():
    dataset = []
    
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.isfile(filepath) and filename.startswith("site_"):
            with open(filepath, "r", encoding="utf-8") as file:
                raw_text = file.read()

            cleaned_text = clean_text(raw_text)
            sentences = split_sentences(cleaned_text)

            if not sentences:
                continue  # Skip files that contain no relevant sentences

            tokenized_texts = tokenizer(sentences, padding="longest", truncation=True, max_length=512, return_tensors="pt")

            for i, sentence in enumerate(sentences):
                input_ids = tokenized_texts["input_ids"][i].tolist()
                attention_mask = tokenized_texts["attention_mask"][i].tolist()

                # Ensure the sentence has at least 5 non-padding tokens before adding to the dataset
                num_non_padding_tokens = sum(attention_mask)
                if num_non_padding_tokens < 5:
                    continue  

                dataset.append({
                    "filename": filename,
                    "original_text": sentence,
                    "tokenized_input_ids": input_ids,
                    "tokenized_attention_mask": attention_mask
                })

    return dataset

# Run processing and save dataset
dataset = process_text_files()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4)

print(f"✅ Processed dataset saved with {len(dataset)} relevant entries.")
