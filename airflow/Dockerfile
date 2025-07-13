FROM apache/airflow:2.10.5-python3.9

COPY requirements.txt /requirements.txt




USER root
RUN apt-get update && apt-get install -y curl && \
    curl -L -o OpenJDK11.tar.gz https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.20.1%2B1/OpenJDK11U-jdk_x64_linux_hotspot_11.0.20.1_1.tar.gz && \
    mkdir -p /opt/java/openjdk11 && \
    tar -xzf OpenJDK11.tar.gz -C /opt/java/openjdk11 --strip-components=1 && \
    rm OpenJDK11.tar.gz

# Копируем JAR'ы для работы с MinIO (s3a)
COPY ./jars/aws-java-sdk-bundle-1.11.901.jar /opt/jars/
COPY ./jars/hadoop-aws-3.3.1.jar /opt/jars/
COPY ./jars/clickhouse-jdbc-0.4.6.jar /opt/jars/
COPY ./jars/postgresql-42.7.6.jar /opt/jars/


# Добавляем JARы в переменную окружения, чтобы Spark мог их подхватить
ENV SPARK_EXTRA_JARS=/opt/jars/aws-java-sdk-bundle-1.11.901.jar,/opt/jars/hadoop-aws-3.3.1.jar,/opt/jars/postgresql-42.7.6.jar,/opt/jars/clickhouse-jdbc-0.4.6.jar
# Устанавливаем переменные окружения для Java
ENV JAVA_HOME=/opt/java/openjdk11
ENV PATH=$JAVA_HOME/bin:$PATH


USER airflow
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

RUN pip install airflow-code-editor

