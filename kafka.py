from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json

class KafkaConnector:
    def __init__(self, bootstrap_servers=None):
        self.bootstrap_servers = bootstrap_servers or [
            'kafka:9092',
            'kafka2:9093',
            'kafka3:9094'
        ]

    def create_producer(self):
        """Create a Kafka producer instance"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            return producer
        except KafkaError as e:
            print(f"Failed to create producer: {e}")
            raise

    def create_consumer(self, topic, group_id=None):
        """Create a Kafka consumer instance"""
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            return consumer
        except KafkaError as e:
            print(f"Failed to create consumer: {e}")
            raise

    def produce_message(self, topic, message):
        """Produce a message to Kafka topic"""
        producer = self.create_producer()
        try:
            future = producer.send(topic, message)
            future.get(timeout=10)
            print(f"Message sent to {topic}")
        except KafkaError as e:
            print(f"Failed to send message: {e}")
            raise
        finally:
            producer.close()

    def consume_messages(self, topic, group_id=None):
        """Consume messages from Kafka topic"""
        consumer = self.create_consumer(topic, group_id)
        try:
            for message in consumer:
                print(f"Received message: {message.value}")
        except KeyboardInterrupt:
            print("Consumer stopped")
        finally:
            consumer.close()

if __name__ == "__main__":
    # Example usage
    kafka = KafkaConnector()

    # Produce a test message
    kafka.produce_message("test_topic", {"key": "value"})

    # Consume messages
    kafka.consume_messages("test_topic")
