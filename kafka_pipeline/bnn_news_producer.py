import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import json
from urllib.parse import urljoin

# Kafka Config
KAFKA_TOPIC = "news_topic"
KAFKA_SERVER = "localhost:9092"

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Scraping function
def scrape_news():
    url = 'https://www.bnnbloomberg.ca'
    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.text, 'html.parser')

    headlines = soup.find_all('h2', class_='c-heading')
    seen_links = set()
    articles = []

    for headline in headlines:
        link_tag = headline.find('a', class_='c-link')

        if link_tag:
            title = link_tag.text.strip()
            article_link = urljoin(url, link_tag['href'])

            if article_link in seen_links:
                continue
            seen_links.add(article_link)

            # Fetch article details
            try:
                article_response = requests.get(article_link, timeout=5)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                summary_tag = article_soup.find('meta', {'name': 'description'})
                summary = summary_tag['content'] if summary_tag else 'null'

                timestamp_tag = article_soup.find('time')
                timestamp = timestamp_tag.get('datetime', 'null') if timestamp_tag else 'null'

                # Store article data
                article_data = {
                    "title": title,
                    "link": article_link,
                    "summary": summary,
                    "timestamp": timestamp
                }

                articles.append(article_data)

                # Send data to Kafka
                producer.send(KAFKA_TOPIC, article_data)
                print(f"Sent to Kafka: {article_data}")

            except requests.RequestException as e:
                print(f"Error fetching {article_link}: {e}")

    producer.flush()

# Run scraper
scrape_news()
