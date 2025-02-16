import spacy
import json
import re
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

# ------------------------------
# 1) Load SpaCy and the sentiment pipeline
# ------------------------------
nlp = spacy.load("en_core_web_sm")

sentiment_model = AutoModelForSequenceClassification.from_pretrained(
    "cardiffnlp/twitter-roberta-base-sentiment"
)
sentiment_tokenizer = AutoTokenizer.from_pretrained(
    "cardiffnlp/twitter-roberta-base-sentiment"
)
sentiment_pipeline = pipeline(
    "sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer
)

# ------------------------------
# 2) Domain synonyms / aspects dictionary
#    (Same as provided; can be extended as you like)
# ------------------------------
TECH_ASPECTS = {
    # Display & Screen
    "display": [
        "screen", "display", "brightness", "contrast", "resolution", "refresh rate",
        "color accuracy", "HDR", "glare", "touchscreen", "OLED", "LCD", "Mini LED",
        "viewing angles", "screen size", "pixel density", "aspect ratio", "curved display",
        "ambient light sensor", "anti-reflective", "matte finish", "edge-to-edge", "in-cell touch",
        "dual display", "3D display"
    ],
    # Performance
    "performance": [
        "speed", "lag", "efficiency", "responsiveness", "multitasking", "processing power",
        "CPU", "GPU", "RAM", "thermal performance", "overheating", "frame rate",
        "rendering speed", "benchmark scores", "clock speed", "turbo boost", "core count",
        "hyper-threading", "instruction throughput", "latency", "parallel processing"
    ],
    # Battery & Power Management
    "battery": [
        "battery life", "charge time", "power consumption", "fast charging",
        "wireless charging", "battery drain", "energy efficiency", "wattage", "power adapter",
        "battery capacity", "battery degradation", "battery cycle count", "removable battery",
        "charging efficiency", "battery backup", "endurance", "battery health"
    ],
    # Storage & SSD
    "storage": [
        "SSD", "HDD", "storage capacity", "read speed", "write speed", "load times",
        "expandable storage", "NVMe", "PCIe", "external storage", "SD card",
        "flash memory", "eMMC", "UFS", "HFS+", "file system performance"
    ],
    # Connectivity & Ports
    "ports": [
        "USB", "USB-C", "Thunderbolt", "HDMI", "Ethernet", "SD card reader", "audio jack",
        "Wi-Fi", "Bluetooth", "5G", "LTE", "NFC", "Wi-Fi 6", "Wi-Fi 7", "network connectivity",
        "dongle", "VGA", "DisplayPort", "DVI", "microSD slot", "FireWire", "MHL", "Mini DisplayPort"
    ],
    # Keyboard
    "keyboard": [
        "key travel", "key feel", "backlit keyboard", "mechanical switches", "RGB lighting",
        "typing experience", "keyboard layout", "macro keys", "numpad", "scissor switches",
        "chiclet keys", "water-resistant keyboard", "ergonomic design", "key rollover", "anti-ghosting"
    ],
    # Trackpad & Mouse Input
    "trackpad": [
        "touchpad", "trackpad sensitivity", "multi-touch gestures", "palm rejection",
        "haptic feedback", "scrolling experience", "precision tracking", "force touch", "gesture recognition"
    ],
    "mouse": [
        "mouse DPI", "tracking accuracy", "ergonomics", "click latency", "wireless mouse",
        "mechanical buttons", "RGB customization", "programmable buttons", "optical sensor",
        "laser sensor", "battery life", "wireless range"
    ],
    # Audio & Sound System
    "audio": [
        "speaker", "sound quality", "volume", "bass", "treble", "microphone",
        "noise cancellation", "Dolby Atmos", "spatial audio", "headphone jack",
        "bluetooth audio latency", "wireless earbuds support", "audio codec", "sound clarity",
        "frequency response", "balanced audio", "amplifier", "subwoofer"
    ],
    # Design & Build Quality
    "design": [
        "build quality", "materials", "aesthetics", "weight", "thickness",
        "durability", "hinge strength", "bezel", "chassis", "color options",
        "portability", "carbon fiber", "aluminum body", "plastic chassis", "sleek design",
        "ergonomic design", "form factor", "curved design", "industrial design", "finish",
        "texture", "back cover design"
    ],
    # Software & User Experience
    "software": [
        "operating system", "pre-installed apps", "UI", "UX", "bloatware",
        "customization", "dark mode", "gesture controls", "voice assistant",
        "AI features", "Windows 11", "macOS", "Linux", "software updates", "firmware",
        "OS stability", "driver support", "security patches", "app ecosystem",
        "multitasking support", "interface design"
    ],
    # Cooling & Thermal Management
    "cooling": [
        "overheating", "fan noise", "heat dissipation", "thermal throttling",
        "liquid cooling", "airflow", "heat pipes", "cooling pad", "vapor chamber",
        "active cooling", "passive cooling", "temperature control", "thermal design power"
    ],
    # Camera & Imaging
    "camera": [
        "webcam", "camera resolution", "low-light performance", "autofocus",
        "video quality", "megapixels", "Face ID", "portrait mode", "ultrawide",
        "zoom", "optical image stabilization", "night mode", "depth sensor", "macro capability",
        "color reproduction", "HDR video", "sensor size", "aperture", "white balance"
    ],
    # Security & Privacy
    "security": [
        "fingerprint scanner", "Windows Hello", "privacy shutter",
        "TPM chip", "encryption", "secure boot", "face recognition", "iris scanner",
        "biometric security", "two-factor authentication", "password protection", "data encryption"
    ],
    # Gaming & Graphics
    "gaming": [
        "ray tracing", "FPS", "VR gaming", "G-Sync", "FreeSync", "input lag",
        "graphics card", "RGB lighting", "game compatibility", "frame rate consistency",
        "latency", "anti-aliasing", "shader performance", "gaming benchmarks"
    ],
    # Accessories & Expansion
    "accessories": [
        "stylus", "pen support", "dock", "external GPU", "external monitor",
        "VR headset", "gaming controller", "webcam cover", "wireless charger", "case",
        "screen protector", "portable charger", "headphone stand", "adapter", "cable management",
        "portable docking station"
    ],
    # Mobile-Specific Features
    "mobile": [
        "dual SIM", "eSIM", "fast charging", "camera bump", "screen notch",
        "water resistance", "5G connectivity", "foldable display", "biometric sensors",
        "accelerometer", "gyroscope", "compass", "proximity sensor", "GPS", "magnetic sensor"
    ],
    # AI or Smart Features
    "AI_features": [
        "machine learning", "AI upscaling", "chatbot", "predictive text",
        "smart home integration", "automation", "voice recognition", "natural language processing",
        "personal assistant", "recommendation system", "adaptive learning", "context-aware computing"
    ],
    # Cloud & Subscription Services
    "cloud_services": [
        "cloud storage", "OneDrive", "Google Drive", "iCloud", "Dropbox",
        "streaming services", "gaming cloud", "remote desktop", "cloud backup", "SaaS", "PaaS", "IaaS"
    ],
    # Reliability & Longevity
    "reliability": [
        "long-term performance", "warranty", "customer support",
        "firmware updates", "repairability", "modularity", "build durability",
        "consistency", "stability", "upgradability", "error rate", "mean time between failures"
    ],
}

