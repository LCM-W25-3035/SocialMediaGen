from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# Kafka and MongoDB configurations
KAFKA_TOPIC = 'news_data'
KAFKA_BROKER = 'localhost:9092'
MONGO_URL = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URL)
    db = client['News_Api']
    collection = db['News_data']
    print("Connected to MongoDB successfully!")
except Exception as e:
    print("Failed to connect to MongoDB:", e)
    exit()

# Connect to Kafka
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Listening for messages...")

for message in consumer:
    news_article = message.value
    print("Received from Kafka:", news_article)  # Print the data before inserting

    # Ensure the article has a unique URL before inserting
    if not collection.find_one({'url': news_article.get('url')}):
        collection.insert_one(news_article)
        print(f"Stored in MongoDB: {news_article['title']}")
    else:
        print(f"Duplicate skipped: {news_article['title']}")
