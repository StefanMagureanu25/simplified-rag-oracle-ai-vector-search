import wikipedia
import os

# List of major countries and cities to scrape
PLACES = [
    "United States", "New York City", 
    "Japan", "Tokyo", 
    "France", "Paris", 
    "United Kingdom", "London", 
    "Egypt", "Cairo", 
    "Brazil", "Rio de Janeiro",
    "Australia", "Sydney",
    "Italy", "Rome"
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "data", "corpus.txt")

def create_corpus(output_path=DEFAULT_OUTPUT):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Generating {output_path} for {len(PLACES)} locations using Wikipedia...")
    
    # We use a set to avoid scraping the same place twice if someone modifies the list
    scraped_places = set()

    with open(output_path, "w", encoding="utf-8") as f:
        for place in PLACES:
            if place in scraped_places:
                continue
            
            try:
                print(f"Fetching data for: {place}...")
                # Fetch the Wikipedia page
                page = wikipedia.page(place, auto_suggest=False)
                
                # Write the title and content
                f.write(f"{page.title}\n")
                f.write(f"{'=' * len(page.title)}\n\n")
                
                # Write the content
                f.write(page.content)
                f.write("\n\n")  # Double newline helps our simple chunker separate paragraphs
                
                scraped_places.add(place)
            except wikipedia.exceptions.DisambiguationError as e:
                print(f"Disambiguation error for {place}. Options: {e.options[:5]}")
            except wikipedia.exceptions.PageError:
                print(f"Page not found for {place}")
            except Exception as e:
                print(f"Error fetching {place}: {e}")
                
    print(f"\nCorpus generation complete! Saved to {output_path}")

if __name__ == "__main__":
    # Ensure we run from the root of the project
    create_corpus()
