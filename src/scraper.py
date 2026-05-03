import os
import time
import requests
from bs4 import BeautifulSoup

PLACES = [
    "France", "Paris", "Lyon",
    "Germany", "Berlin", "Munich",
    "Italy", "Rome", "Milan",
    "Spain", "Madrid", "Barcelona",
    "United Kingdom", "London", "Edinburgh",
    "Netherlands", "Amsterdam",
    "Austria", "Vienna",
    "Switzerland", "Zurich",
    "Greece", "Athens"
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "data", "corpus.txt")

def fetch_wikipedia_page(title):
    
    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    headers = {"User-Agent": "GlobalExplorerRAGBot/1.0 (https://example.org; someone@example.org)"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find(id='mw-content-text')
    
    if not content_div:
        return None
        
    paragraphs = content_div.find_all('p')
    
    # Extract all paragraphs, giving us extreme depth for the RAG
    text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
    return text

def create_corpus(output_path=DEFAULT_OUTPUT):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Generating European corpus to {output_path}...")
    
    scraped_places = set()

    with open(output_path, "w", encoding="utf-8") as f:
        for place in PLACES:
            if place in scraped_places:
                continue
            
            try:
                print(f"Fetching in-depth data for: {place}...")
                content = fetch_wikipedia_page(place)
                
                if content:
                    f.write(f"{place}\n")
                    f.write(f"{'=' * len(place)}\n\n")
                    f.write(content)
                    f.write("\n\n")
                    scraped_places.add(place)
                else:
                    print(f"Page not found for {place}")
                    
            except Exception as e:
                print(f"Error fetching {place}: {e}")
            
            time.sleep(1)
                
    print(f"\nCorpus generation complete! Saved to {output_path}")

if __name__ == "__main__":
    create_corpus()
