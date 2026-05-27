"""""
import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer

# Konfiguracja Kafki
KAFKA_BROKER = 'kafka:9092'
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
        # 1. ZEGAR FAZOWY - zmiana trybu co 10 sekund
        current_time = int(time.time())
        cycle_phase = (current_time // 10) % 4 
        
        # Lekki szum dla realizmu (wykresy w Grafanie nie będą płaskie)
        noise = random.uniform(-2.0, 2.0)
        
        # 2. DEFINICJA TRYBÓW JAZDY OMNIWHEEL (MECANUM)
        if cycle_phase == 0:
            mode = "JAZDA W PRZÓD"
            fl_rpm, fr_rpm = 100.0, 100.0
            rl_rpm, rr_rpm = 100.0, 100.0
        
        elif cycle_phase == 1:
            mode = "STRAFE W PRAWO"
            # Znoszenie się sił pcha wózek w prawo
            fl_rpm, fr_rpm = 100.0, -100.0
            rl_rpm, rr_rpm = -100.0, 100.0
        
        elif cycle_phase == 2:
            mode = "OBRÓT W MIEJSCU"
            # Lewa strona w przód, prawa w tył
            fl_rpm, fr_rpm = 80.0, -80.0
            rl_rpm, rr_rpm = 80.0, -80.0
            
        elif cycle_phase == 3:
            mode = "STRAFE W LEWO"
            # Odwrotność fazy 1
            fl_rpm, fr_rpm = -100.0, 100.0
            rl_rpm, rr_rpm = 100.0, -100.0

        # Dodajemy szum do idealnych wartości
        current_fl = fl_rpm + noise
        current_fr = fr_rpm + noise
        current_rl = rl_rpm + noise
        current_rr = rr_rpm + noise

        # 3. BUDOWANIE PACZKI DANYCH
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
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
                }
            }
        }

        # 4. WYSYŁKA
        producer.send(TOPIC, payload)
        
        # Używamy end='\r', aby konsola nadpisywała tę samą linijkę, zamiast spamować 10 liniami na sekundę
        print(f"🔄 {mode:<16} | FL:{current_fl:>5.1f} FR:{current_fr:>6.1f} RL:{current_rl:>6.1f} RR:{current_rr:>6.1f}", end='\r', flush=True)
        
        time.sleep(0.1) # 10 Hz

if __name__ == "__main__":
    start_emulator

    """