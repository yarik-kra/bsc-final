import sys
import requests
import time

# API key
API_KEY = "AIzaSyD3rGswjIk33bQKe-kNy8YnsG24HwDt028"

# engine ID
CX_ID = "d3a3d03040c604d84"

# sites to search
ALLOWED_SITES = [
    "techradar.com", "tomshardware.com", "macrumors.com",
    "forums.overclockers.co.uk", "www.engadget.com",
    "www.tomsguide.com", "www.overclockers.co.uk", "www.rtings.com"
]

def fetch_google_discussion_links(product, max_pages=2):
    print(f"Searching Google for '{product}' discussions and reviews...")

    base_url = "https://www.googleapis.com/customsearch/v1"
    all_links = []
    site_query = " OR ".join([f"site:{site}" for site in ALLOWED_SITES])

    for page in range(1, max_pages + 1):
        start_index = (page - 1) * 10 + 1  

        params = {
            "q": f"{product} review OR discussion OR forum ({site_query})",
            "key": API_KEY,
            "cx": CX_ID,
            "start": start_index,
            "num": 10,
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            data = response.json()

            if "items" not in data:
                print(f"Page {page}: No results found.")
                break

            page_links = [item["link"] for item in data["items"]]
            all_links.extend(page_links)

            print(f"Page {page}: Found {len(page_links)} links.")

            time.sleep(2)  # prevent rate limiting

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

    with open("/Users/yarik/Documents/GitHub/bsc-final/Data_Collection_Module/GoogleSearchCollection/google_discussion_links.txt", "w", encoding="utf-8") as f:
        for link in all_links:
            f.write(link + "\n")

    print("Saved all links to 'google_discussion_links.txt'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No product name provided.")
        sys.exit(1)
    
    product_name = sys.argv[1]
    fetch_google_discussion_links(product_name, max_pages=2)
