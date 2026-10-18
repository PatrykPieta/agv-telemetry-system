"""IDUB Neuro-Curiosity showcase emulator — synthetic telemetry for grant presentation.

Generates realistic-looking AGV data enriched with Reinforcement Learning metrics
(Intrinsic Curiosity Module, PPO, Sim-to-Real gap) for the IDUB D12 grant demo.
All values are synthetic and designed purely for visual presentation.
"""
import json
import logging
import math
import os
import random
import signal
import threading
import time
import uuid
from kafka import KafkaProducer

AGV_ID = os.getenv("AGV_ID", "AGV-01")
TELEMETRY_TOPIC = os.getenv("TELEMETRY_TOPIC", "telemetry_topic")
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")

def get_producer():
    return KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks=1,
    )

def send(producer, topic, payload):
    producer.send(topic, key=AGV_ID.encode(), value=payload).get(timeout=5)

LOG = logging.getLogger(__name__)

# Mecanum wheel layout: FL, FR, RL, RR (signed RPM)
MOTORS = ("front_left", "front_right", "rear_left", "rear_right")

# Exploration patterns — robot navigates a warehouse grid
# Each pattern lasts ~8 seconds, simulating an episode
PATTERNS = [
    (120, 120, 120, 120),      # Forward
    (-120, 120, 120, -120),    # Strafe right (Mecanum)
    (120, -120, -120, 120),    # Strafe left
    (-90, 90, -90, 90),        # Rotate CW (turning, exploring)
    (60, 60, 60, 60),          # Slow forward (approaching obstacle)
    (0, 0, 0, 0),              # Stop — intrinsic curiosity peak (unexpected state)
    (100, 110, 100, 110),      # Forward slight turn right
    (-120, -120, -120, -120),  # Reverse
]


def _curiosity_curve(elapsed, rng):
    """Intrinsic reward follows a dampened oscillation — peaks near new obstacles."""
    base = 0.3 + 0.5 * math.exp(-elapsed / 60) * abs(math.sin(elapsed * 0.4))
    noise = rng.uniform(-0.05, 0.05)
    return round(max(0.0, min(1.0, base + noise)), 4)


def _icm_error(elapsed, rng, pattern_idx):
    """ICM forward model prediction error — high when robot enters unknown state."""
    # Spikes when pattern changes (unexpected transition)
    is_transition = (int(elapsed) % 8) == 0
    base = 0.15 + (0.6 if is_transition else 0.0)
    decay = math.exp(-((elapsed % 8) / 3.0)) if is_transition else 0
    val = base * decay + rng.uniform(0.01, 0.08)
    return round(max(0.0, min(1.0, val)), 4)


def _jerk(speed_diff, dt, rng):
    """Rate of change of acceleration (m/s^3) — smoothness metric for Jetson gait."""
    raw = abs(speed_diff) / max(dt, 0.01) * 0.001
    return round(raw + rng.uniform(0.0, 0.02), 4)


def _reality_gap(elapsed, rng):
    """Sim-to-Real gap index — decreases as policy converges (fine-tuning on hardware)."""
    base = max(0.05, 0.8 * math.exp(-elapsed / 120))
    return round(base + rng.uniform(-0.02, 0.02), 4)


def _extrinsic_reward(pattern_idx, elapsed, rng):
    """Navigation reward — positive when moving forward, zero when stopped."""
    moving = PATTERNS[pattern_idx][0] != 0
    base = 0.85 if moving else 0.0
    return round(base + rng.uniform(-0.1, 0.1), 4)


