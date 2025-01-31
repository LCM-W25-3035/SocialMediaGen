import requests
from bs4 import BeautifulSoup
import json
import time
import os

def load_existing_data(filename="yahoo_news.json"):
    """
    Load existing data from a JSON file, if it exists.
    Returns a list of dictionaries, each with 'headline', 'link', (and optionally 'paragraph').
    """
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def deduplicate_data(data):
    """
    Remove duplicate entries from data, where each entry
    is a dict containing 'headline' and 'link'.
    Duplicates are identified by the tuple (headline, link).
    """
    seen = set()
    unique_data = []

    for item in data:
        key = (item['headline'], item['link'])
        if key not in seen:
            seen.add(key)
            unique_data.append(item)

    return unique_data

def scrape_yahoo_news():
    """
    Scrape Yahoo News homepage for headlines, links, and paragraph snippets.
    Returns a list of dictionaries with keys: 'headline', 'link', and 'paragraph'.
    """
    url = "https://news.yahoo.com/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Yahoo often has multiple modules or sections.
    # We initially find all <h3> elements for headlines.
    headline_elements = soup.find_all('h3')
    
    data = []
    for element in headline_elements:
        headline_text = element.get_text(strip=True)
        link_tag = element.find('a')
        link = link_tag['href'] if link_tag else None
        
        # Hypothetical paragraph snippet:
        #  - Some Yahoo layouts include a <p> or <div> with text near the headline.
        #  - In many sites, the paragraph might be in a sibling or parent container.
        #  - This example tries to find the next <p> after the headline, as an example.
        
        # Attempt 1: find a <p> within the same article block
        # (We look up the ancestor container, then find a paragraph inside it).
        paragraph_text = None

        # 1) Try to move up to a container that might hold headline + snippet
        parent_container = element.find_parent(['div', 'li', 'section'])
        if parent_container:
            # 2) Look for a <p> tag in that container
            p_tag = parent_container.find('p')
            if p_tag:
                paragraph_text = p_tag.get_text(strip=True)
        
        # If that doesn't work well, you could do something else:
        # e.g., element.find_next_sibling('p'), etc.
        #
        # paragraph_tag = element.find_next_sibling('p')
        # paragraph_text = paragraph_tag.get_text(strip=True) if paragraph_tag else None
        
        if headline_text and link:
            data.append({
                'headline': headline_text,
                'link': link,
                'paragraph': paragraph_text  # may be None if not found
            })
    
    return data

def save_to_json(data, filename="yahoo_news.json"):
    """
    Save the final list of data (after deduplication) to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Simple respectful scraping practice
    time.sleep(1)  # short delay before request
    
    # 1. Load existing data if any
    existing_data = load_existing_data("yahoo_news.json")

    # 2. Scrape new data
    new_data = scrape_yahoo_news()

    # 3. Combine old and new data
    combined_data = existing_data + new_data

    # 4. Deduplicate
    unique_data = deduplicate_data(combined_data)

    # 5. Save final deduplicated data to JSON
    save_to_json(unique_data, "yahoo_news.json")

    print(f"Scraping complete. {len(new_data)} new headlines scraped.")
    print(f"Database updated. Total unique items in JSON: {len(unique_data)}.")
