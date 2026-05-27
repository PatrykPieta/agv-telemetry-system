import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from kafka import KafkaConsumer

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 Przeglądarka podłączona!", flush=True)
    
    try:
        # Konfiguracja bez wymuszania tematów z góry
        consumer = KafkaConsumer(
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda x: x.decode('utf-8', errors='ignore'),
            auto_offset_reset='latest'
        )
        
        # Elastyczna subskrypcja (nie blokuje się na brakujących tematach)
        consumer.subscribe(topics=['telemetry_topic', 'alerts_topic'])
        print("🎧 Nasłuchuję Kafki (Telemetria + Alarmy)...", flush=True)
        
        while True:
            records = consumer.poll(timeout_ms=100)
            if records:
                print(f"📦 Serwer odebrał paczkę z Kafki! Przelewam do przeglądarki...", flush=True)
            
            for tp, messages in records.items():
                for message in messages:
                    await websocket.send_text(message.value)
                    
            await asyncio.sleep(0.01)
            
    except WebSocketDisconnect:
        print("🔴 Przeglądarka się rozłączyła.", flush=True)
    except Exception as e:
        print(f"❌ Błąd serwera: {e}", flush=True)
    finally:
        if 'consumer' in locals():
            consumer.close()

app.mount("/", StaticFiles(directory=".", html=True), name="static")