import boto3
import requests
import logging
import json
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

logging.basicConfig(

level=logging.INFO,

format='%(asctime)s - %(levelname)s - %(message)s'

)

logger = logging.getLogger(__name__)

def get_api_data():
    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast",
        params={
                "latitude": 55.75,
                "longitude": 37.62,
                "current_weather": True
                }
        )
        if response.status_code == 200:
            data = response.json()
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            logging.info('Данные успешно загружены')
            return json_str
        else:
            logging.error(f'Error: {response.status_code} - Данные не загружены')
            return None
    except:
        logging.error(f'Error: {e} - Данные не загружены')
        raise


def save_json_to_s3():
    # Проверка подключения к S3
    try:
        hook = S3Hook(aws_conn_id="minios3_conn")
        hook.check_for_bucket(bucket_name="weather")
    except Exception as e:
        logger.error(f"Ошибка подключения к S3: {e}")
        raise
        
    data = get_api_data()
    if data:
        try:
            hook = S3Hook(aws_conn_id="minios3_conn")
            hook.load_string(
                string_data=data,
                key="weather_data.json",
                bucket_name="weather",
                replace=True
            )
            logging.info(f"Данные успешно записаны в S3")
        except Exception as e:
            logger.error(f"Ошибка {e}")
            raise
    else:
        logging.error(f"Данных нет")