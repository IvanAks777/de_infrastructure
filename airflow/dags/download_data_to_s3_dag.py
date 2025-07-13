from airflow.decorators import dag, task
from datetime import datetime
from download_data_to_s3 import get_api_data, save_json_to_s3
import logging

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 7, 1),
    "retries": 1
}


@dag(
    schedule_interval='*/10 * * * *',
    catchup=False,
    default_args=default_args
)

def download_data_to_s3_dag():
    @task()
    def get_data_task():
        try:
            get_api_data()
            logging.info('Task completed')
        except Exception as e:
            logging.error(f'Error: {e}')
    @task()
    def download_to_s3():
        try:
            save_json_to_s3()
            logging.info(f'Task completed')
        except Exception as e:
            logging.error(f'Error: {e}')


    get_data_task = get_data_task()
    download_to_s3_task = download_to_s3()

    get_data_task >> download_to_s3_task

download_data_to_s3 = download_data_to_s3_dag()