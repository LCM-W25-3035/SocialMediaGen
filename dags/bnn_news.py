from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.scraping_producer import scraping_producer
from src.scraping_consumer import scraping_consumer

# import subprocess

# def start_scraping():
#     subprocess.run(['python', 'scraping_producer.py'])

# def start_consumer():
#     subprocess.run(['python', 'scraping_consumer.py'])

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 2),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'news_scraper_kafka_mongo',
    default_args=default_args,
    description='A simple DAG to scrape news, send to Kafka and load to MongoDB',
    schedule_interval=timedelta(hours=24),
)

scraping_task = PythonOperator(
    task_id='scrape_news',
    python_callable=scraping_producer,
    dag=dag,
)

consumer_task = PythonOperator(
    task_id='consume_and_save',
    python_callable=scraping_consumer,
    dag=dag,
)

scraping_task >> consumer_task
