import psycopg2
import time

# Konfiguracja bazy danych
DB_HOST = "timescaledb"
DB_PORT = "5432"
DB_NAME = "agv_db"
DB_USER = "admin"
DB_PASS = "password"

def create_aggregations():
    print("⏳ Łączenie z bazą danych w celu utworzenia agregacji Power BI...")
    
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        conn.autocommit = True
        cursor = conn.cursor()

        # 1. Tworzenie zmaterializowanego widoku (Ciągła Agregacja)
        print("🏗️ Tworzenie tabeli agregacyjnej 'telemetry_agg_1m'...")
        cursor.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_agg_1m
            WITH (timescaledb.continuous) AS
            SELECT
                time_bucket('1 minute', time) AS bucket,
                agv_id,
                AVG(bus_voltage_v) AS avg_voltage,
                AVG(current_a) AS avg_current,
                MAX(fl_temp_c) AS max_temp_fl,
                MAX(fr_temp_c) AS max_temp_fr,
                MAX(rl_temp_c) AS max_temp_rl,
                MAX(rr_temp_c) AS max_temp_rr,
                AVG(fl_rpm) AS avg_rpm_fl,
                MAX(ABS(accel_z)) AS max_vibration_z
            FROM telemetry
            GROUP BY bucket, agv_id;
        """)

        # 2. Uruchomienie "robota" w bazie danych, który będzie odświeżał dane co minutę
        print("⚙️ Konfiguracja automatycznego odświeżania w tle...")
        try:
            cursor.execute("""
                SELECT add_continuous_aggregate_policy('telemetry_agg_1m',
                    start_offset => NULL,
                    end_offset => INTERVAL '1 minute',
                    schedule_interval => INTERVAL '1 minute');
            """)
            print("✅ Polityka odświeżania dodana pomyślnie!")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️ Polityka odświeżania już istnieje, pomijam.")
            else:
                print(f"⚠️ Uwaga przy tworzeniu polityki (możliwe, że już istnieje): {e}")

        cursor.close()
        conn.close()
        print("🚀 Gotowe! Baza danych jest teraz przygotowana na audyt Power BI.")

    except Exception as e:
        print(f"❌ Błąd podczas konfiguracji bazy danych: {e}")

if __name__ == "__main__":
    create_aggregations()