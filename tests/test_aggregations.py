"""Policy migration tests: run only in an explicitly selected disposable test DB."""
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "edge-emulator"))
from consumer import connect_db
from create_aggregations import create_aggregations


@unittest.skipUnless(os.getenv("AGV_POLICY_TEST") == "1", "Requires disposable DB and AGV_POLICY_TEST=1")
class AggregationTests(unittest.TestCase):
    def setUp(self):
        create_aggregations()
        self.conn = connect_db()
        self.conn.autocommit = True

    def tearDown(self):
        self.conn.close()

    def policies(self):
        with self.conn.cursor() as cur:
            cur.execute("""SELECT job_id, config FROM timescaledb_information.jobs
                WHERE proc_name='policy_refresh_continuous_aggregate' ORDER BY job_id""")
            return cur.fetchall()

    def test_repeated_initialization_preserves_policy(self):
        before = self.policies()
        create_aggregations()
        create_aggregations()
        self.assertEqual(self.policies(), before)
        self.assertEqual(len(before), 1)

    def test_missing_policy_is_created(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT remove_continuous_aggregate_policy('telemetry_agg_1m')")
        self.assertEqual(self.policies(), [])
        create_aggregations()
        after = self.policies()
        self.assertEqual(len(after), 1)
        self.assertIsNotNone(after[0][1]["start_offset"])

    def test_legacy_policy_and_data_are_preserved(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT remove_continuous_aggregate_policy('telemetry_agg_1m')")
            cur.execute("""SELECT add_continuous_aggregate_policy('telemetry_agg_1m',
                start_offset => NULL, end_offset => INTERVAL '1 minute',
                schedule_interval => INTERVAL '1 minute')""")
            cur.execute("INSERT INTO telemetry(time, agv_id) VALUES (now(), 'POLICY-TEST')")
            cur.execute("SELECT count(*) FROM telemetry WHERE agv_id='POLICY-TEST'")
            rows_before = cur.fetchone()[0]
        before = self.policies()
        self.assertIsNone(before[0][1]["start_offset"])
        create_aggregations()
        self.assertEqual(self.policies(), before)
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM telemetry WHERE agv_id='POLICY-TEST'")
            self.assertEqual(cur.fetchone()[0], rows_before)


if __name__ == "__main__":
    unittest.main()
