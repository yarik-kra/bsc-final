import os
import re
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Input and output folders
INPUT_FOLDER = "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/" + "scraped_texts"
OUTPUT_FOLDER = "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/" + "sentiment_ready_texts"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Regex patterns to remove irrelevant text
UNWANTED_PATTERNS = [
    r"https?://\S+",  # Remove URLs
    r"\b(\d{1,2} [A-Za-z]+ \d{4})\b",  # Remove dates
    r"\b(Posted on|Updated on|Published on)\b.*",  # Remove timestamps
    r"\b(Page|Article|Share|Link|Email|Facebook|Twitter|Reddit)\b.*",  # Remove social media tags
    r"\b(Reporter|Editor|Contributor|Author|Review|News|Shopping|Journalist)\b.*",  # Remove author details
    r"\b(\d+GB|\d+MHz|\d+fps|\d+W|\d+TB|\d+Hz)\b",  # Remove technical specs
    r"\b(\$\d+|£\d+|€\d+)\b",  # Remove prices
]

# Function to filter relevant sentences for sentiment analysis
def extract_relevant_sentences(text):
    sentences = []
    doc = nlp(text)

    for sent in doc.sents:
        sentence = sent.text.strip()
        
        # Remove unwanted patterns
        if any(re.search(pattern, sentence, re.IGNORECASE) for pattern in UNWANTED_PATTERNS):
            continue
        
        # Check for sentiment-related words (adjectives & verbs)
        sentiment_words = [token for token in sent if token.pos_ in ["ADJ", "VERB"]]
        
        if sentiment_words:
            cleaned_sentence = re.sub(r"[^a-zA-Z0-9.,!?'\s]", "", sentence)  # Remove special characters
            cleaned_sentence = cleaned_sentence.lower().strip()  # Lowercase
            sentences.append(cleaned_sentence)

    return "\n".join(sentences)

# Process each file
for filename in os.listdir(INPUT_FOLDER):
    input_filepath = os.path.join(INPUT_FOLDER, filename)
    output_filepath = os.path.join(OUTPUT_FOLDER, filename)

    with open(input_filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    processed_text = extract_relevant_sentences(raw_text)

    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(processed_text)

    print(f"Processed: {output_filepath}")