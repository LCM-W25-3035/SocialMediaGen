from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 16),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'bnn_bloomberg_scraper',
    default_args=default_args,
    description='Scrapes BNN Bloomberg News and stores it in MongoDB',
    schedule_interval="0 */1 * * *",  
    catchup=False
)

# MongoDB Connection
MONGO_URI = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "news_database"
COLLECTION_NAME = "bnn_news"

def scrape_bnn_bloomberg():
    """Scrapes BNN Bloomberg News and stores it in MongoDB"""

    # MongoDB Setup
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Step 1: Remove existing duplicates
    print("Checking for duplicate records...")
    pipeline = [
        {"$group": {
            "_id": {"title": "$title", "link": "$link"},
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
    print("🔧 Creating unique index on 'title' and 'link'...")
    collection.create_index([("title", 1), ("link", 1)], unique=True)
    print("Unique index created successfully.")

    # Step 3: Scrape BNN Bloomberg Homepage
    url = "https://www.bnnbloomberg.ca"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve page: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = soup.find_all('h2', class_='c-heading')

    # Step 4: Reset set for fresh scraping
    seen_links = set()

    print("Scraping BNN Bloomberg news...")
    for headline in headlines:
        link_tag = headline.find('a', class_='c-link')

        # Initialize variables
        title = 'null'
        article_link = 'null'
        summary = 'null'
        timestamp = 'null'

        if link_tag:
            title = link_tag.text.strip()
            article_link = link_tag['href']

            # Check for duplicate articles within this run
            if article_link in seen_links:
                continue
            seen_links.add(article_link)

            full_article_link = url + article_link
            try:
                article_response = requests.get(full_article_link, timeout=10)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                # Extract summary
                summary_tag = article_soup.find('meta', {'name': 'description'})
                summary = summary_tag['content'] if summary_tag else 'null'

                # Extract timestamp
                timestamp_tag = article_soup.find('time')
                timestamp = timestamp_tag['datetime'] if timestamp_tag else 'null'
            except requests.exceptions.RequestException:
                pass

        # Create the article object
        news_item = {
            "title": title,
            "link": article_link,
            "summary": summary,
            "timestamp": timestamp
        }

        # Step 5: Insert into MongoDB if not duplicate
        if not collection.find_one({"title": news_item["title"], "link": news_item["link"]}):
            collection.insert_one(news_item)
            print(f"Inserted: {news_item['title']}")
        else:
            print(f"Skipped (duplicate): {news_item['title']}")

    print("Scraping and database update completed successfully!")

# Define Airflow Task
scrape_task = PythonOperator(
    task_id='scrape_bnn_bloomberg_news',
    python_callable=scrape_bnn_bloomberg,
    dag=dag,
)

scrape_task
