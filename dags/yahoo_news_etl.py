from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
DB_NAME = "news_database"
COLLECTION_NAME = "yahoo_news"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Yahoo News URL
URL = "https://news.yahoo.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_data():
    """Fetches raw HTML content from Yahoo News"""
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    return response.text

def transform_data(**context):
    """Extracts and cleans news data from the raw HTML"""
    html_text = context['ti'].xcom_pull(task_ids='fetch_data')
    soup = BeautifulSoup(html_text, "html.parser")
    articles = []

    base_url = "https://news.yahoo.com"
    for element in soup.find_all('h3'):
        headline_text = element.get_text(strip=True)
        link_tag = element.find('a')
        link = link_tag.get('href') if link_tag else None

        # Convert relative link to absolute
        if link and link.startswith('/'):
            link = base_url + link

        # Extract summary from nearby paragraph tag
        paragraph_text = None
        parent_container = element.find_parent(['div', 'li', 'section'])
        if parent_container:
            p_tag = parent_container.find('p')
            if p_tag:
                paragraph_text = p_tag.get_text(strip=True)

        timestamp = datetime.utcnow().isoformat()  # Use current time if no timestamp

        # Skip duplicate articles
        if collection.find_one({"headline": headline_text}):
            continue

        articles.append({
            "headline": headline_text,
            "summary": paragraph_text if paragraph_text else "N/A",
            "link": link if link else "N/A",
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
    'yahoo_news_etl',
    default_args=default_args,
    description='ETL pipeline for Yahoo News scraping',
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
