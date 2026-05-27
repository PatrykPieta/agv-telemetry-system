import math
import time
import json
import numpy as np
from datetime import datetime
from sklearn.cluster import DBSCAN
from kafka import KafkaProducer

# =========================================================
# WERSJA DLA EMULATORA (Do testów na laptopie)
from mock_lidar import MockRPLidar as RPLidar

# WERSJA DOCELOWA (Odkomentuj na fizycznym Raspberry Pi)
# from rplidar import RPLidar
# =========================================================

# DOBRZE:
KAFKA_BROKER = 'kafka:9092' # tu bedzie ip jak pdolacze raspberry
KAFKA_TOPIC = 'lidar_topic'
AGV_ID = "AGV-01"

# Parametry DBSCAN
EPSILON_M = 0.2    # Maksymalna odległość między punktami w klastrze (20 cm)
MIN_SAMPLES = 3    # Minimum punktów, by uznać coś za obiekt, a nie szum

def get_producer():
    while True:
        try:
            return KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception:
            print("Czekam na Kafkę...")
            time.sleep(3)

def polar_to_cartesian(angle_deg, distance_mm):
    """Zmienia Kąt i Dystans na szkolne X i Y (w metrach)."""
    dist_m = distance_mm / 1000.0
    angle_rad = math.radians(angle_deg)
    # Dla AGV często X to przód, Y to bok
    x = dist_m * math.cos(angle_rad)
    y = dist_m * math.sin(angle_rad)
    return x, y

def run_lidar_edge_node():
    producer = get_producer()
    lidar = RPLidar('/dev/ttyUSB0')
    lidar.connect()
    
    print("🚀 Mózg AGV (DBSCAN) uruchomiony. Nasłuchuję skanera...")
    
    scan_points = []
    
    # iter_measurments wypluwa pojedyncze strzały z lasera
    for new_scan, quality, angle, distance in lidar.iter_measurments():
        
        # Jeśli to nowy obrót, analizujemy poprzedni zebrany zestaw punktów
        if new_scan and len(scan_points) > 0:
            start_time = time.time()
            
            # Krok 1: Ekstrakcja tylko wsp. X, Y do tablicy NumPy dla DBSCAN
            xy_points = np.array([[p['x'], p['y']] for p in scan_points])
            
            obstacles = []
            
            # Uruchamiamy AI tylko, gdy mamy jakiekolwiek punkty blisko nas
            if len(xy_points) > 0:
                # Krok 2: Magia DBSCAN
                db = DBSCAN(eps=EPSILON_M, min_samples=MIN_SAMPLES).fit(xy_points)
                labels = db.labels_ # Tablica etykiet (np. 0, 0, 1, 1, -1) -1 to szum!
                
                # Krok 3: Wyciąganie klastrów
                unique_labels = set(labels)
                for label in unique_labels:
                    if label == -1:
                        continue # Ignorujemy szum (śmieci lasera)
                        
                    # Wyciągamy punkty z konkretnego obiektu
                    class_member_mask = (labels == label)
                    cluster_xy = xy_points[class_member_mask]
                    
                    # Liczymy środek ciężkości obiektu (średnia z X i Y)
                    center_x = round(float(np.mean(cluster_xy[:, 0])), 3)
                    center_y = round(float(np.mean(cluster_xy[:, 1])), 3)
                    
                    # Przybliżony rozmiar przeszkody (największy odstęp między punktami)
                    size = round(float(np.ptp(cluster_xy[:, 0]) + np.ptp(cluster_xy[:, 1])) / 2, 3)
                    
                    # Uśrednione odbicie (quality)
                    cluster_points = [scan_points[i] for i, mask in enumerate(class_member_mask) if mask]
                    avg_ref = int(sum(p['quality'] for p in cluster_points) / len(cluster_points))
                    
                    obstacles.append({
                        "id": int(label),
                        "center_x_m": center_x,
                        "center_y_m": center_y,
                        "size_m": max(size, 0.05), # min 5 cm, żeby w Three.js było to widać
                        "avg_reflectivity": avg_ref
                    })
            
            # Krok 4: Wysłanie na Kafkę zgrabnej paczki
            payload = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "agv_id": AGV_ID,
                "obstacles": obstacles
            }
            producer.send(KAFKA_TOPIC, payload)
            
            # Czyszczenie bufora na nowy obrót 360
            scan_points = [] 
            
            calc_time = round((time.time() - start_time) * 1000, 2)
            print(f"📡 Przetworzono skan w {calc_time} ms. Wykryto {len(obstacles)} obiektów.", end='\r')

        # === PROCES ZBIERANIA DANYCH (Filtrowanie w locie) ===
        # Zbieramy punkty tylko do 3 metrów, odrzucamy błędne (distance == 0)
        if distance > 0 and distance <= 3000:
            x, y = polar_to_cartesian(angle, distance)
            scan_points.append({
                'x': x, 'y': y, 'quality': quality
            })

if __name__ == '__main__':
    run_lidar_edge_node()