"""Reproducible telemetry emulator for a laptop or Raspberry Pi."""
import logging
import math
import os
import random
import signal
import threading
import time
import uuid
from config import AGV_ID, TELEMETRY_TOPIC
from telemetry import MOTORS, validate
from transport import get_producer, send
LOG = logging.getLogger(__name__)

def make_payload(sequence, elapsed, rng, session_id, scenario="normal", timestamp=None):
    patterns = ((100, 100, 100, 100), (100, -100, -100, 100),
                (80, -80, 80, -80), (-100, 100, 100, -100))
    rpms = patterns[int(elapsed // 10) % len(patterns)]
    motors = {name: {"speed_rpm": round(rpm + rng.uniform(-2, 2), 1), "temp_C": 42.0}
              for name, rpm in zip(MOTORS, rpms)}
    # Synthetic scenarios verify the pipeline, not the physical diagnostic accuracy.
    fault = scenario == "overheat" and elapsed >= 10
    if fault:
        motors["rear_right"]["temp_C"] = 65.0
        motors["rear_right"]["speed_rpm"] *= 0.2
    payload = {
        "schema_version": 1, "timestamp": time.time() if timestamp is None else timestamp,
        "agv_id": AGV_ID, "session_id": session_id, "sequence": sequence,
        "source": "emulator", "scenario": scenario, "fault_active": fault,
        "telemetry": {
            "power_supply": {"bus_voltage_V": round(48 + rng.uniform(-0.2, 0.2), 2),
                             "current_A": round((5.0 if fault else 2.5) + rng.uniform(-0.1, 0.5), 2)},
            "motors": motors,
            "imu": {"accel_g": {"x": 0.02, "y": -0.01, "z": 0.99},
                    "gyro_dps": {"x": 0.0, "y": 0.0, "z": 0.0}},
        },
    }
    validate(payload)
    return payload

def start_emulator():
    hz = float(os.getenv("EMULATOR_HZ", "10"))
    duration = float(os.getenv("EMULATOR_DURATION_S", "0"))
    scenario = os.getenv("EMULATOR_SCENARIO", "normal")
    if not math.isfinite(hz) or not 0 < hz <= 1000 or not math.isfinite(duration) or duration < 0:
        raise ValueError("EMULATOR_HZ must be in (0, 1000], duration >= 0")
    if scenario not in ("normal", "overheat"):
        raise ValueError("EMULATOR_SCENARIO must be normal or overheat")
    rng = random.Random(int(os.getenv("EMULATOR_SEED", "42")))
    session_id = str(uuid.uuid4())
    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    producer = get_producer()
    started = deadline = time.monotonic()
    sequence = 0
    try:
        while not stop.is_set():
            elapsed = time.monotonic() - started
            if duration and elapsed >= duration:
                break
            send(producer, TELEMETRY_TOPIC, make_payload(sequence, elapsed, rng, session_id, scenario))
            sequence += 1
            if sequence % max(1, int(hz)) == 0:
                LOG.info("Acknowledged=%s session=%s", sequence, session_id)
            deadline += 1 / hz
            deadline = max(deadline, time.monotonic())
            stop.wait(max(0, deadline - time.monotonic()))
    finally:
        producer.close(timeout=10)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    start_emulator()
