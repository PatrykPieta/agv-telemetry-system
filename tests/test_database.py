"""Run only against the isolated agv-check project; uses rollback for injected failures."""
import json
import random
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "edge-emulator"))
from kafka import TopicPartition
from consumer import connect_db, init_db, persist_batch
from main import make_payload

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.conn = connect_db()
        init_db(self.conn)
        with self.conn, self.conn.cursor() as cur:
            cur.execute("DELETE FROM telemetry WHERE agv_id='TEST-DB'")
            cur.execute("DELETE FROM ingested_messages WHERE topic='test-database'")
            cur.execute("DELETE FROM rejected_messages WHERE topic='test-database'")

    def tearDown(self):
        self.conn.close()

    def message(self, offset=0, raw=None):
        data = make_payload(offset, 0, random.Random(42), "test", timestamp=1750000000.0 + offset)
        data["agv_id"] = "TEST-DB"
        return SimpleNamespace(topic="test-database", partition=0, offset=offset,
                               value=raw if raw is not None else json.dumps(data).encode())

    def count(self, table):
        with self.conn, self.conn.cursor() as cur:
            if table == "telemetry":
                cur.execute("SELECT count(*) FROM telemetry WHERE agv_id='TEST-DB'")
            else:
                cur.execute("SELECT count(*) FROM " + table + " WHERE topic='test-database'")
            return cur.fetchone()[0]

    def test_replay_does_not_duplicate(self):
        batch = {TopicPartition("test-database", 0): [self.message()]}
        offsets = persist_batch(self.conn, batch)
        persist_batch(self.conn, batch)
        self.assertEqual(self.count("telemetry"), 1)
        self.assertEqual(next(iter(offsets.values())).offset, 1)

    def test_bad_message_does_not_block_valid(self):
        batch = {TopicPartition("test-database", 0): [self.message(0, b"bad JSON"), self.message(1)]}
        persist_batch(self.conn, batch)
        persist_batch(self.conn, batch)
        self.assertEqual(self.count("telemetry"), 1)
        self.assertEqual(self.count("rejected_messages"), 1)

    def test_transaction_rolls_back_whole_batch(self):
        from unittest.mock import patch
        import consumer
        batch = {TopicPartition("test-database", 0): [self.message(0), self.message(1)]}
        real_validate = consumer.validate
        calls = 0
        def fail_second(data):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("injected write failure")
            return real_validate(data)
        with patch("consumer.validate", side_effect=fail_second):
            with self.assertRaises(RuntimeError):
                persist_batch(self.conn, batch)
        self.assertEqual(self.count("telemetry"), 0)
        self.assertEqual(self.count("ingested_messages"), 0)
        persist_batch(self.conn, batch)
        self.assertEqual(self.count("telemetry"), 2)

if __name__ == "__main__":
    unittest.main()
