"""Environment configuration shared by edge processes and the DB writer."""
import os
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
TELEMETRY_TOPIC = os.getenv("TELEMETRY_TOPIC", "telemetry_topic")
LIDAR_TOPIC = os.getenv("LIDAR_TOPIC", "lidar_topic")
AGV_ID = os.getenv("AGV_ID", "AGV-01")

def db_settings():
    return dict(host=os.getenv("DB_HOST", "timescaledb"),
                port=int(os.getenv("DB_PORT", "5432")),
                dbname=os.getenv("POSTGRES_DB", "agv_db"),
                user=os.getenv("POSTGRES_USER", "admin"),
                password=os.getenv("POSTGRES_PASSWORD", "password"),
                connect_timeout=10)
