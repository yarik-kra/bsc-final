import os
import re
import json
import spacy
from transformers import DebertaTokenizer

# Load NLP model
nlp = spacy.load("en_core_web_sm")  # SpaCy for sentence segmentation

# Load DeBERTa tokenizer
tokenizer = DebertaTokenizer.from_pretrained("microsoft/deberta-large")

# Define the directory containing site text files
DATA_DIR = os.path.join(os.path.dirname(__file__), "sentiment_ready_texts")
OUTPUT_FILE = "processed_dataset.json"

# Patterns to remove unwanted system messages
REMOVE_PATTERNS = [
    r"you are using an out of date browser.*?",
    r"this sidebar will go away.*?",
    r"http\S+|www\S+",  # Remove URLs
    r"\s+"  # Normalize extra spaces
]

# Function to clean text
def clean_text(text):
    """Remove system messages, ads, and unwanted symbols from scraped discussions."""
    for pattern in REMOVE_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)  # Replace removed content with space
    text = re.sub(r"\s+", " ", text).strip()  # Ensure spaces are normalized
    return text

# Function to split text into structured sentences using SpaCy
def split_sentences(text):
    """Split discussions into individual sentences while preserving product context."""
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]  # Ensure sentences are properly segmented

# Function to process all site text files
def process_text_files():
    dataset = []
    
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.isfile(filepath) and filename.startswith("site_"):
            with open(filepath, "r", encoding="utf-8") as file:
                raw_text = file.read()

            # Step 1: Clean and normalize text
            cleaned_text = clean_text(raw_text)

            # Step 2: Split discussions into sentences
            sentences = split_sentences(cleaned_text)

            # Step 3: Tokenize each sentence for DeBERTa
            tokenized_texts = tokenizer(sentences, padding="longest", truncation=True, max_length=512)

            # Store processed data
            for i, sentence in enumerate(sentences):
                dataset.append({
                    "filename": filename,  # Track which site the sentence came from
                    "original_text": sentence,
                    "tokenized_input_ids": tokenized_texts["input_ids"][i],
                    "tokenized_attention_mask": tokenized_texts["attention_mask"][i]
                })

    return dataset

# Process all text files and save the structured dataset
dataset = process_text_files()

# Save as JSON for later use in training
with open("GoogleSearchCollection/" + OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4)

print(f"✅ Processed dataset saved to {OUTPUT_FILE} with {len(dataset)} entries.")