PRICING_TERMS = ["expensive", "price", "cost", "worth", "value for money",
                 "too costly", "cheap", "budget", "overpriced"]

EXTRA_BATTERY_TERMS = ["lasted", "longer battery", "energy efficient"]

NEGATIVE_WORDS = [
    "don't like", "hate", "not good", "bad", "overpriced", "too expensive",
    "disappointed", "worse", "issue", "problem"
]

COMPARATIVE_NEGATIVE = ["slower than", "worse than", "not as good", "less powerful", "weaker performance"]

BRAND_TERMS = [
    "iphone", "apple", "samsung", "galaxy", "pixel", "macbook", 
    "ipad", "oneplus", "sony", "xiaomi", "nvidia", "intel", "amd"
]

# ------------------------------------------------
# 3) Aspect Extraction
# ------------------------------------------------
def extract_aspects(sentence):
    aspects_found = set()
    lower_sentence = sentence.lower()
    doc = nlp(sentence)

    # (A) Check for domain-based aspect keywords in noun chunks
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        for aspect_category, keywords in TECH_ASPECTS.items():
            if any(keyword in chunk_text for keyword in keywords):
                aspects_found.add(aspect_category)

    # (B) Battery references
    battery_terms = ["battery life", "charge time", "power consumption", "energy efficiency"] + EXTRA_BATTERY_TERMS
    if any(term in lower_sentence for term in battery_terms):
        aspects_found.add("battery")

    # (C) Pricing references
    if any(p in lower_sentence for p in PRICING_TERMS):
        aspects_found.add("pricing")

    # (D) (Optional) numeric references via NER
    for ent in doc.ents:
        if ent.label_ in ["CARDINAL", "QUANTITY", "MONEY"]:
            if re.match(r"(16GB|32GB|64GB|128GB|256GB|512GB|1TB|2TB|4K|8K|fps|GHz|nm|hours|minutes)",
                        ent.text, re.IGNORECASE):
                pass  # Expand logic if needed

    return list(aspects_found)


