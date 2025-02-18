from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 16),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'cnn_news_scraper',
    default_args=default_args,
    description='Scrapes CNN News and stores it in MongoDB',
    schedule_interval='@daily',  # Runs daily
    catchup=False
)

# MongoDB Connection
MONGO_URI = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "news_database"
COLLECTION_NAME = "cnn_news"

def scrape_cnn():
    """Scrapes CNN News and stores it in MongoDB"""
    
    # MongoDB Setup
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Step 1: Remove existing duplicates
    print("Checking for duplicate records...")
    pipeline = [
        {"$group": {
            "_id": {"headline": "$headline", "link": "$link"},
            "count": {"$sum": 1},
            "docs": {"$push": "$_id"}
        }},
        {"$match": {"count": {"$gt": 1}}}
    ]
    duplicates = list(collection.aggregate(pipeline))
    for dup in duplicates:
        ids_to_delete = dup["docs"][1:]  # Keep one, delete others
        collection.delete_many({"_id": {"$in": ids_to_delete}})

    print(f"Removed {len(duplicates)} duplicate records.")

    # Step 2: Ensure unique index
    print("Creating unique index on 'headline' and 'link'...")
    collection.create_index([("headline", 1), ("link", 1)], unique=True)
    print("Unique index created successfully.")

    # Step 3: Scrape CNN Homepage
    base_url = "https://www.cnn.com"

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve page: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('a', class_='container__link')

    # Step 4: Clear set for fresh scraping
    news_set = set()

    def extract_details(article_url):
        """Fetch the article page and extract timestamp and content."""
        try:
            article_response = requests.get(article_url, timeout=10)
            article_response.raise_for_status()
            article_soup = BeautifulSoup(article_response.text, 'html.parser')

            timestamp_tag = article_soup.find('div', class_='timestamp vossi-timestamp')
            timestamp = timestamp_tag.text.strip() if timestamp_tag else None

            paragraphs = article_soup.find_all('p', class_='paragraph')
            summary = " ".join(p.text.strip() for p in paragraphs) if paragraphs else None

            return timestamp, summary
        except requests.exceptions.RequestException:
            return None, None

    # Step 5: Process and insert articles into MongoDB
    print("Scraping CNN news...")
    for article in articles:
        headline = article.find('span', class_='container__headline-text')
        link = article.get('href', '')
        full_link = base_url + link if link.startswith("/") else link

        if full_link in news_set:
            continue
        news_set.add(full_link)

        timestamp, summary = extract_details(full_link)

        news_item = {
            "headline": headline.text.strip() if headline else "null",
            "link": full_link,
            "timestamp": timestamp,
            "summary": summary
        }

        # Step 6: Insert into MongoDB if not duplicate
        if not collection.find_one({"headline": news_item["headline"], "link": news_item["link"]}):
            collection.insert_one(news_item)
            print(f"Inserted: {news_item['headline']}")
        else:
            print(f"Skipped (duplicate): {news_item['headline']}")

    print("🎉 Scraping and database update completed successfully!")

# Define Airflow Task
scrape_task = PythonOperator(
    task_id='scrape_cnn_news',
    python_callable=scrape_cnn,
    dag=dag,
)

scrape_task
