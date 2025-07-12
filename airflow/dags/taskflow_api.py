from airflow.decorators import dag, task

from datetime import datetime, timedelta

default_args = {
    'owner' : 'ivan',
    'retries':3,
    'retry_delay': timedelta(minutes=3),
    'catchup': False,
}

@dag(
    dag_id = 'taskflow_api',
    default_args=default_args,
    start_date=datetime(2025,2,2),
    schedule_interval='@daily',
    catchup=False
)
# backfill s
def hello_world_etl():

    @task(multiple_outputs=True)
    def get_name():
        return {
            'first_name': 'Ivan',
            'last_name': 'Aksyonov'
        }

    @task
    def get_age():
        return 22

    @task
    def greet(first_name, last_name, age):
        print(f'Hello, {first_name} {last_name}, you are {age}')

    name_dict = get_name()
    age = get_age()
    greet(first_name=name_dict['first_name'], last_name=name_dict['last_name'], age=age)


greet_dag = hello_world_etl()