# ------------------------------------------------
# 4) Sentiment Computation
# ------------------------------------------------
def get_sentiment(sentence, aspects):
    sentiment_output = sentiment_pipeline(sentence)[0]
    sentiment_label = sentiment_output["label"]  # e.g. 'LABEL_0', 'LABEL_1', 'LABEL_2'

    # Map label to numeric sentiment
    label_to_val = {"LABEL_0": -1.0, "LABEL_1": 0.0, "LABEL_2": 1.0}
    base_sentiment = label_to_val.get(sentiment_label, 0.0)

    lowered = sentence.lower()
    for nw in NEGATIVE_WORDS:
        if nw in lowered:
            base_sentiment -= 0.3
    for cmp_neg in COMPARATIVE_NEGATIVE:
        if cmp_neg in lowered:
            base_sentiment -= 0.3

    # If no aspects, store as 'general'
    if not aspects:
        return {"general": base_sentiment}

    # Otherwise, per-aspect sentiment
    aspect_scores = {}
    for a in aspects:
        aspect_scores[a] = base_sentiment
    return aspect_scores

# ------------------------------------------------
# 5) Meaningful Sentence Check
# ------------------------------------------------
def is_meaningful(sentence, aspects, sentiment_scores):
    """
    Heuristic logic to decide if this sentence provides actual value:
      1) If there's at least 1 aspect => keep it
      2) Else, if it mentions a brand and has moderate absolute sentiment >= 0.5 => keep
      3) Else, if length >= 8 tokens and strong absolute sentiment >= 1.0 => keep
      4) Otherwise => discard
    """
    # 1) If any aspects found
    if aspects:
        return True

    # We'll look for "general" sentiment if no aspects
    general_sentiment = sentiment_scores.get("general", 0.0)
    lowered = sentence.lower()

    # 2) brand mention + moderate sentiment
    if any(b in lowered for b in BRAND_TERMS) and abs(general_sentiment) >= 0.5:
        return True

    # 3) If enough tokens + strong sentiment
    doc = nlp(sentence)
    if len(doc) >= 8 and abs(general_sentiment) >= 1.0:
        return True

    # 4) Otherwise discard
    return False


# ------------------------------------------------
# 6) Main Processing: read input, run extraction & sentiment,
#    but keep only meaningful lines
# ------------------------------------------------
def process_reviews(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    filtered_results = []
    for entry in dataset:
        # Adjust reading logic as needed. E.g., "original_text" or "sentence"
        sentence = entry.get("original_text", "").strip()

        # 1) Extract aspects
        aspects = extract_aspects(sentence)

        # 2) Get sentiment
        sentiment_scores = get_sentiment(sentence, aspects)

        # 3) Decide if it's meaningful
        if is_meaningful(sentence, aspects, sentiment_scores):
            filtered_results.append({
                "sentence": sentence,
                "aspects": aspects,
                "sentiment_scores": sentiment_scores
            })

    # Write out only the meaningful sentences
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_results, f, indent=4)

    print(f"Refined ABSA completed! Output => {output_file}, with {len(filtered_results)} kept.")


# ------------------------------------------------
# 7) If you want to run directly
# ------------------------------------------------
if __name__ == "__main__":
    input_file = "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/processed_dataset.json"
    output_file = "/Users/yarik/Documents/GitHub/bsc-final/AI_Module/analyzed_sentiments.json"
    process_reviews(input_file, output_file)
