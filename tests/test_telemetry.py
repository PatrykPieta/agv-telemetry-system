import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "edge-emulator"))
from main import make_payload
from telemetry import validate
from edge_processor import cluster_scan, polar_to_cartesian

class TelemetryTests(unittest.TestCase):
    def payload(self, elapsed=0, scenario="normal"):
        return make_payload(0, elapsed, random.Random(42), "test-session", scenario, 1750000000.0)

    def test_reproducible(self):
        self.assertEqual(self.payload(), self.payload())
        self.assertEqual(len(validate(self.payload())), 18)

    def test_fault_after_ten_seconds(self):
        self.assertFalse(self.payload(9, "overheat")["fault_active"])
        self.assertTrue(self.payload(10, "overheat")["fault_active"])
        self.assertGreater(self.payload(10, "overheat")["telemetry"]["motors"]["rear_right"]["temp_C"], 50)

    def test_invalid_values(self):
        for invalid in (float("nan"), float("inf"), "100", True, None):
            data = self.payload()
            data["telemetry"]["motors"]["front_left"]["speed_rpm"] = invalid
            with self.assertRaises(ValueError):
                validate(data)

    def test_invalid_envelope(self):
        for key, value in (("timestamp", -1), ("timestamp", 1750000000000),
                           ("schema_version", 2), ("sequence", -1), ("agv_id", ""), ("session_id", "")):
            data = self.payload()
            data[key] = value
            with self.assertRaises(ValueError):
                validate(data)

    def test_legacy_supported(self):
        data = self.payload()
        del data["schema_version"]
        self.assertEqual(len(validate(data)), 18)

    def test_lidar_empty_and_two_clusters(self):
        self.assertEqual(cluster_scan([]), [])
        points = [{"x": x + d, "y": 0, "quality": 20}
                  for x in (1.0, 2.0) for d in (0, 0.01, 0.02)]
        self.assertEqual(len(cluster_scan(points)), 2)
        x, y = polar_to_cartesian(90, 1000)
        self.assertAlmostEqual(x, 0)
        self.assertAlmostEqual(y, 1)

if __name__ == "__main__":
    unittest.main()