def make_idub_payload(sequence, elapsed, rng, session_id, prev_rpms, dt, timestamp=None):
    pattern_idx = int(elapsed // 8) % len(PATTERNS)
    base_rpms = PATTERNS[pattern_idx]

    motors = {
        name: {
            "speed_rpm": round(rpm + rng.uniform(-3, 3), 1),
            "temp_C": round(38.0 + abs(rpm) * 0.04 + rng.uniform(-0.5, 0.5), 1),
        }
        for name, rpm in zip(MOTORS, base_rpms)
    }

    # Spike temperature on RR when ICM error is high (simulates hard deceleration)
    if (int(elapsed) % 24) in (0, 1, 2):
        motors["rear_right"]["temp_C"] = round(
            motors["rear_right"]["temp_C"] + 8.0 + rng.uniform(0, 4), 1
        )

    # RL metrics
    speed_diff = abs(base_rpms[0] - (prev_rpms[0] if prev_rpms else base_rpms[0]))
    intrinsic_r = _curiosity_curve(elapsed, rng)
    extrinsic_r = _extrinsic_reward(pattern_idx, elapsed, rng)
    icm_err = _icm_error(elapsed, rng, pattern_idx)
    jerk_val = _jerk(speed_diff, dt, rng)
    gap_val = _reality_gap(elapsed, rng)

    # Total reward = extrinsic + beta * intrinsic (ICM standard formula)
    beta = 0.01
    total_r = round(extrinsic_r + beta * intrinsic_r, 4)

    # Training step counter
    training_step = int(elapsed * 10)  # 10 Hz -> ~step count
    policy_entropy = round(max(0.1, 1.8 - elapsed / 200 + rng.uniform(-0.05, 0.05)), 4)

    payload = {
        "schema_version": 1,
        "timestamp": time.time() if timestamp is None else timestamp,
        "agv_id": AGV_ID,
        "session_id": session_id,
        "sequence": sequence,
        "source": "idub_emulator",
        "scenario": "neuro_curiosity",
        "fault_active": False,
        "telemetry": {
            "power_supply": {
                "bus_voltage_V": round(48.0 + rng.uniform(-0.3, 0.3), 2),
                "current_A": round(
                    2.5 + abs(base_rpms[0]) * 0.015 + rng.uniform(-0.1, 0.4), 2
                ),
            },
            "motors": motors,
            "imu": {
                "accel_g": {
                    "x": round(rng.uniform(-0.05, 0.15), 3),
                    "y": round(rng.uniform(-0.02, 0.02), 3),
                    "z": round(0.98 + rng.uniform(-0.01, 0.01), 3),
                },
                "gyro_dps": {
                    "x": round(rng.uniform(-0.5, 0.5), 3),
                    "y": round(rng.uniform(-0.1, 0.1), 3),
                    "z": round((base_rpms[0] - base_rpms[1]) * 0.02 + rng.uniform(-0.2, 0.2), 3),
                },
            },
        },
        # IDUB-specific fields — RL agent telemetry
        "rl_agent": {
            "algorithm": "PPO+ICM",
            "policy": "NeuroC_v1",
            "mode": "sim_to_real",
            "training_step": training_step,
            "episode_elapsed_s": round(elapsed % 60, 2),
            "intrinsic_reward": intrinsic_r,
            "extrinsic_reward": extrinsic_r,
            "total_reward": total_r,
            "icm_prediction_error": icm_err,
            "policy_entropy": policy_entropy,
            "jerk_mps3": jerk_val,
            "sim_to_real_gap": gap_val,
            "curiosity_beta": beta,
            "platform": "Jetson Orin NX (synthetic)",
            "sim_source": "NVIDIA Isaac Sim (synthetic)",
        },
    }
    return payload


def start_idub_emulator():
    hz = float(os.getenv("EMULATOR_HZ", "10"))
    duration = float(os.getenv("EMULATOR_DURATION_S", "0"))
    if not math.isfinite(hz) or not 0 < hz <= 1000:
        raise ValueError("EMULATOR_HZ must be in (0, 1000]")

    rng = random.Random(int(os.getenv("EMULATOR_SEED", "99")))
    session_id = str(uuid.uuid4())
    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())

    producer = get_producer()
    started = deadline = time.monotonic()
    sequence = 0
    prev_rpms = None

    try:
        while not stop.is_set():
            elapsed = time.monotonic() - started
            if duration and elapsed >= duration:
                break
            dt = 1.0 / hz
            payload = make_idub_payload(sequence, elapsed, rng, session_id, prev_rpms, dt)
            prev_rpms = [payload["telemetry"]["motors"][m]["speed_rpm"] for m in MOTORS]
            send(producer, TELEMETRY_TOPIC, payload)
            sequence += 1
            if sequence % max(1, int(hz)) == 0:
                LOG.info(
                    "IDUB seq=%s step=%s intrinsic=%.3f gap=%.3f",
                    sequence,
                    payload["rl_agent"]["training_step"],
                    payload["rl_agent"]["intrinsic_reward"],
                    payload["rl_agent"]["sim_to_real_gap"],
                )
            deadline += 1 / hz
            deadline = max(deadline, time.monotonic())
            stop.wait(max(0, deadline - time.monotonic()))
    finally:
        producer.close(timeout=10)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    start_idub_emulator()
