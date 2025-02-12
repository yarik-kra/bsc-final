import requests
from bs4 import BeautifulSoup
import time
import os

# file containing discussion links
INPUT_FILE = "Data_Collection_Module/GoogleSearchCollection/" + "google_discussion_links.txt"
OUTPUT_FOLDER = "Data_Collection_Module/GoogleSearchCollection/" + "scraped_texts"

# create output directory if it doesnt exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# extracts and cleans text from a webpage
def extract_text_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url} - Status Code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # remove unnecessary elements
        for script in soup(["script", "style", "noscript", "meta", "iframe", "footer", "header", "nav", "aside"]):
            script.extract()

        raw_text = soup.get_text(separator="\n", strip=True)

        # remove short lines (menu items, buttons, metadata)
        lines = [line.strip() for line in raw_text.split("\n") if len(line) > 50]

        # remove duplicate lines while maintaining order
        seen = set()
        unique_lines = [line for line in lines if not (line in seen or seen.add(line))]

        return "\n".join(unique_lines)

    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

# reads urls and scrapes them
def scrape_links_from_file(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        urls = file.read().splitlines()

    for index, url in enumerate(urls):
        print(f"Scraping ({index+1}/{len(urls)}): {url}")
        extracted_text = extract_text_from_url(url)

        if extracted_text:
            output_filename = f"{OUTPUT_FOLDER}/site_{index+1}.txt"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(extracted_text)

            print(f"Saved cleaned text to {output_filename}")

        time.sleep(2)  # prevent rate limiting

scrape_links_from_file(INPUT_FILE)
