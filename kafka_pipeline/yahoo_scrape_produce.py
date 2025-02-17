import json
import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import datetime

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

def produce_to_kafka(news_list):
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for news in news_list:
        producer.send("yahoo_news_raw", news)
        print("Produced to Kafka:", news)
    producer.flush()

if __name__ == "__main__":
    print("Starting to scrape Yahoo News...")
    news_data = scrape_yahoo_news()
    if news_data:
        produce_to_kafka(news_data)
        print("Scraping and producing completed.")
    else:
        print("No news data scraped.")
