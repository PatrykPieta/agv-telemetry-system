import os
import json
import time
import psycopg2
from kafka import KafkaConsumer

# Konfiguracja bazy danych (zgodna z Twoim docker-compose.yaml)
DB_HOST = "timescaledb"
DB_PORT = "5432"
DB_NAME = "agv_db"
DB_USER = "admin"
DB_PASS = "password"

def connect_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            conn.autocommit = True
            return conn
        except Exception as e:
            print(f"Czekam na bazę danych... {e}")
            time.sleep(5)

def init_db(conn):
    cursor = conn.cursor()
    # Kasujemy starą tabelę i robimy nową, pod nasz nowy przemysłowy JSON
    cursor.execute("""
        DROP TABLE IF EXISTS telemetry CASCADE;
        
        CREATE TABLE telemetry (
            time TIMESTAMPTZ NOT NULL,
            agv_id TEXT,
            bus_voltage_v DOUBLE PRECISION,
            current_a DOUBLE PRECISION,
            fl_rpm DOUBLE PRECISION, fl_temp_c DOUBLE PRECISION,
            fr_rpm DOUBLE PRECISION, fr_temp_c DOUBLE PRECISION,
            rl_rpm DOUBLE PRECISION, rl_temp_c DOUBLE PRECISION,
            rr_rpm DOUBLE PRECISION, rr_temp_c DOUBLE PRECISION,
            accel_x DOUBLE PRECISION, accel_y DOUBLE PRECISION, accel_z DOUBLE PRECISION,
            gyro_x DOUBLE PRECISION, gyro_y DOUBLE PRECISION, gyro_z DOUBLE PRECISION
        );
    """)
    try:
        # Tworzenie hiper-tabeli dla wydajności TimescaleDB
        cursor.execute("SELECT create_hypertable('telemetry', 'time');")
    except Exception:
        pass # Ignorujemy błąd, jeśli już jest hiper-tabelą
    cursor.close()

def start_consumer():
    print("Konsument startuje. Czekam 15s na usługi...")
    time.sleep(15)
    
    conn = connect_db()
    init_db(conn)
    print("Połączono z TimescaleDB i zainicjalizowano nową tabelę!")

    consumer = KafkaConsumer(
        'telemetry_topic',
        bootstrap_servers=['10.10.133.187:9092'],
        group_id='agv_db_writers',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    cursor = conn.cursor()
    print("Odbieranie poszerzonego kontraktu z Kafki i zapis do bazy...")

    for message in consumer:
        data = message.value
        try:
            # Nawigacja po nowej ścieżce JSON (rozwiązuje KeyError)
            t_stamp = data['timestamp']
            agv_id = data['agv_id']
            
            # Zasilanie
            volts = data['telemetry']['power_supply']['bus_voltage_V']
            amps = data['telemetry']['power_supply']['current_A']
            
            # Silniki
            m = data['telemetry']['motors']
            fl_rpm, fl_temp = m['front_left']['speed_rpm'], m['front_left']['temp_C']
            fr_rpm, fr_temp = m['front_right']['speed_rpm'], m['front_right']['temp_C']
            rl_rpm, rl_temp = m['rear_left']['speed_rpm'], m['rear_left']['temp_C']
            rr_rpm, rr_temp = m['rear_right']['speed_rpm'], m['rear_right']['temp_C']
            
            # IMU
            imu = data['telemetry']['imu']
            ax, ay, az = imu['accel_g']['x'], imu['accel_g']['y'], imu['accel_g']['z']
            gx, gy, gz = imu['gyro_dps']['x'], imu['gyro_dps']['y'], imu['gyro_dps']['z']

            # Zapis do nowej tabeli
            cursor.execute("""
                INSERT INTO telemetry (
                    time, agv_id, bus_voltage_v, current_a,
                    fl_rpm, fl_temp_c, fr_rpm, fr_temp_c,
                    rl_rpm, rl_temp_c, rr_rpm, rr_temp_c,
                    accel_x, accel_y, accel_z,
                    gyro_x, gyro_y, gyro_z
                ) VALUES (
                    to_timestamp(%s), %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
            """, (
                t_stamp, agv_id, volts, amps,
                fl_rpm, fl_temp, fr_rpm, fr_temp,
                rl_rpm, rl_temp, rr_rpm, rr_temp,
                ax, ay, az, gx, gy, gz
            ))
            
        except KeyError as e:
            # Zabezpieczenie na wypadek, gdyby Kafka wypluła jakąś resztkę starych danych
            print(f"Pominięto starą paczkę. Brak klucza: {e}")

if __name__ == "__main__":
    start_consumer()