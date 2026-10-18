"""End-to-end check against the isolated agv-check stack."""
import json
import random
import sys
import time
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "edge-emulator"))
from kafka import KafkaConsumer
from consumer import connect_db
from main import make_payload
from telemetry import MOTORS
from transport import get_producer, send

session = str(uuid.uuid4())
agv = "TEST-SMOKE-" + session[:8]
alerts = KafkaConsumer("alerts_topic", bootstrap_servers="kafka:9092",
                       auto_offset_reset="latest", group_id=None, enable_auto_commit=False,
                       value_deserializer=lambda value: json.loads(value))
alerts.poll(timeout_ms=1000)
producer = get_producer()
try:
    for seq in range(50):
        payload = make_payload(seq, 20, random.Random(seq), session, "overheat")
        payload["agv_id"] = agv
        for name in MOTORS:
            payload["telemetry"]["motors"][name]["temp_C"] = 65.0 if name == MOTORS[seq % 4] else 42.0
        send(producer, "telemetry_topic", payload)
    conn = connect_db()
    deadline = time.monotonic() + 45
    alerted_motors = set()
    count = 0
    while time.monotonic() < deadline:
        for messages in alerts.poll(timeout_ms=500).values():
            alerted_motors.update(m.value["motor"]["name"] for m in messages if m.value.get("agv_id") == agv)
        with conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM telemetry WHERE agv_id=%s", (agv,))
            count = cur.fetchone()[0]
        if count == 50 and alerted_motors == set(MOTORS):
            break
    assert count == 50, f"Expected 50 database rows, found {count}"
    assert alerted_motors == set(MOTORS), f"Missing motor warnings: {alerted_motors}"
    with conn, conn.cursor() as cur:
        cur.execute("""SELECT count(*) FROM ingested_messages
                       WHERE payload->>'session_id'=%s""", (session,))
        assert cur.fetchone()[0] == 50
    print("PASS: 50 acknowledged messages -> Kafka -> database, metadata archive and Spark warning")
finally:
    producer.close()
    alerts.close()
