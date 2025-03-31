from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb+srv://devansh:*******@cluster2.q4obi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster2")
db = client["news_db"]
collection = db["guardian_news"]

# URL of The Guardian homepage or relevant section
URL = "https://www.theguardian.com/world"
headers = {"User-Agent": "Mozilla/5.0"}

def fetch_data():
    response = requests.get(URL, headers=headers)
    return response.text

def transform_data(**context):
    html_text = context['ti'].xcom_pull(task_ids='fetch_data')
    soup = BeautifulSoup(html_text, "html.parser")
    articles = []
    
    for article in soup.find_all("div", class_="dcr-f9aim1"):
        headline_elem = article.find("h3", class_="card-headline")
        summary_elem = article.find("div", class_="dcr-4v2oe6")
        link_elem = article.find("a")
        time_elem = article.find("time")
        
        headline = headline_elem.text.strip() if headline_elem else None
        summary = summary_elem.text.strip() if summary_elem else None
        link = f"https://www.theguardian.com{link_elem['href']}" if link_elem else None
        timestamp = time_elem["datetime"] if time_elem else None

        if timestamp:
            timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%b. %d, %Y, %I:%M %p GMT")
        
        articles.append({
            "headline": headline if headline else None,
            "summary": summary if summary else None,
            "link": link if link else None,
            "timestamp": timestamp if timestamp else None,
        })
    
    context['ti'].xcom_push(key='transformed_data', value=articles)

def load_data(**context):
    articles = context['ti'].xcom_pull(task_ids='transform_data', key='transformed_data')
    
    for article in articles:
        if not collection.find_one({"link": article["link"]}):
            collection.insert_one(article)
            print(f"Stored: {article['headline']}")
        else:
            print(f"Duplicate found: {article['headline']}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 16),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'guardian_news_etl',
    default_args=default_args,
    description='ETL pipeline for Guardian news scraping',
    schedule_interval=timedelta(hours=1),
    catchup=False,
)

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
