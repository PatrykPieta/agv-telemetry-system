import os
import time
import json
import random
from kafka import KafkaProducer

# Konfiguracja Kafki
KAFKA_BROKER = os.getenv('KAFKA_SERVER', 'kafka:9092')
TOPIC = 'telemetry_topic'

def get_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ Połączono z Kafką! Rozpoczynamy taniec AGV (Napęd Omniwheel)...")
            return producer
        except Exception as e:
            print(f"⏳ Czekam na Kafkę... ({e})")
            time.sleep(5)

def start_emulator():
    producer = get_producer()
    
    while True:
        # ZEGAR FAZOWY
        current_time_sec = time.time()
        cycle_phase = (int(current_time_sec) // 10) % 4 
        noise = random.uniform(-2.0, 2.0)
        
        # DEFINICJA TRYBÓW
        if cycle_phase == 0:
            mode = "JAZDA W PRZÓD"
            fl_rpm, fr_rpm, rl_rpm, rr_rpm = 100.0, 100.0, 100.0, 100.0
        elif cycle_phase == 1:
            mode = "STRAFE W PRAWO"
            fl_rpm, fr_rpm, rl_rpm, rr_rpm = 100.0, -100.0, -100.0, 100.0
        elif cycle_phase == 2:
            mode = "OBRÓT W MIEJSCU"
            fl_rpm, fr_rpm, rl_rpm, rr_rpm = 80.0, -80.0, 80.0, -80.0
        elif cycle_phase == 3:
            mode = "STRAFE W LEWO"
            fl_rpm, fr_rpm, rl_rpm, rr_rpm = -100.0, 100.0, 100.0, -100.0

        current_fl = fl_rpm + noise
        current_fr = fr_rpm + noise
        current_rl = rl_rpm + noise
        current_rr = rr_rpm + noise

        # BUDOWANIE PACZKI DANYCH
        payload = {
            "timestamp": current_time_sec, # Zmiana z tekstu ISO na Unix Float! (Wymagane przez bazę)
            "agv_id": "AGV-01",
            "telemetry": {
                "power_supply": {
                    "bus_voltage_V": round(48.0 + random.uniform(-0.2, 0.2), 2),
                    "current_A": round(2.5 + random.uniform(-0.1, 0.5), 2)
                },
                "motors": {
                    "front_left": {"speed_rpm": round(current_fl, 1), "temp_C": 42.1},
                    "front_right": {"speed_rpm": round(current_fr, 1), "temp_C": 41.8},
                    "rear_left": {"speed_rpm": round(current_rl, 1), "temp_C": 43.0},
                    "rear_right": {"speed_rpm": round(current_rr, 1), "temp_C": 58.5}
                },
                "imu": {
                    "accel_g": {"x": 0.02, "y": -0.01, "z": 0.99},
                    "gyro_dps": {"x": 0.1, "y": 0.0, "z": round(12.5 + noise, 1)}
                },
                "edge_diagnostics": {
                    "cpu_temp_C": round(45.0 + random.uniform(-2.0, 2.0), 1)
                }
            }
        }

        producer.send(TOPIC, payload)
        
        print(f"🔄 {mode:<16} | FL:{current_fl:>5.1f} FR:{current_fr:>6.1f} RL:{current_rl:>6.1f} RR:{current_rr:>6.1f}", end='\r', flush=True)
        time.sleep(0.1)

if __name__ == "__main__":
    start_emulator() # <-- BŁĄD BYŁ TUTAJ (Brakowało nawiasów)