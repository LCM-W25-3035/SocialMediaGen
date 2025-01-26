from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pymongo import MongoClient
from pynytimes import NYTAPI
import json
import os


NYT_API_KEY = "*************" 
DB_URI = "***************"
DB_NAME = "nyt_database"
COLLECTION_NAME = "articles"
LOCAL_ARCHIVE_PATH = "../Data/nyt_archive"


def fetch_articles():
    nyt = NYTAPI(NYT_API_KEY, parse_dates=True) 
    client = MongoClient(DB_URI)  
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]


    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    print(f"Fetching articles from {start_date.date()} to {end_date.date()}")

    try:
        articles = nyt.article_search(
            query="news",
            dates={"begin": start_date, "end": end_date}
        )

        
        if articles:
            for article in articles:
                collection.update_one(
                    {"_id": article["uri"]},  
                    {"$set": article},
                    upsert=True
                )
            print(f"Inserted {len(articles)} articles.")
        else:
            print("No new articles found.")
    except Exception as e:
        print("Error fetching articles:", e)

def archive_old_articles():
    client = MongoClient(DB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    cutoff_date = datetime.now() - timedelta(days=30)

    old_articles = list(collection.find({"pub_date": {"$lt": cutoff_date}}))
    if old_articles:
        os.makedirs(LOCAL_ARCHIVE_PATH, exist_ok=True)
        archive_file = os.path.join(LOCAL_ARCHIVE_PATH, f"archived_data_{cutoff_date.date()}.json")

        with open(archive_file, "w") as f:
            json.dump(old_articles, f, indent=4, default=str)

        collection.delete_many({"pub_date": {"$lt": cutoff_date}})
        print(f"Archived {len(old_articles)} articles to {archive_file}.")
    else:
        print("No old data to archive.")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'nyt_data_pipeline',
    default_args=default_args,
    description='Daily NYT Data Collection and Archiving',
    schedule_interval=timedelta(days=1),
    catchup=False
)

fetch_task = PythonOperator(
    task_id='fetch_articles',
    python_callable=fetch_articles,
    dag=dag,
)

archive_task = PythonOperator(
    task_id='archive_old_articles',
    python_callable=archive_old_articles,
    dag=dag,
)

fetch_task >> archive_task
