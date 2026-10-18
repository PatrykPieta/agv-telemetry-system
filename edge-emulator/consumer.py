"""Atomic Kafka -> PostgreSQL batches, replay protection and rejected-message archive."""
import json
import logging
import os
import signal
import threading
from pathlib import Path
import psycopg2
from kafka import KafkaConsumer
from kafka.structs import OffsetAndMetadata
from config import KAFKA_SERVER, TELEMETRY_TOPIC, db_settings
from telemetry import validate
LOG = logging.getLogger(__name__)

def reject_constant(value):
    raise ValueError("Non-finite JSON number: " + value)

INSERT = """INSERT INTO telemetry (
    time, agv_id, bus_voltage_v, current_a,
    fl_rpm, fl_temp_c, fr_rpm, fr_temp_c, rl_rpm, rl_temp_c, rr_rpm, rr_temp_c,
    accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
) VALUES (to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

def connect_db():
    return psycopg2.connect(**db_settings())

def init_db(conn):
    with conn, conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
        cur.execute("""CREATE TABLE IF NOT EXISTS telemetry (
            time TIMESTAMPTZ NOT NULL, agv_id TEXT,
            bus_voltage_v DOUBLE PRECISION, current_a DOUBLE PRECISION,
            fl_rpm DOUBLE PRECISION, fl_temp_c DOUBLE PRECISION,
            fr_rpm DOUBLE PRECISION, fr_temp_c DOUBLE PRECISION,
            rl_rpm DOUBLE PRECISION, rl_temp_c DOUBLE PRECISION,
            rr_rpm DOUBLE PRECISION, rr_temp_c DOUBLE PRECISION,
            accel_x DOUBLE PRECISION, accel_y DOUBLE PRECISION, accel_z DOUBLE PRECISION,
            gyro_x DOUBLE PRECISION, gyro_y DOUBLE PRECISION, gyro_z DOUBLE PRECISION)""")
        cur.execute("SELECT create_hypertable('telemetry', 'time', if_not_exists => TRUE, migrate_data => TRUE)")
        cur.execute("CREATE INDEX IF NOT EXISTS telemetry_agv_time ON telemetry (agv_id, time DESC)")
        cur.execute("""CREATE TABLE IF NOT EXISTS ingested_messages (
            topic TEXT NOT NULL, partition_id INTEGER NOT NULL, offset_id BIGINT NOT NULL,
            received_at TIMESTAMPTZ NOT NULL DEFAULT now(), payload JSONB,
            PRIMARY KEY (topic, partition_id, offset_id))""")
        cur.execute("""CREATE TABLE IF NOT EXISTS rejected_messages (
            topic TEXT NOT NULL, partition_id INTEGER NOT NULL, offset_id BIGINT NOT NULL,
            received_at TIMESTAMPTZ NOT NULL DEFAULT now(), reason TEXT NOT NULL, raw_value BYTEA,
            PRIMARY KEY (topic, partition_id, offset_id))""")

def persist_batch(conn, records):
    """Return offsets only after the entire DB transaction commits."""
    offsets = {}
    with conn, conn.cursor() as cur:
        for tp, messages in records.items():
            for message in messages:
                identity = (message.topic, message.partition, message.offset)
                cur.execute("""INSERT INTO ingested_messages (topic, partition_id, offset_id)
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING RETURNING offset_id""", identity)
                if cur.fetchone() is not None:
                    try:
                        data = json.loads(message.value, parse_constant=reject_constant)
                        row = validate(data)
                    except (ValueError, KeyError, TypeError, OverflowError, UnicodeError) as exc:
                        cur.execute("""INSERT INTO rejected_messages
                            (topic, partition_id, offset_id, reason, raw_value)
                            VALUES (%s, %s, %s, %s, %s)""", (*identity, str(exc), message.value))
                        LOG.warning("Rejected %s: %s", identity, exc)
                    else:
                        cur.execute(INSERT, row)
                        cur.execute("""UPDATE ingested_messages SET payload=%s::jsonb
                            WHERE topic=%s AND partition_id=%s AND offset_id=%s""",
                            (json.dumps(data, allow_nan=False), *identity))
                offsets[tp] = OffsetAndMetadata(message.offset + 1, "", -1)
    return offsets

def start_consumer():
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    conn = connect_db()
    consumer = None
    try:
        init_db(conn)
        consumer = KafkaConsumer(
            TELEMETRY_TOPIC, bootstrap_servers=KAFKA_SERVER.split(","),
            group_id=os.getenv("DB_CONSUMER_GROUP", "agv_db_writers"),
            enable_auto_commit=False, auto_offset_reset="earliest", max_poll_records=200,
        )
        while not stop.is_set():
            records = consumer.poll(timeout_ms=500)
            if records:
                consumer.commit(offsets=persist_batch(conn, records))
            Path('/tmp/consumer-health').touch()
    finally:
        # Fail closed: Docker restarts on DB/commit errors; the ledger makes replay safe.
        if consumer is not None:
            consumer.close(autocommit=False)
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_consumer()
