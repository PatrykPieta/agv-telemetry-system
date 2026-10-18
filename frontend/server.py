"""One asynchronous Kafka subscription broadcasts to bounded WebSocket queues."""
import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent
clients = set()
broker_connected = False
TOPICS = [os.getenv("TELEMETRY_TOPIC", "telemetry_topic"), "alerts_topic",
          os.getenv("LIDAR_TOPIC", "lidar_topic")]

async def relay():
    global broker_connected
    while True:
        consumer = AIOKafkaConsumer(
            *TOPICS, bootstrap_servers=os.getenv("KAFKA_SERVER", "kafka:9092"),
            group_id=None, enable_auto_commit=False, auto_offset_reset="latest")
        try:
            await consumer.start()
            broker_connected = True
            while True:
                records = await consumer.getmany(timeout_ms=1000, max_records=500)
                for messages in records.values():
                    for message in messages:
                        try:
                            payload = json.loads(message.value)
                            if not isinstance(payload, dict):
                                continue
                            packet = json.dumps({"topic": message.topic, "payload": payload}, allow_nan=False)
                        except (ValueError, UnicodeError):
                            LOG.warning("Invalid JSON at %s:%s", message.topic, message.offset)
                            continue
                        for queue in tuple(clients):
                            if queue.full():
                                queue.get_nowait()
                            queue.put_nowait(packet)
        except asyncio.CancelledError:
            raise
        except Exception:
            LOG.exception("Kafka connection failed; retrying")
        finally:
            broker_connected = False
            await consumer.stop()
        await asyncio.sleep(3)

@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(relay())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def refresh_application_assets(request, call_next):
    response = await call_next(request)
    if request.url.path in ("/", "/styles.css", "/api/config") or request.url.path.startswith("/js/"):
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response

@app.get("/health")
async def health():
    return JSONResponse({"kafka_connected": broker_connected, "clients": len(clients)},
                        status_code=200 if broker_connected else 503)

@app.get("/api/config")
async def config():
    return {"agv_id": os.getenv("AGV_ID", "AGV-01"), "stale_ms": 2000}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue(maxsize=100)
    clients.add(queue)
    async def sender():
        while True:
            await asyncio.wait_for(websocket.send_text(await queue.get()), timeout=5)
    async def receiver():
        while True:
            await websocket.receive_text()
    tasks = [asyncio.create_task(sender()), asyncio.create_task(receiver())]
    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            task.result()
    except (WebSocketDisconnect, RuntimeError, asyncio.TimeoutError):
        pass
    finally:
        clients.discard(queue)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        with suppress(Exception):
            await websocket.close()

@app.get("/")
async def index():
    return FileResponse(ROOT / "index.html")

@app.get("/styles.css")
async def styles():
    return FileResponse(ROOT / "styles.css")

app.mount("/js", StaticFiles(directory=ROOT / "js"), name="js")
app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")