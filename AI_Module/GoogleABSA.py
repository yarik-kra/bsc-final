import os
import re
import json
import spacy
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from collections import defaultdict

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Load sentiment model
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Define file paths
DATA_FILE = "Data_Collection_Module/GoogleSearchCollection/processed_dataset.json"
OUTPUT_FILE = "AI_Module/analyzed_sentiments.json"

# Sentiment labels map
SENTIMENT_MAP = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

# Clean text
def clean_text(text):
    """Remove unwanted symbols and normalize text."""
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Extract aspects
def extract_aspects(sentences):
    """Use noun chunking to extract aspects."""
    aspect_counts = defaultdict(int)

    for sentence in sentences:
        doc = nlp(sentence)
        for chunk in doc.noun_chunks:
            aspect = chunk.text.lower().strip()
            aspect_counts[aspect] += 1

    # Filter out stopwords
    stopwords = {"the", "it", "this", "that", "i", "you", "we", "one", "they", "all", "app",
                 "d", "only", "way", "head", "which", "me", "min", "bo"}
    aspects = [aspect for aspect, count in aspect_counts.items() if count > 1 and aspect not in stopwords]
    return aspects if aspects else ["general"]

# Map sentiment
def map_sentiment_label(label, score):
    """Convert model output to detailed sentiment categories."""
    mapped_label = SENTIMENT_MAP.get(label, "Unknown")
    # Classify strength by score
    if score > 0.85:
        return f"Strong {mapped_label}"
    elif score > 0.70:
        return f"Moderate {mapped_label}"
    elif score > 0.40:
        return f"Weak {mapped_label}"
    else:
        return f"Very Weak {mapped_label}"

# Analyze sentiments
def analyze_sentiments(sentences, aspects):
    """Perform aspect-based sentiment analysis."""
    results = []

    for sentence in sentences:
        sentiment_result = sentiment_pipeline(sentence)[0]
        label = map_sentiment_label(sentiment_result['label'], sentiment_result['score'])
        score = round(sentiment_result['score'], 4)

        # Debug: print classification
        print(f"\nSentence: {sentence}\nSentiment: {label} (Score: {score})")

        # Skip low confidence
        if score < 0.40:
            print("Skipping: Very low confidence")
            continue

        # Identify aspects
        related_aspects = [aspect for aspect in aspects if aspect in sentence.lower()]
        print(f"Detected Aspects: {related_aspects}")

        results.append({
            "sentence": sentence,
            "sentiment": label,
            "score": score,
            "aspects": related_aspects if related_aspects else ["general"]
        })

    return results

# Load data
with open(DATA_FILE, "r", encoding="utf-8") as f:
    dataset = json.load(f)

# Extract sentences
sentences = [entry["original_text"] for entry in dataset]

# Detect aspects
detected_aspects = extract_aspects(sentences)

# Analyze sentiments
sentiment_results = analyze_sentiments(sentences, detected_aspects)

# Save results
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(sentiment_results, f, indent=4)

print(f"Sentiment analysis completed and saved to {OUTPUT_FILE}")
