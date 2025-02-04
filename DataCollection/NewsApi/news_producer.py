from kafka import KafkaProducer
import json
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import time

# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'news_data'

# API keys
api_keys = ['6fa922774e3548a3825bdb717a570d81','8420df35e605441d92e5c763b0110bfa','77f7879369e54ba98b8225d153d7b78b','121a6d5420fb49ac8eda4b8dc9112c51','080bdb5200754c16b529c07a97ec3061','664a5901f8db44c2970051b51b7f06e7']

# Categories and Sources
categories = ['technology', 'sports', 'entertainment', 'politics', 'business']
category_sources = {
    'technology': ['techcrunch', 'the-verge', 'wired', 'ars-technica', 'engadget', 'gruenderszene'],
    'sports': ['espn', 'bbc-sport', 'fox-sports', 'four-four-two', 'bleacher-report', 'nfl-news'],
    'entertainment': ['buzzfeed', 'mtv-news', 'entertainment-weekly', 'polygon', 'ign', 'the-lad-bible'],
    'politics': ['cnn', 'bbc-news', 'reuters', 'politico', 'the-hill', 'the-washington-times'],
    'business': ['business-insider', 'the-wall-street-journal', 'bloomberg', 'fortune', 'financial-post', 'les-echos']
}

# Kafka Producer
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def fetch_and_publish_news():
    s_time = time.time()
    today = datetime.now()
    last_week = today - timedelta(days=7)
    from_date = last_week.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    total_keys = len(api_keys)
    key_index = 0
    source_indices = {category: 0 for category in categories}  # Track source index per category
    
    # will loop through each category to fetch news articles from sources
    for category in categories:
        sources = category_sources[category]
        num_sources = len(sources)
        
        # Will loop through each source in the current category
        for _ in range(num_sources):
            source_index = source_indices[category] % num_sources  # Rotate sources per category
            source = sources[source_index]
            source_indices[category] += 1  # Move to next source in next iteration

            api_key = api_keys[key_index % total_keys]
            print(f"Using API key {key_index + 1}: {api_key}, Source: {source}")
            news_api = NewsApiClient(api_key=api_key)

            articles_fetched = False

            print(f"Fetching articles from source {source} for category {category}")
            try:
                response = news_api.get_everything(
                    sources=source,         # Specifying sources directly
                    from_param=from_date,   # Date from fetching news
                    to=to_date,             # Date to fetching news
                    page=1,                 # Start from page 1
                    page_size=16,           # Fetch 16 articles per page
                    language='en'           # Specifying language as English
                )
                if 'articles' in response and response['articles']:
                    for article in response['articles']: 
                        article['category'] = category             # Adding the category to the article metadata
                        producer.send(KAFKA_TOPIC, article)        # Sending article to Kafka topic
                        print(f"Published: {article['title']}")
                else:
                    print(f"No articles found for {category}")

            except Exception as e:
                print(f"Error fetching news for {category}: {e}")


    e_time = time.time()
    print(f'Fetch complete! Time taken: {e_time - s_time:.2f} seconds')
    
    # Flush the producer to ensure all messages are sent before the script ends
    producer.flush()


# Execute once per run
fetch_and_publish_news()

