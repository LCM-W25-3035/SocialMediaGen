from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pymongo import MongoClient
import requests

# NYT API Key (Replace with your actual API key)
NYT_API_KEY = "15MPlclMxKGuTa7WreSZ9IYcbjoo45sL"

# MongoDB Connection
MONGO_URI = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "news_database"
COLLECTION_NAME = "nyt_news"

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
    'nyt_news_scraper',
    default_args=default_args,
    description='Scrapes NYT News and stores it in MongoDB',
    schedule_interval="0 */4 * * *",  # Runs every 4 hours
    catchup=False
)

def extract_news():
    """Fetches news articles from the NYT API and stores them in MongoDB"""

    # MongoDB Setup
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Step 1: Remove existing duplicates
    print("Checking for duplicate records...")
    pipeline = [
        {"$group": {
            "_id": {"headline": "$headline", "pub_date": "$pub_date"},
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
    print("🔧 Creating unique index on 'headline' and 'pub_date'...")
    collection.create_index([("headline", 1), ("pub_date", 1)], unique=True)
    print("Unique index created successfully.")

    # Step 3: Fetch articles from NYT API
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")

    url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?q=news&begin_date={start_date}&end_date={end_date}&api-key={NYT_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("response", {}).get("docs", [])

        if articles:
            print(f"Found {len(articles)} new articles.")
            for article in articles:
                cleaned_article = transform_data(article)

                # Insert into MongoDB if not duplicate
                if not collection.find_one({"headline": cleaned_article["headline"], "pub_date": cleaned_article["pub_date"]}):
                    collection.insert_one(cleaned_article)
                    print(f"Inserted: {cleaned_article['headline']}")
                else:
                    print(f"Skipped (duplicate): {cleaned_article['headline']}")
        else:
            print("No new articles found.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")

def transform_data(article):
    """Cleans and prepares the news article for storage in MongoDB"""

    cleaned_data = {key: value for key, value in article.items() if value not in [None, '', 'NaN']}

    important_fields = ['headline', 'pub_date', 'source', 'abstract', 'web_url']
    for field in important_fields:
        if field not in cleaned_data:
            cleaned_data[field] = 'N/A'

    if 'uri' in cleaned_data:
        cleaned_data['_id'] = cleaned_data.pop('uri')  

    return cleaned_data

# Define Airflow Task
extract_task = PythonOperator(
    task_id='extract_nyt_news',
    python_callable=extract_news,
    dag=dag,
)

extract_task
