import logging
from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError

# Setup logging for detailed output
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- MongoDB Connection Settings ---
mongo_uri = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
mongo_db_name = "news_database"            # Replace with your actual database name
mongo_collection_name = "master_news_cleaned"  # Replace with your collection name

def get_mongo_collection(uri, db_name, coll_name):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        logging.info("Connected to MongoDB database '%s'", db_name)
        return db[coll_name]
    except Exception as e:
        logging.error("Error connecting to MongoDB: %s", e)
        raise

collection = get_mongo_collection(mongo_uri, mongo_db_name, mongo_collection_name)

# --- Check total documents in MongoDB ---
total_docs_mongo = collection.count_documents({})
logging.info("Total documents in MongoDB collection '%s': %d", mongo_collection_name, total_docs_mongo)

# --- Elasticsearch Connection Settings ---
es_host = "https://40.118.170.15:9200"
es_username = "elastic"
es_password = "jhaA_lqCTVtvRbR1a0jf"

def get_es_client(host, username, password):
    try:
        es_client = Elasticsearch(host, basic_auth=(username, password), verify_certs=False)
        logging.info("Connected to Elasticsearch at %s", host)
        return es_client
    except Exception as e:
        logging.error("Error connecting to Elasticsearch: %s", e)
        raise

es = get_es_client(es_host, es_username, es_password)
es_index = "news_index"

# --- Generate Bulk Actions in Chunks ---
def generate_bulk_actions(collection, index, chunk_size=500):
    cursor = collection.find()
    actions = []
    for doc in cursor:
        doc_id = str(doc.get("_id"))
        # Remove the _id field (pop returns None if key doesn't exist)
        doc.pop("_id", None)
        action = {
            "_index": index,
            "_id": doc_id,
            "_source": doc
        }
        actions.append(action)
        if len(actions) >= chunk_size:
            yield actions
            actions = []
    if actions:
        yield actions

processed_count = 0
total_indexed = 0
failed_docs = 0

try:
    for chunk in generate_bulk_actions(collection, es_index, chunk_size=500):
        processed_count += len(chunk)
        try:
            helpers.bulk(es, chunk)
            total_indexed += len(chunk)
            logging.info("Successfully indexed %d documents in current chunk.", len(chunk))
        except BulkIndexError as bulk_error:
            errors = bulk_error.errors
            num_errors = len(errors)
            failed_docs += num_errors
            # Assume the rest of the chunk indexed successfully
            total_indexed += (len(chunk) - num_errors)
            logging.error("BulkIndexError: %d documents failed in current chunk.", num_errors)
            for error in errors:
                logging.error("Error detail: %s", error)
except Exception as e:
    logging.error("Error during bulk indexing: %s", e)

logging.info("Finished indexing. Total documents in MongoDB: %d, Processed: %d, Successfully indexed: %d, Failed: %d",
             total_docs_mongo, processed_count, total_indexed, failed_docs)
