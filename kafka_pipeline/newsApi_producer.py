from kafka import KafkaProducer
import json
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import time
import schedule

# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'news_data'

# API keys (6 in total)
api_keys = [
    '6fa922774e3548a3825bdb717a570d81',
    '8420df35e605441d92e5c763b0110bfa',
    '77f7879369e54ba98b8225d153d7b78b',
    '121a6d5420fb49ac8eda4b8dc9112c51',
    '080bdb5200754c16b529c07a97ec3061',
    '664a5901f8db44c2970051b51b7f06e7'
]
total_keys = len(api_keys)
current_key_index = 0  # Start from the first key

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
    global current_key_index

    s_time = time.time()
    today = datetime.now()
    last_week = today - timedelta(days=7)
    from_date = last_week.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    if current_key_index >= total_keys:
        print("\n All API keys have been used once. Stopping execution.")
        schedule.clear()  # Stop scheduled jobs
        return

    api_key = api_keys[current_key_index]  # Use the current key
    print(f"\n Using API Key {current_key_index + 1}/{total_keys}: {api_key}")
    news_api = NewsApiClient(api_key=api_key)

    source_indices = {category: 0 for category in categories}  # Track source index per category

    # Loop through each category to fetch news
    for category in categories:
        sources = category_sources[category]
        num_sources = len(sources)

        for _ in range(num_sources):
            source_index = source_indices[category] % num_sources  # Rotate sources per category
            source = sources[source_index]
            source_indices[category] += 1  # Move to next source in next iteration

            print(f"📡 Fetching articles from {source} for category {category}")
            try:
                response = news_api.get_everything(
                    sources=source, from_param=from_date, to=to_date,
                    page=1, page_size=16, language='en'
                )
                if 'articles' in response and response['articles']:
                    for article in response['articles']:
                        article['category'] = category  # Add category
                        producer.send(KAFKA_TOPIC, article)  # Send to Kafka
                        print(f" Published: {article['title']}")
                else:
                    print(f" No articles found for {category}")

            except Exception as e:
                print(f" Error fetching news for {category}: {e}")

    # Move to the next API Key
    current_key_index += 1

    e_time = time.time()
    print(f'\n Fetch complete! Time taken: {e_time - s_time:.2f} seconds')

    # Flush the producer to ensure all messages are sent
    producer.flush()

# Schedule the function to run every 15 minutes
schedule.every(15).minutes.do(fetch_and_publish_news)

# Run the first fetch before scheduling the rest
print("\n Starting news fetcher. Fetching news every 15 minutes...")
fetch_and_publish_news()  # Run once before starting the loop

# Run the scheduler
while schedule.get_jobs():  # Only run if there are scheduled jobs
    schedule.run_pending()
    time.sleep(1)

print("\n Script execution completed. Exiting.")
