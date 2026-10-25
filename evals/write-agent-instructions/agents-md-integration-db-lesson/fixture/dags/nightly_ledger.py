from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {"owner": "data-eng", "retries": 2}

with DAG(
    "nightly_ledger",
    start_date=datetime(2025, 1, 1),
    schedule="0 3 * * *",
    catchup=False,
    default_args=default_args,
) as dag:
    PythonOperator(task_id="run", python_callable=lambda: None)
