import yaml
from kafka import KafkaProducer
import requests
from bs4 import BeautifulSoup
import json

# Load YAML config
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Kafka Producer setup using loaded config
producer = KafkaProducer(
    bootstrap_servers=config['kafka']['bootstrap_servers'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# URL of the website you want to scrape
url = 'https://www.bnnbloomberg.ca'

# Send a GET request to fetch the content of the page
response = requests.get(url)

# Parse the content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all headlines on the page using the 'c-heading' class
headlines = soup.find_all('h2', class_='c-heading')

# Set to keep track of unique article links to avoid duplicates
seen_links = set()

# Loop through each headline and extract title, summary, timestamp, and link
for headline in headlines:
    # Find the <a> tag inside each <h2> and ensure it's not None
    link_tag = headline.find('a', class_='c-link')

    # Initialize variables for headline, link, summary, and timestamp
    title = 'null'
    article_link = 'null'
    summary = 'null'
    timestamp = 'null'

    if link_tag:  # If the <a> tag exists
        title = link_tag.text.strip()  # Get the text of the link
        article_link = link_tag['href']  # Get the href attribute (relative link)
        
        # Check if the article link is already seen to avoid duplicates
        if article_link in seen_links:
            continue
        seen_links.add(article_link)

        # Fetch the article page to get the summary, timestamp, and source
        full_article_link = url + article_link
        article_response = requests.get(full_article_link)
        article_soup = BeautifulSoup(article_response.text, 'html.parser')

        # Extract the summary (if available), else set to 'null'
        summary_tag = article_soup.find('meta', {'name': 'description'})
        summary = summary_tag['content'] if summary_tag else 'null'

        # Extract timestamp (if available), else set to 'null'
        timestamp_tag = article_soup.find('time')
        timestamp = timestamp_tag['datetime'] if timestamp_tag else 'null'

    # Create the article object
    article = {
        "title": title,
        "link": article_link,
        "summary": summary,
        "timestamp": timestamp
    }

    # Send the data to Kafka
    producer.send(config['kafka']['producer_topic'], article)

    # Print the headline, article link, summary, and timestamp
    print(f"Headline: {title}")
    print(f"Link: {article_link if article_link != 'null' else 'null'}")
    print(f"Summary: {summary}")
    print(f"Timestamp: {timestamp}")
    print('---')

# Close the producer after finishing
producer.close()
