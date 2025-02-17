import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from pymongo import MongoClient

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

import requests
from bs4 import BeautifulSoup
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_yahoo_news():
    """
    Scrape the Yahoo News homepage for headlines, links, and paragraph snippets.
    Returns a list of dictionaries with keys: 'headline', 'link', 'paragraph', and 'time_scraped'.
    """
    url = "https://news.yahoo.com/"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve page: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all <h3> elements which are assumed to contain headlines.
    headline_elements = soup.find_all('h3')
    if not headline_elements:
        print("No headlines found. The page structure may have changed.")
        return []
    
    data = []
    base_url = "https://news.yahoo.com"
    for element in headline_elements:
        # Extract the headline text.
        headline_text = element.get_text(strip=True)
        
        # Find the parent anchor tag to retrieve the link.
        link_tag = element.find('a')
        link = link_tag.get('href') if link_tag else None
        
        # If the link is relative, prepend the base URL.
        if link and link.startswith('/'):
            link = base_url + link
        
        # Attempt to find a paragraph snippet in the same container or nearby.
        paragraph_text = None
        parent_container = element.find_parent(['div', 'li', 'section'])
        if parent_container:
            p_tag = parent_container.find('p')
            if p_tag:
                paragraph_text = p_tag.get_text(strip=True)
        
        # Only add the item if both headline and link are available.
        if headline_text and link:
            item = {
                'headline': headline_text,
                'link': link,
                'paragraph': paragraph_text,  # may be None if not found
                'time_scraped': datetime.now().isoformat()
            }
            data.append(item)
    
    return data





def save_to_mongodb(data, mongodb_uri="mongodb+srv://funniket:Annu96545%40@cluster0.m20bs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", db_name="news_db", collection_name="yahoo_news"):
    """
    Save the scraped data directly to a MongoDB collection.
    """
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    if data:
        # Insert the list of documents into the MongoDB collection.
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} documents into MongoDB.")
    else:
        print("No data to insert.")
    
    client.close()

if __name__ == "__main__":
    # Respectful scraping practice: short delay before making the request.
    time.sleep(1)
    
    # 1. Scrape new data from Yahoo News.
    new_data = scrape_yahoo_news()
    
    # 2. Save the scraped data directly to MongoDB.
    save_to_mongodb(new_data)
    
    print(f"Scraping complete. {len(new_data)} new headlines scraped and saved to MongoDB.")
