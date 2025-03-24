from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError

# --- MongoDB Connection Settings ---
mongo_uri = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
mongo_db_name = "news_database"            # Replace with your actual database name
mongo_collection_name = "master_news"      # Replace with your collection name

# Connect to MongoDB
mongo_client = MongoClient(mongo_uri)
db = mongo_client[mongo_db_name]
collection = db[mongo_collection_name]

# --- Elasticsearch Connection Settings ---
es_host = "https://40.118.170.15:9200"
es_username = "elastic"
es_password = "jhaA_lqCTVtvRbR1a0jf"

# Connect to Elasticsearch using basic_auth and disable certificate verification for self-signed certs.
es = Elasticsearch(
    es_host,
    basic_auth=(es_username, es_password),
    verify_certs=False
)

# Define the Elasticsearch index name
es_index = "news_index"

# --- Prepare Data for Bulk Indexing ---
actions = []
for doc in collection.find():
    # Convert the MongoDB _id to a string for Elasticsearch
    doc_id = str(doc.get("_id"))
    # Remove the _id field so we can use it as the document ID in Elasticsearch
    if "_id" in doc:
        del doc["_id"]
    action = {
        "_index": es_index,
        "_id": doc_id,
        "_source": doc
    }
    actions.append(action)

# --- Bulk Index Documents into Elasticsearch with Error Handling ---
try:
    helpers.bulk(es, actions)
    print(f"Successfully indexed {len(actions)} documents into index '{es_index}'.")
except BulkIndexError as bulk_error:
    print(f"Bulk indexing error: {bulk_error}")
    for error in bulk_error.errors:
        print("Error details:", error)
except Exception as e:
    print(f"Error indexing: {e}")
