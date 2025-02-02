from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.extract_nyt import extract_nyt
from src.transform_nyt import transform_nyt
from src.load_nyt import load_nyt

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 3),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'nyt_pipeline',
    default_args=default_args,
    description='Industry-level NYT Data Pipeline with ETL',
    schedule_interval='0 5 * * *',  # Daily at 5 AM
    catchup=False
)

fetch_task = PythonOperator(
    task_id='fetch_articles',
    python_callable=extract_nyt,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_nyt,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_mongodb',
    python_callable=load_nyt,
    dag=dag,
)

fetch_task >> transform_task >> load_task
