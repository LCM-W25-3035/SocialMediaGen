from kafka import KafkaConsumer
import json
from pymongo import MongoClient

# Kafka & MongoDB Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'news_data' # topic we created in kafka
MONGO_URL = "mongodb+srv://Govind:*******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"

# MongoDB Connection
client = MongoClient(MONGO_URL)
db = client['News_Api']
collection = db['News_data']

# Kafka Consumer
consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BROKER, value_deserializer=lambda m: json.loads(m.decode('utf-8')),consumer_timeout_ms=10000) # Stop after 10s if no messages

print("Consumer started. Listening for messages...")

for message in consumer:
    news_article = message.value
    
    # Check if article already exists(deduplication)
    if not collection.find_one({'url': news_article.get('url')}):
        collection.insert_one(news_article)
        print(f"Stored: {news_article['title']}")
    else:
        print(f"Duplicate: {news_article['title']}")

print("Consumer finished processing messages.")
