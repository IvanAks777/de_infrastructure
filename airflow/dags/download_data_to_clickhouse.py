from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import logging
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DataType, TimestampType
import os
from airflow.models import Variable
from airflow.exceptions import AirflowException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)




def create_spark_session():
    try:
        # Проверка переменных окружения
        required_vars = ["MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_ENDPOINT"]
        for var in required_vars:
            if not Variable.get(var, default_var=None):
                raise ValueError(f"Не задана обязательная переменная: {var}")

        # Пути к JAR-файлам в контейнере (из docker-compose)
        jars_dir = "/opt/jars"
        if not os.path.exists(jars_dir):
            raise FileNotFoundError(
                f"Каталог с JAR-файлами не найден: {jars_dir}. "
                "Проверьте монтирование volumes в docker-compose"
            )

        jar_files = [
            f"{jars_dir}/hadoop-aws-3.3.1.jar",
            f"{jars_dir}/aws-java-sdk-bundle-1.11.901.jar",
            f"{jars_dir}/clickhouse-jdbc-0.4.6.jar"
        ]
        for jar in jar_files:
            if not os.path.exists(jar):
                raise FileNotFoundError(f"JAR файл не найден: {jar}")

        spark = SparkSession.builder \
            .appName("MinIO Data Reader") \
            .config("spark.hadoop.fs.s3a.access.key", Variable.get("MINIO_ACCESS_KEY")) \
            .config("spark.hadoop.fs.s3a.secret.key", Variable.get("MINIO_SECRET_KEY")) \
            .config("spark.hadoop.fs.s3a.endpoint", Variable.get("MINIO_ENDPOINT")) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
            .config("spark.jars", ",".join(jar_files)) \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()

        logging.info('SparkSession успешно создана для работы с MinIO')
    except Exception as e:
        logging.error(f'Ошибка при создании SparkSession: {str(e)}')
        logging.error("Проверьте:")
        logging.error("- Наличие Java (версия 8+)")
        logging.error("- Доступность JAR-файлов")
        logging.error("- Корректность переменных окружения")
        raise AirflowException(f"Не удалось создать SparkSession: {str(e)}")
    return spark


def download_data_to_clickhouse():
    path = "s3a://weather/weather_data.json"
    spark = create_spark_session()
    schema = StructType([
        StructField("latitude", DoubleType()),
        StructField("longitude", DoubleType()),
        StructField("timezone", StringType()),
        StructField("current_weather_units", StructType([
            StructField("time", StringType())
        ])),
        StructField("current_weather", StructType([
            StructField("time", StringType()),
            StructField("temperature", DoubleType()),
            StructField("windspeed", DoubleType())
    ]))
    ])
    try:
        raw_df = spark.read.json(path, schema=schema, multiLine=True)
        logging.info("✔ DataFrame успешно загружен. Печатаю схему и первые строки:")
        raw_df.printSchema()
        raw_df.show(truncate=False)
    except Exception as e:
        logging.error(f"DataFrame не создан по причине {e}")
        raise

    flat_df = raw_df.select(
        F.col("latitude"),
        F.col("longitude"),
        F.col("timezone"),
        F.col("current_weather_units.time").alias("format_time"),
        F.to_timestamp(F.col("current_weather.time")).alias("time"),
        F.col("current_weather.temperature").alias("temperature"),
        F.col("current_weather.windspeed").alias("windspeed")
    )

    flat_df.show(truncate=False)
    flat_df.printSchema()

    logging.info("Начинаю процесс записи в Clickhouse")
    try:
        flat_df.write \
            .format("jdbc") \
            .option("url", Variable.get("CLICKHOUSE_URL")) \
            .option("user", Variable.get("CLICKHOUSE_USER")) \
            .option("password", Variable.get("CLICKHOUSE_PASSWORD")) \
            .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
            .option("dbtable", "default.weather") \
            .mode("append") \
            .save()
        logging.info('Данные успешно записаны в Clickhouse')
    except Exception as e:
        logging.error(f"Запись завершилась с ошибкой по причине {e}")



