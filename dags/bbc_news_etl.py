from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "mongodb+srv://Govind:*******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "news_database"
COLLECTION_NAME = "bbc_news"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# BBC News URL
URL = "https://www.bbc.com/news"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_data():
    """Fetches raw HTML content from BBC News"""
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    return response.text

def scrape_article_description(link):
    """Scrapes the summary of an individual article"""
    try:
        response = requests.get(link, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            description_tag = soup.find('meta', attrs={"name": "description"})
            return description_tag["content"] if description_tag and description_tag.get("content") else "No description available."
        return "Failed to fetch article."
    except Exception as e:
        print(f"Error scraping description for {link}: {e}")
        return "Error fetching description."

def transform_data(**context):
    """Extracts and cleans news data from the raw HTML"""
    html_text = context['ti'].xcom_pull(task_ids='fetch_data')
    soup = BeautifulSoup(html_text, "html.parser")
    articles = []

    for headline in soup.select('h2'):
        title = headline.get_text(strip=True)
        link_tag = headline.find_parent('a')
        link = link_tag['href'] if link_tag else None
        full_link = f"https://www.bbc.com{link}" if link and link.startswith('/') else link

        if not title or not full_link:
            continue

        summary = scrape_article_description(full_link)
        timestamp = datetime.utcnow().isoformat()  # Use current time if no timestamp

        # Skip duplicate articles
        if collection.find_one({"headline": title}):
            continue

        articles.append({
            "headline": title,
            "summary": summary,
            "link": full_link,
            "timestamp": timestamp
        })

    context['ti'].xcom_push(key='transformed_data', value=articles)

def load_data(**context):
    """Loads transformed data into MongoDB, avoiding duplicates"""
    articles = context['ti'].xcom_pull(task_ids='transform_data', key='transformed_data')

    if not articles:
        print("No new articles to upload.")
        return

    try:
        collection.insert_many(articles)
        print(f"Successfully inserted {len(articles)} articles into MongoDB.")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 16),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'bbc_news_etl',
    default_args=default_args,
    description='ETL pipeline for BBC News scraping',
    schedule_interval="0 */1 * * *",  
    catchup=False,
)

# Define Airflow Tasks
fetch_task = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

fetch_task >> transform_task >> load_task
