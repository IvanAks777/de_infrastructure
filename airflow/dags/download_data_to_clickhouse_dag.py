import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from download_data_to_clickhouse import create_spark_session, download_data_to_clickhouse
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime
from airflow.utils.dates import days_ago
from airflow.models import Variable
import logging


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "retries": 1
}


with DAG (
    dag_id='download_data_to_clickhouse_dag',
    schedule_interval=None,
    catchup=False,
    default_args=default_args
) as dag:

    wait_for_update_data = ExternalTaskSensor(
        task_id="wait_for_dag_download_s3",
        external_dag_id="download_data_to_s3_dag",
        external_task_id="download_to_s3",
        allowed_states=["success"],
        failed_states=["failed", "skipped"],
        timeout=600,
        mode="poke",
        dag=dag
    )

    download_to_clickhouse = PythonOperator(
        task_id="download_to_click",
        python_callable=download_data_to_clickhouse,
        dag=dag
    )


wait_for_update_data >> download_to_clickhouse
