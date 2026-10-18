"""Acknowledged Kafka delivery; terminal errors stop the process visibly."""
import json
from kafka import KafkaProducer
from config import KAFKA_SERVER

def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_SERVER.split(","),
        acks="all", retries=5, max_in_flight_requests_per_connection=1,
        request_timeout_ms=15000, max_block_ms=20000,
        key_serializer=lambda key: key.encode("utf-8"),
        value_serializer=lambda value: json.dumps(value, allow_nan=False).encode("utf-8"),
    )

def send(producer, topic, payload):
    return producer.send(topic, key=payload["agv_id"], value=payload).get(timeout=30)
