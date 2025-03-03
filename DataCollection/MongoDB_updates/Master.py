# Importing liabraries
from pymongo import MongoClient
from datetime import datetime
import threading

# Connectong to MongoDB
client = MongoClient("mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics")
db = client['news_database']

# Defining source collections and master collection
source_collections = ['Newsapi_data', 'bbc_news', 'bnn_news', 'cnn_news', 'ctv_news', 'guardian_news', 'nyt_news', 'nytimes_news', 'yahoo_news']
master_collection = db['master_news']

# Creating essential indexes on the master collection
master_collection.create_index([("timestamp", -1)])  # Index on 'timestamp' (descending)
master_collection.create_index([("link", 1)], unique=True)  # Unique index on 'link' for deduplication

# Function to check if a field is invalid (null or 'N/A')
def is_invalid_field(value):
    return value is None or value == 'N/A'

# Function to synchronize existing data from source collections to master collection
def synchronize_existing_data():
    for source in source_collections:
        source_collection = db[source]
        for document in source_collection.find():
            # Skip if headline or summary is null or 'N/A'
            if is_invalid_field(document.get('headline')) or is_invalid_field(document.get('summary')):
                print(f"Skipping document from {source} due to 'N/A' in headline or summary: {document.get('_id')}")
                continue
            
            # Deduplication: Check if the document already exists in the master collection
            # Using 'link' or '_id' as the unique identifier
            query = {"$or": [{"_id": document["_id"]},{"link": document.get("link")}]}
            
            existing_document = master_collection.find_one(query)
            
            if existing_document:
                print(f"Document already exists in master collection: {document.get('headline')}")
                continue
            
            # Adding source and sync timestamp to the document
            document['source'] = source
            document['sync_date'] = datetime.utcnow()
            
            # Inserting the document into the master collection
            master_collection.insert_one(document)
    print("Initial synchronization completed.")

# Function to watch a source collection for real-time updates
def watch_collection(collection_name):
    collection = db[collection_name]
    with collection.watch(full_document='updateLookup') as stream:
        for change in stream:
            if change['operationType'] in ['insert', 'update', 'replace']:
                document = change['fullDocument']
                
                # Skip if headline or summary is null or 'N/A'
                if is_invalid_field(document.get('headline')) or is_invalid_field(document.get('summary')):
                    print(f"Skipping document from {collection_name} due to 'N/A' in headline or summary: {document.get('_id')}")
                    continue
                
                # Deduplication: Check if the document already exists in the master collection
                # Using 'link' or '_id' as the unique identifier
                query = {"$or": [{"_id": document["_id"]},{"link": document.get("link")}]}
                
                existing_document = master_collection.find_one(query)
                
                if existing_document:
                    print(f"Document already exists in master collection: {document.get('headline')}")
                    continue
                
                # Adding source and sync timestamp to the document
                document['source'] = collection_name
                document['sync_date'] = datetime.utcnow()
                
                # Inserting the document into the master collection
                master_collection.insert_one(document)
                print(f"New data inserted into master collection from {collection_name}: {document.get('headline')}")

# initializing synchronization
synchronize_existing_data()

# watching each source collection for real-time updates
threads = []
for source in source_collections:
    thread = threading.Thread(target=watch_collection, args=(source,))
    thread.start()
    threads.append(thread)

# Keep the script running
for thread in threads:
    thread.join()
    
"""Prompts:
1st:
image.png
PNG 54.01KB
I have this db in mongo db with these collections, now i want to move all other collections data to master_news collection

last:
also move real time data getting saved in other sources collection to master_news while checking for duplicate entries"""

