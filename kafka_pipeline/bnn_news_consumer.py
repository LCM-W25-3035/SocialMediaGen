from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# Kafka Config
KAFKA_TOPIC = "bnn_news_topic"
KAFKA_SERVER = "localhost:9092"

# MongoDB Config
MONGO_URI = "mongodb+srv://talk2akashkumar:5374%40marblewood@newsinsight.ogfr7.mongodb.net/"
mongo_client = MongoClient(MONGO_URI)
bnn_news_db = mongo_client["bnn_news_database"]
news_collection = bnn_news_db["bnn_news_articles"]

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Listening for messages from Kafka...")

# Consume messages from Kafka and store in MongoDB
for message in consumer:
    news_collection.insert_one(message.value)
    print(f"Stored in MongoDB: {message.value}")
