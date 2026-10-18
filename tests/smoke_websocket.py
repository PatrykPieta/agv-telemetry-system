import asyncio
import json
import urllib.request
import urllib.error
from websockets.asyncio.client import connect

async def main():
    with urllib.request.urlopen("http://frontend:8000/health") as response:
        assert json.load(response)["kafka_connected"]
    for path in ("server.py", "requirements.txt", "Dockerfile"):
        try:
            urllib.request.urlopen("http://frontend:8000/" + path)
            raise AssertionError("Backend source exposed: " + path)
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
    async with connect("ws://frontend:8000/ws") as a, connect("ws://frontend:8000/ws") as b:
        for ws in (a, b):
            seen = set()
            for _ in range(100):
                packet = json.loads(await asyncio.wait_for(ws.recv(), 10))
                seen.add(packet["topic"])
                if {"telemetry_topic", "lidar_topic"} <= seen:
                    break
            assert {"telemetry_topic", "lidar_topic"} <= seen, seen
    print("PASS: backend readiness, two concurrent WebSocket clients, telemetry and LiDAR, source files hidden")

asyncio.run(main())
