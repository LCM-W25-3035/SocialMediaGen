from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "mongodb+srv://Govind:*******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "news_database"
COLLECTION_NAME = "nytimes_news"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# URL of The NYTimes homepage
URL = "https://www.nytimes.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_data():
    """Fetches raw HTML content from NYTimes"""
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    return response.text

def transform_data(**context):
    """Extracts and cleans news data from the raw HTML"""
    html_text = context['ti'].xcom_pull(task_ids='fetch_data')
    soup = BeautifulSoup(html_text, "html.parser")
    articles = []

    for item in soup.find_all('section', class_='story-wrapper'):
        headline_elem = item.find('p', class_='indicate-hover')
        summary_elem = item.find('p', class_='summary-class')
        link_elem = item.find('a', href=True)
        time_elem = item.find('time', class_='css-16lxk39')

        headline = headline_elem.text.strip() if headline_elem else "N/A"
        summary = summary_elem.text.strip() if summary_elem else "N/A"
        link = f"https://www.nytimes.com{link_elem['href']}" if link_elem else "N/A"
        timestamp = time_elem.text.strip() if time_elem else datetime.utcnow().isoformat()

        # Convert timestamp to readable format
        try:
            timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%b. %d, %Y, %I:%M %p GMT")
        except ValueError:
            timestamp = datetime.utcnow().strftime("%b. %d, %Y, %I:%M %p GMT")  # Use current timestamp if format is invalid

        articles.append({
            "headline": headline,
            "summary": summary,
            "link": link,
            "timestamp": timestamp
        })

    context['ti'].xcom_push(key='transformed_data', value=articles)

def load_data(**context):
    """Loads transformed data into MongoDB, avoiding duplicates"""
    articles = context['ti'].xcom_pull(task_ids='transform_data', key='transformed_data')

    for article in articles:
        if not collection.find_one({"link": article["link"]}):
            collection.insert_one(article)
            print(f"Stored: {article['headline']}")
        else:
            print(f"Skipped (duplicate): {article['headline']}")

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
    'nytimes_news_etl',
    default_args=default_args,
    description='ETL pipeline for NYTimes news scraping',
    schedule_interval="0 */1 * * *",  # Runs every 4 hours
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
