from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta

default_args = {
    'owner': 'ivan',
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'catchup': False,
}

def greet(ti):
    first_name = ti.xcom_pull(task_ids='get_name', key='first_name')
    last_name = ti.xcom_pull(task_ids='get_name', key='last_name')
    age = ti.xcom_pull(task_ids='get_age', key='age')
    print(f'Hello, {first_name} {last_name}, I am {age}')


def get_name(ti):
    ti.xcom_push(key='first_name', value='Jerry')
    ti.xcom_push(key='last_name', value='Freedman')

def get_age(ti):
    ti.xcom_push(key='age', value=22)


with DAG (
    dag_id = 'dag_test',
    default_args=default_args,
    description='first PythonOperator',
    start_date = datetime(2025, 2, 6),
    schedule_interval = '@daily'
) as dag:

    task2 = PythonOperator(
            task_id='get_name',
            python_callable=get_name
            )


    task1 = PythonOperator(
        task_id='greet',
        python_callable=greet,
    )

    task3 = PythonOperator(
        task_id = 'get_age',
        python_callable=get_age
    )


    [task2, task3] >> task1


# max x_com = 48 kb


