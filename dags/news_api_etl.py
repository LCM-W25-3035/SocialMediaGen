from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from pymongo import MongoClient
from newsapi import NewsApiClient

# MongoDB setup
MONGO_URI = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "news_database"
COLLECTION_NAME = "Newsapi_data"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# News API keys
API_KEYS = [
    "6fa922774e3548a3825bdb717a570d81",
    "8420df35e605441d92e5b763b0110bfa",
    "77f787936e54ba98b8225d153d7b78b",
    "121a6d5420fb49ac8eda4b8dc9112c51",
    "080bdb5200754c16b529c07a97ec3061",
    "664a5901f8db44c2970051b51b7f06e7"
]

# News sources
NEWS_SOURCES = [
    "cnn", "bbc-news", "reuters", "the-verge",
    "wired", "bloomberg", "business-insider",
    "fox-news", "nbc-news", "cbs-news"
]

def fetch_news():
    """Fetches news articles from multiple sources using the News API"""
    today = datetime.now()
    last_week = today - timedelta(days=7)
    from_date = last_week.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    key_index = 0
    total_keys = len(API_KEYS)

    for source in NEWS_SOURCES:
        api_key = API_KEYS[key_index % total_keys]
        print(f"Using API key {key_index + 1}: {api_key}, Source: {source}")

        news_api = NewsApiClient(api_key=api_key)
        key_index = (key_index + 1) % total_keys  # Rotate API keys

        try:
            response = news_api.get_everything(
                sources=source,
                from_param=from_date,
                to=to_date,
                page=1,
                page_size=16,
                language="en"
            )
            if "articles" in response and response["articles"]:
                articles_to_insert = []
                for article in response["articles"]:
                    news_item = {
                        "headline": article.get("title", "N/A"),
                        "summary": article.get("description", "N/A"),
                        "link": article.get("url", "N/A"),
                        "timestamp": article.get("publishedAt", datetime.utcnow().isoformat())
                    }

                    # Check for duplicates before inserting
                    if not collection.find_one({"link": news_item["link"]}):
                        articles_to_insert.append(news_item)
                        print(f"Inserted: {news_item['headline']}")
                    else:
                        print(f"Skipped (duplicate): {news_item['headline']}")

                if articles_to_insert:
                    collection.insert_many(articles_to_insert)
                    print(f"Successfully inserted {len(articles_to_insert)} articles.")

            else:
                print(f"No articles found for source: {source}")

        except Exception as e:
            print(f"Error fetching articles from source {source}: {e}")

# Default DAG arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 2, 16),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    "news_api_etl",
    default_args=default_args,
    description="ETL pipeline for fetching news from News API",
    schedule_interval="0 */4 * * *",  # Runs every 4 hours
    catchup=False,
)

# Define Airflow Task
fetch_task = PythonOperator(
    task_id="fetch_news",
    python_callable=fetch_news,
    dag=dag,
)

fetch_task
