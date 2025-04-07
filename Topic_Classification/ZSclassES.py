import logging
from transformers import pipeline
from pymongo import MongoClient
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError

# Setup logging for detailed output
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- MongoDB Connection Settings ---
mongo_uri = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
mongo_db_name = "news_database"            
mongo_input_collection_name = "master_news"
mongo_output_collection_name = "master_news_clean_es"  # Optional: to store classified docs

def get_mongo_collection(uri, db_name, coll_name):
    client = MongoClient(uri)
    db = client[db_name]
    logging.info("Connected to MongoDB database '%s'", db_name)
    return db[coll_name]

input_collection = get_mongo_collection(mongo_uri, mongo_db_name, mongo_input_collection_name)
output_collection = get_mongo_collection(mongo_uri, mongo_db_name, mongo_output_collection_name)

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

# --- Zero-Shot Classifier Setup ---
labels = [
    "Finance", "Politics", "Technology", "Sports", "Health",
    "Entertainment", "Environment", "Education", "Travel", "Food"
]

classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/deberta-v3-large-zeroshot-v1",
    device=0  # set to -1 to run on CPU if GPU is not available
)

batch_size = 32
confidence_threshold = 0.7

def classify_and_index():
    # Fetch all documents from the MongoDB input collection
    docs = list(input_collection.find())
    total_docs = len(docs)
    logging.info("Found %d documents in MongoDB input collection.", total_docs)
    
    all_cleaned_docs = []
    
    # Process documents in batches for classification
    for i in range(0, total_docs, batch_size):
        batch = docs[i:i + batch_size]
        # Avoid reprocessing if a topic is already set
        batch = [doc for doc in batch if "topic" not in doc]
        if not batch:
            continue
        
        # Concatenate headline and summary
        texts = [f"{doc.get('headline', '')} {doc.get('summary', '')}".strip() for doc in batch]
        results = classifier(texts, labels)
        
        for doc, res in zip(batch, results):
            top_label = res["labels"][0]
            top_score = res["scores"][0]
            doc["topic"] = top_label if top_score >= confidence_threshold else "Miscellaneous"
            # Optionally remove unwanted fields
            doc.pop("category", None)
            doc.pop("cluster", None)
            doc.pop("score", None)
            all_cleaned_docs.append(doc)
            logging.info("Processed document %s | Topic: %s", str(doc.get("_id")), doc["topic"])
        
        # Optionally, insert classified documents into the output MongoDB collection
        if batch:
            output_collection.insert_many(batch)
    
    # --- Bulk Index Classified Documents into Elasticsearch ---
    actions = []
    for doc in all_cleaned_docs:
        doc_id = str(doc.get("_id"))
        # Remove the MongoDB _id so we can use it as the ES document ID
        doc.pop("_id", None)
        action = {
            "_index": es_index,
            "_id": doc_id,
            "_source": doc
        }
        actions.append(action)
    
    if actions:
        try:
            helpers.bulk(es, actions)
            logging.info("Successfully indexed %d documents into Elasticsearch index '%s'.", len(actions), es_index)
        except BulkIndexError as bulk_error:
            logging.error("BulkIndexError: %s", bulk_error)
            for error in bulk_error.errors:
                logging.error("Error detail: %s", error)
    else:
        logging.info("No documents to index into Elasticsearch.")

if __name__ == "__main__":
    classify_and_index()
