"""Idempotent database initialization, executed by Compose before the writer."""
from consumer import connect_db, init_db

def ensure_refresh_policy(cur):
    # Existing installations may use a different refresh window. Preserve it:
    # if_not_exists alone does not prevent overlapping-policy errors in TimescaleDB.
    cur.execute("""
        SELECT j.job_id
        FROM timescaledb_information.jobs j
        JOIN _timescaledb_catalog.continuous_agg ca
          ON j.config->>'mat_hypertable_id' = ca.mat_hypertable_id::text
        WHERE j.proc_name = 'policy_refresh_continuous_aggregate'
          AND ca.user_view_schema = 'public'
          AND ca.user_view_name = 'telemetry_agg_1m'
    """)
    existing = cur.fetchone()
    if existing:
        print(f"Preserving existing telemetry_agg_1m refresh policy (job {existing[0]}).", flush=True)
        return
    cur.execute("""
        SELECT add_continuous_aggregate_policy('public.telemetry_agg_1m',
            start_offset => INTERVAL '1 day', end_offset => INTERVAL '1 minute',
            schedule_interval => INTERVAL '1 minute', if_not_exists => TRUE)
    """)
    print("Created telemetry_agg_1m refresh policy.", flush=True)

def create_aggregations():
    conn = connect_db()
    try:
        init_db(conn)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_agg_1m
                WITH (timescaledb.continuous) AS
                SELECT time_bucket('1 minute', time) AS bucket, agv_id,
                    AVG(bus_voltage_v) AS avg_voltage, AVG(current_a) AS avg_current,
                    MAX(fl_temp_c) AS max_temp_fl, MAX(fr_temp_c) AS max_temp_fr,
                    MAX(rl_temp_c) AS max_temp_rl, MAX(rr_temp_c) AS max_temp_rr,
                    AVG(fl_rpm) AS avg_rpm_fl,
                    MAX(ABS(accel_z)) AS max_vibration_z
                FROM telemetry GROUP BY bucket, agv_id WITH NO DATA
            """)
            ensure_refresh_policy(cur)
    finally:
        conn.close()

if __name__ == "__main__":
    create_aggregations()
