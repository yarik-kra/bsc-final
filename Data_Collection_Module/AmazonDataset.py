import json
import pandas as pd
from datasets import load_dataset

def load_metadata_subset(dataset_name, subset, categories, limit=50):
    # load a small subset of metadata from hugging face dataset and filter products based on categories
    dataset = load_dataset(dataset_name, subset, split="train", trust_remote_code=True)
    tech_products = {}
    
    for i, data in enumerate(dataset):
        if data.get("main_category") in categories:
            tech_products[data["parent_asin"]] = {
                "title": data.get("title", "Unknown"),
                "category": data.get("main_category"),
                "price": data.get("price", "N/A"),
            }
        
        if len(tech_products) >= limit:
            break
    
    return tech_products

def print_available_products_subset(dataset_name, subset, categories, limit=50):
    # load metadata subset and print available product names
    tech_products = load_metadata_subset(dataset_name, subset, categories, limit)
    print("\nAvailable Products:")
    for i, (asin, product) in enumerate(tech_products.items()):
        print(f"{i+1}. {product['title']} ({asin})")

def main():
    # define relevant tech categories
    tech_categories = ["Electronics", "Computers & Accessories", "Smartphones & Tablets", "Audio Devices", "PC Components", "Gaming"]
    
    # hugging Face dataset details
    dataset_name = "McAuley-Lab/Amazon-Reviews-2023"
    subset = "raw_meta_Electronics"  # load small subset of Electronics metadata
    
    # load metadata subset and print available products
    print("Loading small metadata subset from Hugging Face dataset...")
    print_available_products_subset(dataset_name, subset, tech_categories)
    
if __name__ == "__main__":
    main()
