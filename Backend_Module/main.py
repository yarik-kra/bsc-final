from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os

class ProductRequest(BaseModel):
    product: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANALYZED_SENTIMENTS_FILE = "/Users/yarik/Documents/GitHub/bsc-final/AI_Module/analyzed_sentiments.json"
LAST_ANALYZED_PRODUCT = {"name": "Unknown Product"}  # Global variable to store the last analyzed product

@app.post("/api/analyze")
async def analyze_product(data: ProductRequest):
    product_name = data.product.strip()
    print(f"Received product from frontend: {product_name}")

    # Store the last analyzed product name
    LAST_ANALYZED_PRODUCT["name"] = product_name

    try:
        # Run RunAll.py with the product name
        result = subprocess.run(
            ["python3", "/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/RunAll.py", product_name], 
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()

        # Send response back to frontend
        return {"result": output, "product_name": product_name}

    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to execute RunAll.py: {e}"}

@app.get("/api/results")
async def get_results():
    """Fetch the processed sentiment results from analyzed_sentiments.json"""
    if os.path.exists(ANALYZED_SENTIMENTS_FILE):
        with open(ANALYZED_SENTIMENTS_FILE, "r") as f:
            data = json.load(f)

        if not data or not isinstance(data, list):
            return {"error": "Invalid data format in JSON"}

        # Retrieve the last stored product name
        product_name = LAST_ANALYZED_PRODUCT["name"]

        # Process sentiment counts
        total_reviews = len(data)
        positive_count = sum(1 for review in data if any(score > 0 for score in review["sentiment_scores"].values()))
        negative_count = sum(1 for review in data if any(score < 0 for score in review["sentiment_scores"].values()))
        neutral_count = total_reviews - (positive_count + negative_count)

        positive_percentage = round((positive_count / total_reviews) * 100, 2) if total_reviews > 0 else 0
        negative_percentage = round((negative_count / total_reviews) * 100, 2) if total_reviews > 0 else 0
        neutral_percentage = round((neutral_count / total_reviews) * 100, 2) if total_reviews > 0 else 0

        # Extract praised features
        feature_sentiments = {}
        for review in data:
            for feature, score in review["sentiment_scores"].items():
                if feature not in feature_sentiments:
                    feature_sentiments[feature] = []
                feature_sentiments[feature].append(score)

        praised_features = sorted(
            [(feature, sum(scores) / len(scores)) for feature, scores in feature_sentiments.items()],
            key=lambda x: x[1], reverse=True
        )

        return {
            "product_name": product_name,  # Now correctly returning the stored product name
            "positive_percentage": positive_percentage,
            "negative_percentage": negative_percentage,
            "neutral_percentage": neutral_percentage,
            "praised_features": [feature for feature, score in praised_features if score > 0]
        }

    return {"error": "No analyzed sentiment data found."}
