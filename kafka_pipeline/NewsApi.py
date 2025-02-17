import asyncio
import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from newsapi import NewsApiClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

# Kafka and MongoDB Configurations
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "news_data"
MONGO_URI = "mongodb+srv://Govind:*******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"

# API Keys and Assigned Sources
api_keys = ['6fa922774e3548a3825bdb717a570d81', '8420df35e605441d92e5c763b0110bfa', 
            '77f7879369e54ba98b8225d153d7b78b', '121a6d5420fb49ac8eda4b8dc9112c51', 
            '080bdb5200754c16b529c07a97ec3061', '664a5901f8db44c2970051b51b7f06e7']

# Map each API key to a specific set of sources per category
api_key_sources = {
    api_keys[0]: {'technology': 'techcrunch', 'sports': 'espn', 'entertainment': 'buzzfeed', 'politics': 'cnn', 'business': 'business-insider'},
    api_keys[1]: {'technology': 'the-verge', 'sports': 'fox-sports', 'entertainment': 'mtv-news', 'politics': 'bbc-news', 'business': 'bloomberg'},
    api_keys[2]: {'technology': 'wired', 'sports': 'four-four-two', 'entertainment': 'entertainment-weekly', 'politics': 'reuters', 'business': 'fortune'},
    api_keys[3]: {'technology': 'ars-technica', 'sports': 'bleacher-report', 'entertainment': 'polygon', 'politics': 'politico', 'business': 'the-wall-street-journal'},
    api_keys[4]: {'technology': 'engadget', 'sports': 'nfl-news', 'entertainment': 'ign', 'politics': 'the-hill', 'business': 'financial-post'},
    api_keys[5]: {'technology': 'gruenderszene', 'sports': 'bbc-sport', 'entertainment': 'the-lad-bible', 'politics': 'the-washington-times', 'business': 'les-echos'}
}

# MongoDB Async Connection
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["News_Api"]
collection = db["News_data"]

async def fetch_news_and_produce():
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()

    try:
        key_index = 0  # Start with the first API key
        while True:  # Infinite loop to fetch data every 15 minutes
            api_key = api_keys[key_index]  # Get the current API key
            sources = api_key_sources[api_key]  # Get sources assigned to this key
            
            print(f"\nFetching news using API Key {key_index + 1}: {api_key}...\n")

            today = datetime.utcnow()
            last_week = today - timedelta(days=7)
            from_date, to_date = last_week.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

            news_api = NewsApiClient(api_key=api_key)

            for category, source in sources.items():
                try:
                    response = news_api.get_everything(
                        sources=source, from_param=from_date, to=to_date, language="en"
                    )

                    if response.get("articles"):
                        for article in response["articles"]:
                            # Rename columns and keep only required fields
                            filtered_article = {
                                "headline": article.get("title"),
                                "Summary": article.get("content"),
                                "link": article.get("url"),
                                "timestamp": article.get("publishedAt"),
                                "category": category
                            }

                            # Drop articles where headline or Summary is missing
                            if not filtered_article["headline"] or not filtered_article["Summary"]:
                                print(f"Skipped article due to missing headline or summary: {article.get('url')}")
                                continue

                            await producer.send(KAFKA_TOPIC, filtered_article)
                            print(f"Produced: {filtered_article['headline']} (Category: {category}, Source: {source})")

                except Exception as e:
                    print(f"API Error ({api_key} - {category}/{source}): {e}")

            # Rotate to the next API key
            key_index = (key_index + 1) % len(api_keys)

            print("\nWaiting 15 minutes before the next fetch...\n")
            await asyncio.sleep(900)  # Wait for 15 minutes

    finally:
        await producer.stop()

async def consume_and_store():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    await consumer.start()

    try:
        async for message in consumer:
            news_article = message.value

            # Drop articles where headline or Summary is missing
            if not news_article.get("headline") or not news_article.get("Summary"):
                print(f"Skipped storing article due to missing headline or summary: {news_article.get('link')}")
                continue

            if not await collection.find_one({"link": news_article.get("link")}):
                await collection.insert_one(news_article)
                print(f"Stored: {news_article['headline']}")
            else:
                print(f"Duplicate skipped: {news_article['headline']}")
    finally:
        await consumer.stop()

async def main():
    producer_task = asyncio.create_task(fetch_news_and_produce())
    consumer_task = asyncio.create_task(consume_and_store())
    await asyncio.gather(producer_task, consumer_task)

if __name__ == "__main__":
    asyncio.run(main())
