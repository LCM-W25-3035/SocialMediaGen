from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB Connection
MONGO_URI = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "news_database"
COLLECTION_NAME = "ctv_news"

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# URL of CTV News
URL = "https://www.ctvnews.ca/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_data():
    """Fetches raw HTML content from CTV News"""
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    return response.text

def transform_data(**context):
    """Extracts and cleans news data from the raw HTML"""
    html_text = context['ti'].xcom_pull(task_ids='fetch_data')
    soup = BeautifulSoup(html_text, "html.parser")
    articles = []

    for article in soup.find_all('div', class_='c-stack'):
        headline_elem = article.find('h2', class_='c-heading')
        summary_elem = article.find('p', class_='c-paragraph')
        link_elem = article.find('a', class_='c-link')
        time_elem = datetime.utcnow().isoformat()  # Use current time if no timestamp

        headline = headline_elem.text.strip() if headline_elem else "N/A"
        summary = summary_elem.text.strip() if summary_elem else "N/A"
        link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else "N/A"

        # Skip duplicate articles
        if collection.find_one({"headline": headline}):
            continue

        articles.append({
            "headline": headline,
            "summary": summary,
            "link": link,
            "timestamp": time_elem  # Store current timestamp if missing
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
        print(f"rror inserting data into MongoDB: {e}")

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
    'ctv_news_etl',
    default_args=default_args,
    description='ETL pipeline for CTV News scraping',
    schedule_interval="0 */4 * * *",  # Runs every 4 hours
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
