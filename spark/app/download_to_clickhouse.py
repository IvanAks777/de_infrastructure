from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
import logging
from airflow.models import Variable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    spark = SparkSession.builder \
        .appName("MinIO_to_ClickHouse") \
        .config("spark.hadoop.fs.s3a.access.key", Variable.get("MINIO_ACCESS_KEY")) \
        .config("spark.hadoop.fs.s3a.secret.key", Variable.get("MINIO_SECRET_KEY")) \
        .config("spark.hadoop.fs.s3a.endpoint", Variable.get("MINIO_ENDPOINT")) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()

    schema = StructType([
        StructField("latitude", DoubleType()),
        StructField("longitude", DoubleType()),
        StructField("timezone", StringType()),
        StructField("current_weather_units", StructType([
            StructField("time", StringType())
        ])),
        StructField("current_weather", StructType([
            StructField("time", TimestampType()),
            StructField("temperature", DoubleType()),
            StructField("windspeed", DoubleType())
        ]))
    ])

    try:
        raw_df = spark.read.json("s3a://weather/weather_data.json", schema=schema, multiLine=True)
        logging.info("DataFrame loaded successfully")

        flat_df = raw_df.select(
            F.col("latitude"),
            F.col("longitude"),
            F.col("timezone")
        )

        flat_df.write \
            .format("jdbc") \
            .option("url", Variable.get("CLICKHOUSE_URL")) \
            .option("user", Variable.get("CLICKHOUSE_USER")) \
            .option("password", Variable.get("CLICKHOUSE_PASSWORD")) \
            .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
            .option("dbtable", "default.weather") \
            .mode("append") \
            .save()

        logging.info("Data successfully written to ClickHouse")
    except Exception as e:
        logging.error(f"Job failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
