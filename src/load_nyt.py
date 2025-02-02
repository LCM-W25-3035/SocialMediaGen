from kafka import KafkaConsumer
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import json
from transform_nyt import transform_data

DB_URI = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "nyt_database"
COLLECTION_NAME = "articles"

mongo_client = MongoClient(DB_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

es = Elasticsearch(['http://localhost:9200'])

def load_data():
    consumer = KafkaConsumer('news_topic', bootstrap_servers='localhost:9092', auto_offset_reset='earliest')

    for message in consumer:
        article = json.loads(message.value)

        cleaned_article = transform_data(article)

       
        collection.update_one(
            {"_id": cleaned_article["_id"]},  
            {"$set": cleaned_article},
            upsert=True
        )

        
        es.index(index='news_index', id=cleaned_article["_id"], document=cleaned_article)

        print(f"Loaded: {cleaned_article.get('headline', 'No Title')}")

if __name__ == "__main__":
    load_data()
