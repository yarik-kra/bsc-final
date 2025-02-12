import os
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Input and output folders
INPUT_FOLDER = "GoogleSearchCollection/" + "sentiment_ready_texts"
OUTPUT_FOLDER = "GoogleSearchCollection/" + "nlp_processed_texts"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to preprocess text for NLP models
def preprocess_text(text):
    doc = nlp(text)
    processed_sentences = []

    for sent in doc.sents:
        words = []
        for token in sent:
            if not token.is_stop and not token.is_punct and token.pos_ in ["ADJ", "VERB", "NOUN"]:
                words.append(token.lemma_)  # Convert to base form

        if words:
            processed_sentences.append(" ".join(words))

    return "\n".join(processed_sentences)

# Process each file
for filename in os.listdir(INPUT_FOLDER):
    input_filepath = os.path.join(INPUT_FOLDER, filename)
    output_filepath = os.path.join(OUTPUT_FOLDER, filename)

    with open(input_filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    processed_text = preprocess_text(raw_text)

    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(processed_text)

    print(f"Processed: {output_filepath}")
