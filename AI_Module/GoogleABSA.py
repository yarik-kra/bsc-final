import spacy
import json
import re
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

# Load SpaCy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

# Load pre-trained sentiment analysis model
sentiment_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
sentiment_tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer)

# Define common tech product aspects
TECH_ASPECTS = {
    # Display & Screen Features
    "display": ["screen", "display", "brightness", "contrast", "resolution", "refresh rate", 
                "color accuracy", "HDR", "glare", "touchscreen", "OLED", "LCD", "Mini LED", "viewing angles"],

    # Performance
    "performance": ["speed", "lag", "efficiency", "responsiveness", "multitasking", 
                    "processing power", "CPU", "GPU", "RAM", "thermal performance", "overheating", 
                    "frame rate", "rendering speed", "benchmark scores"],

    # Battery & Power Management
    "battery": ["battery life", "charge time", "power consumption", "fast charging", 
                "wireless charging", "battery drain", "energy efficiency", "wattage", "power adapter"],

    # Storage & SSD
    "storage": ["SSD", "HDD", "storage capacity", "read speed", "write speed", "load times",
                "expandable storage", "NVMe", "PCIe", "external storage", "SD card"],

    # Connectivity & Ports
    "ports": ["USB", "USB-C", "Thunderbolt", "HDMI", "Ethernet", "SD card reader", 
              "audio jack", "Wi-Fi", "Bluetooth", "5G", "LTE", "NFC", "Wi-Fi 6", "Wi-Fi 7",
              "network connectivity", "dongle dependency"],

    # Keyboard & Typing Experience
    "keyboard": ["key travel", "key feel", "backlit keyboard", "mechanical switches",
                 "RGB lighting", "typing experience", "keyboard layout", "macro keys"],

    # Trackpad & Mouse Input
    "trackpad": ["touchpad", "trackpad sensitivity", "multi-touch gestures", 
                 "palm rejection", "haptic feedback", "scrolling experience"],
    "mouse": ["mouse DPI", "tracking accuracy", "ergonomics", "click latency", "wireless mouse", 
              "mechanical buttons", "RGB customization"],

    # Audio & Sound System
    "audio": ["speaker", "sound quality", "volume", "bass", "treble", "microphone", 
              "noise cancellation", "Dolby Atmos", "spatial audio", "headphone jack", 
              "bluetooth audio latency", "wireless earbuds support"],

    # Build Quality & Design
    "design": ["build quality", "materials", "aesthetics", "weight", "thickness", 
               "durability", "hinge strength", "bezel size", "chassis", "color options", 
               "portability", "carbon fiber", "aluminum body", "plastic chassis"],

    # Software & User Experience
    "software": ["operating system", "pre-installed apps", "UI/UX", "bloatware", 
                 "customization", "dark mode", "gesture controls", "voice assistant", "AI features",
                 "Windows 11", "macOS", "Linux compatibility"],

    # Cooling & Thermal Management
    "cooling": ["overheating", "fan noise", "heat dissipation", "thermal throttling", 
                "liquid cooling", "airflow", "heat pipes", "cooling pad support"],

    # Camera & Webcam
    "camera": ["webcam", "camera resolution", "low-light performance", "autofocus", 
               "video quality", "megapixels", "AI enhancements", "Face ID", "portrait mode", "ultrawide"],

    # Security & Privacy
    "security": ["fingerprint scanner", "Face ID", "Windows Hello", "privacy shutter", 
                 "TPM chip", "encryption", "password manager", "secure boot"],

    # Gaming & Graphics
    "gaming": ["ray tracing", "FPS", "VR gaming", "G-Sync", "FreeSync", "input lag",
               "refresh rate", "graphics card", "RGB lighting", "game compatibility"],

    # Accessories & Expansion
    "accessories": ["stylus", "pen support", "dock", "external GPU", "external monitor",
                    "VR headset", "gaming controller", "webcam cover", "wireless charger"],

    # Mobile-Specific Features
    "mobile": ["dual SIM", "eSIM", "fast charging", "camera bump", "screen notch", 
               "water resistance", "5G connectivity", "foldable display"],

    # Smart Features
    "AI_features": ["smart assistant", "machine learning", "AI upscaling", "chatbot", 
                    "predictive text", "smart home integration", "automation"],

    # Cloud & Subscription Services
    "cloud_services": ["cloud storage", "OneDrive", "Google Drive", "iCloud", "Dropbox", 
                       "streaming services", "gaming cloud", "remote desktop"],

    # Reliability & Longevity
    "reliability": ["durability", "long-term performance", "warranty", "customer support", 
                    "firmware updates", "repairability", "modularity"]
}

