import os
import json
import time
import psycopg2
import psycopg2.extras  # <-- DODANO DO BULK INSERT
from kafka import KafkaConsumer

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
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
        cursor.execute("SELECT create_hypertable('telemetry', 'time', if_not_exists => TRUE);")
    except Exception:
        pass 
    cursor.close()

def start_consumer():
    print("Konsument startuje. Czekam 15s na usługi...")
    time.sleep(15)
    
    conn = connect_db()
    init_db(conn)
    print("Połączono z TimescaleDB i zainicjalizowano nową tabelę!")

    # ZMIANA 1: enable_auto_commit=False (Zabezpiecza przed utratą danych)
    consumer = KafkaConsumer(
        'telemetry_topic',
        bootstrap_servers=['kafka:9092'],
        group_id='agv_db_writers',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        enable_auto_commit=False
    )

    cursor = conn.cursor()
    print("Odbieranie danych z Kafki i ZAPIS HURTOWY do bazy...")

    # ZMIANA 2: Konfiguracja bufora
    BATCH_SIZE = 200
    buffer = []

    while True:
        # Odpytanie Kafki (pobiera dostępne wiadomości, czeka max 0.5s)
        records = consumer.poll(timeout_ms=500)

        for tp, messages in records.items():
            for message in messages:
                data = message.value
                try:
                    t_stamp = data['timestamp']
                    agv_id = data['agv_id']
                    
                    volts = data['telemetry']['power_supply']['bus_voltage_V']
                    amps = data['telemetry']['power_supply']['current_A']
                    
                    m = data['telemetry']['motors']
                    fl_rpm, fl_temp = m['front_left']['speed_rpm'], m['front_left']['temp_C']
                    fr_rpm, fr_temp = m['front_right']['speed_rpm'], m['front_right']['temp_C']
                    rl_rpm, rl_temp = m['rear_left']['speed_rpm'], m['rear_left']['temp_C']
                    rr_rpm, rr_temp = m['rear_right']['speed_rpm'], m['rear_right']['temp_C']
                    
                    imu = data['telemetry']['imu']
                    ax, ay, az = imu['accel_g']['x'], imu['accel_g']['y'], imu['accel_g']['z']
                    gx, gy, gz = imu['gyro_dps']['x'], imu['gyro_dps']['y'], imu['gyro_dps']['z']

                    # Dodanie do bufora zamiast bezpośredniego zapisu
                    buffer.append((
                        t_stamp, agv_id, volts, amps,
                        fl_rpm, fl_temp, fr_rpm, fr_temp,
                        rl_rpm, rl_temp, rr_rpm, rr_temp,
                        ax, ay, az, gx, gy, gz
                    ))
                except KeyError as e:
                    print(f"Pominięto starą paczkę. Brak klucza: {e}")

        # ZMIANA 3: Hurtowy zrzut do bazy (Bulk Insert)
        if len(buffer) >= BATCH_SIZE or (len(buffer) > 0 and not records):
            try:
                query = """
                    INSERT INTO telemetry (
                        time, agv_id, bus_voltage_v, current_a,
                        fl_rpm, fl_temp_c, fr_rpm, fr_temp_c,
                        rl_rpm, rl_temp_c, rr_rpm, rr_temp_c,
                        accel_x, accel_y, accel_z,
                        gyro_x, gyro_y, gyro_z
                    ) VALUES %s
                """
                template = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                
                # Szybki zapis paczki
                psycopg2.extras.execute_values(cursor, query, buffer, template=template)
                
                # Powiadomienie Kafki o sukcesie
                consumer.commit()
                buffer.clear()
            except Exception as e:
                print(f"Krytyczny błąd zapisu: {e}")
                buffer.clear()

if __name__ == "__main__":
    start_consumer()