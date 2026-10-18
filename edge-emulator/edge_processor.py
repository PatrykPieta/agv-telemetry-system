"""Mock LiDAR edge node: distance filtering and DBSCAN per scan."""
import math
import os
import signal
import time
import uuid
import numpy as np
from sklearn.cluster import DBSCAN
from mock_lidar import MockRPLidar
from config import AGV_ID, LIDAR_TOPIC
from transport import get_producer, send

def polar_to_cartesian(angle_deg, distance_mm):
    angle = math.radians(angle_deg)
    return distance_mm / 1000 * math.cos(angle), distance_mm / 1000 * math.sin(angle)

def cluster_scan(points):
    if not points:
        return []
    xy = np.array([[p["x"], p["y"]] for p in points])
    labels = DBSCAN(eps=float(os.getenv("LIDAR_EPS_M", "0.2")),
                    min_samples=int(os.getenv("LIDAR_MIN_SAMPLES", "3"))).fit(xy).labels_
    obstacles = []
    for label in sorted(set(labels) - {-1}):
        mask = labels == label
        cluster = xy[mask]
        obstacles.append({
            "id": int(label),  # Scan-local label, not a persistent tracking ID.
            "center_x_m": round(float(cluster[:, 0].mean()), 3),
            "center_y_m": round(float(cluster[:, 1].mean()), 3),
            "size_m": max(round(float(np.linalg.norm(np.ptp(cluster, axis=0))), 3), 0.05),
            "avg_reflectivity": int(np.mean([p["quality"] for p, keep in zip(points, mask) if keep])),
        })
    return obstacles

def run_lidar_edge_node():
    producer = get_producer()
    lidar = MockRPLidar()
    session = str(uuid.uuid4())
    points, sequence, scan_started = [], 0, None
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        lidar.connect()
        for new_scan, quality, angle, distance in lidar.iter_measurments():
            if new_scan:
                if scan_started is not None:
                    send(producer, LIDAR_TOPIC, {
                        "schema_version": 1, "agv_id": AGV_ID, "session_id": session,
                        "sequence": sequence, "timestamp": scan_started, "frame_id": "lidar",
                        "source": "emulator", "obstacles": cluster_scan(points),
                    })
                    sequence += 1
                points, scan_started = [], time.time()
            if 0 < distance <= 3000 and quality > 0:
                x, y = polar_to_cartesian(angle, distance)
                points.append({"x": x, "y": y, "quality": quality})
    except KeyboardInterrupt:
        pass
    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        producer.close(timeout=10)

if __name__ == "__main__":
    run_lidar_edge_node()
