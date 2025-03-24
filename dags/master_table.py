from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pymongo import MongoClient
import threading

# MongoDB connection
client = MongoClient("mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics")
db = client['news_database']
source_collections = ['Newsapi_data', 'bbc_news', 'bnn_news', 'cnn_news', 'ctv_news', 'guardian_news', 'nyt_news', 'nytimes_news', 'yahoo_news']
master_collection = db['master_news']

# Ensure indexes
master_collection.create_index([("timestamp", -1)])
master_collection.create_index([("link", 1)], unique=True)

def is_invalid_field(value):
    return value is None or value == 'N/A'

# Task 1: Sync existing data
def sync_existing_data():
    for source in source_collections:
        collection = db[source]
        for doc in collection.find():
            if is_invalid_field(doc.get('headline')) or is_invalid_field(doc.get('summary')):
                print(f"[SKIP] {source} -> {doc.get('_id')} has invalid headline or summary.")
                continue

            query = {"$or": [{"_id": doc["_id"]}, {"link": doc.get("link")}]}
            if master_collection.find_one(query):
                print(f"[DUPLICATE] {source} -> {doc.get('headline')}")
                continue

            doc['source'] = source
            doc['sync_date'] = datetime.utcnow()
            master_collection.insert_one(doc)
    print("✅ Existing data synchronized.")

# Task 2: Real-time watch logic
def start_realtime_watch():
    def watch_collection(col_name):
        collection = db[col_name]
        try:
            with collection.watch(full_document='updateLookup') as stream:
                for change in stream:
                    if change['operationType'] in ['insert', 'update', 'replace']:
                        doc = change['fullDocument']
                        if is_invalid_field(doc.get('headline')) or is_invalid_field(doc.get('summary')):
                            print(f"[SKIP REALTIME] {col_name} -> {doc.get('_id')}")
                            continue

                        query = {"$or": [{"_id": doc["_id"]}, {"link": doc.get("link")}]}
                        if master_collection.find_one(query):
                            print(f"[REALTIME DUPLICATE] {col_name} -> {doc.get('headline')}")
                            continue

                        doc['source'] = col_name
                        doc['sync_date'] = datetime.utcnow()
                        master_collection.insert_one(doc)
                        print(f"[REALTIME INSERT] {col_name} -> {doc.get('headline')}")
        except Exception as e:
            print(f"[ERROR] Watching {col_name} failed: {e}")

    # Start one thread per collection
    for col in source_collections:
        t = threading.Thread(target=watch_collection, args=(col,), daemon=True)
        t.start()

# Airflow DAG Definition
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 21),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id='news_data_sync_dag',
    default_args=default_args,
    schedule_interval='0 */1 * * *',  # Run manually or once at deployment
    catchup=False
) as dag:

    sync_task = PythonOperator(
        task_id='sync_existing_data_to_master',
        python_callable=sync_existing_data
    )

    realtime_task = PythonOperator(
        task_id='start_realtime_watch',
        python_callable=start_realtime_watch
    )

    sync_task >> realtime_task
