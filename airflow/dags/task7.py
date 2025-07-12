import os, sys
import json
import requests
import pandas as pd 
from io import StringIO
from datetime import datetime, timedelta


from airflow import DAG
from airflow.decorators import dag, task

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

PATH = '/opt/airflow/dags'


default_args = {
  'owner': 'Ivan',
  'depends_on_past': False,
  'retries': 2,
  'retry_interval': timedelta(minutes=1)
}

def load_data(url, folder, name):
  response = requests.get(url, stream=True)
  json_data = response.json()
  json_string = json.dumps(json_data)
  df = pd.read_json(json_string, orient='column')
  df.to_csv(f'{PATH}/{folder}/{name}', index=False)
  file_path = f'{PATH}/{folder}/{name}'
  return file_path

def insert_data(file_path):
  sio = StringIO()
  df = pd.read_csv(file_path)
  df.columns = ['user_id', 'id', 'title', 'body']
  columns = ','.join(df.columns)
  df.to_csv(sio, index=False, header=False)
  sio.seek(0)
  pg_hook = PostgresHook(postgres_conn_id='pg')
  conn = pg_hook.get_conn()
  cur = conn.cursor()
  cur.copy_expert(
      # ({columns}) optional columns
      f"""
      COPY public.test 
      FROM STDIN WITH CSV
      """,
      sio
    )
  conn.commit()
  return df.shape

with DAG(
  dag_id = 'test7',
  default_args=default_args,
  schedule_interval='1 1 * * *',
  catchup=False,
  start_date=datetime(2025, 3, 31)
) as dag:

  load_api = PythonOperator(
    task_id = 'load_api_data',
    python_callable=load_data,
    op_kwargs={
      'url': 'https://jsonplaceholder.typicode.com/posts',
      'folder': 'data',
      'name': 'test.csv'
    }
  )

  create_table = PostgresOperator(
    task_id = 'create_table',
    postgres_conn_id='pg',
    sql='/sql_scripts/ddl_script.sql'
  )
  
  truncate = PostgresOperator(
    task_id = 'truncate',
    postgres_conn_id='pg',
    sql='TRUNCATE TABLE public.test'
  )
  insert_task = PythonOperator(
    task_id = 'insert_data',
    python_callable=insert_data,
    op_kwargs={
      'file_path': '/opt/airflow/dags/data/test.csv'
    }
  )

  load_api >> create_table >> truncate >> insert_task