# Exclude random numbers unless related to tech specs
def extract_aspects(sentence):
    aspects = set()
    doc = nlp(sentence)
    
    # Named Entity Recognition (NER)
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "ORG", "GPE", "MONEY", "CARDINAL", "QUANTITY"]:
            if re.match(r"\b(16GB|32GB|64GB|128GB|256GB|512GB|1TB|2TB|4K|8K|fps|GHz|nm|hours|minutes)\b", ent.text, re.IGNORECASE):
                aspects.add(ent.text.lower())
    
    # Detect battery-related phrases
    battery_terms = ["battery life", "charge time", "lasted", "longer battery", "power consumption", "energy efficient"]
    if any(term in sentence.lower() for term in battery_terms):
        aspects.add("battery")
    
    # Extract noun chunks for tech-related terms
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        for category, keywords in TECH_ASPECTS.items():
            if any(keyword in chunk_text for keyword in keywords):
                aspects.add(category)
    
    # Handle Pricing & Value-related mentions
    pricing_terms = ["expensive", "price", "cost", "worth", "value for money", "too costly", "cheap", "budget"]
    if any(term in sentence.lower() for term in pricing_terms):
        aspects.add("pricing")
    
    return list(aspects)  # Remove duplicates

# Negative word detection
NEGATIVE_WORDS = ["don't like", "hate", "not good", "bad", "overpriced", "too expensive", "disappointed", "worse", "issue", "problem"]
COMPARATIVE_NEGATIVE = ["slower than", "worse than", "not as good", "less powerful", "weaker performance"]

def get_sentiment(sentence, aspects):
    sentiment_output = sentiment_pipeline(sentence)[0]
    sentiment_score = sentiment_output["score"]
    sentiment_label = sentiment_output["label"]
    
    sentiment_map = {"LABEL_0": -1, "LABEL_1": 0, "LABEL_2": 1}
    base_sentiment = sentiment_map.get(sentiment_label, 0)
    
    # Adjust sentiment if negative words are detected
    for neg_word in NEGATIVE_WORDS:
        if neg_word in sentence.lower():
            base_sentiment -= 0.5  # Shift towards negative
    
    # Adjust sentiment for comparative phrases
    for neg_comp in COMPARATIVE_NEGATIVE:
        if neg_comp in sentence.lower():
            base_sentiment -= 0.5
    
    # Assign sentiment to aspects
    aspect_sentiments = {aspect: base_sentiment for aspect in aspects} if aspects else {"general": base_sentiment}
    return aspect_sentiments

# Process the dataset and analyze sentiments per aspect
def process_reviews(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        dataset = json.load(file)
    
    results = []
    for entry in dataset:
        sentence = entry.get("original_text", "").strip()
        aspects = extract_aspects(sentence)

        # Ensure pricing-related aspects are included if applicable
        if not aspects and any(term in sentence.lower() for term in ["price", "cost", "expensive", "cheap"]):
            aspects.append("pricing")
        
        # Get sentiment per aspect
        sentiment_scores = get_sentiment(sentence, aspects)
        
        results.append({
            "sentence": sentence,
            "aspects": aspects,
            "sentiment_scores": sentiment_scores
        })
    
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

# Run the script
input_file = "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/processed_dataset.json"
output_file = "/Users/yarik/Documents/GitHub/bsc-final/AI_Module/analyzed_sentiments.json"
process_reviews(input_file, output_file)

print("Sentiment analysis with improved ABSA completed!")
