import yaml
from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# Load YAML config
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Kafka Consumer setup using loaded config
consumer = KafkaConsumer(
    config['kafka']['consumer_topic'],
    bootstrap_servers=config['kafka']['bootstrap_servers'],
    group_id=config['kafka']['group_id'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# MongoDB setup using loaded config
client = MongoClient('mongodb+srv://talk2akashkumar:5374%40marblewood@newsinsight.ogfr7.mongodb.net/')
db = client['news_database']
collection = db['bnn_news']

# Consume and store data
for message in consumer:
    article = message.value
    # Insert the article into MongoDB
    collection.insert_one(article)

    # Print the article details
    print(f"Saved article: {article['title']} to MongoDB")
