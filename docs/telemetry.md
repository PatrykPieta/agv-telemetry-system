# Kontrakt telemetrii v1

Każda nowa wiadomość zawiera schema_version=1, agv_id, session_id (nowy UUID
na start procesu), sequence (od zera) i timestamp (Unix UTC w sekundach jako liczba).
Klucz wiadomości Kafka to agv_id. Wszystkie czasy wymagają synchronizacji zegarów.

telemetry.power_supply: bus_voltage_V [V], current_A [A].
telemetry.motors: front_left, front_right, rear_left, rear_right, każdy z
speed_rpm [obr/min ze znakiem] i temp_C [°C].
telemetry.imu: accel_g.{x,y,z} [g], gyro_dps.{x,y,z} [°/s].

Dozwolone są skończone liczby. Wymagane pola, typy i timestamp są walidowane.
Historyczne wiadomości bez schema_version są obsługiwane, o ile mają wymagane
pomiary oraz liczbowy czas Unix. Zmiana schematu wymaga jawnej migracji.

LiDAR korzysta z tej samej koperty i tablicy obstacles. frame_id=lidar:
X do przodu, Y w lewo, metry. Three.js: X do przodu, Z w prawo, Y w górę.
Pozycja i obrót modelu transformują przeszkody; skala graficzna modelu jest pomijana.
id przeszkody jest numerem klastra w jednym skanie, nie identyfikatorem śledzenia.
Brak przeszkód wysyła pustą tablicę.

Backend wysyła WebSocketem obiekt {topic, payload}. UI filtruje agv_id,
odrzuca dane starsze niż 2 s oraz starsze timestampy/numery sekwencji.
Po 2 s bez telemetrii zatrzymuje estymację ruchu i pokazuje brak aktualnych danych.
WebSocket wznawia połączenie z narastającym odstępem do 10 s.
Kolejka każdego klienta ma 100 wiadomości; przeciążony podgląd pomija najstarsze.
Historia pozostaje w bazie.

Ostrzeżenia Sparka zawierają timestamp pomiaru, agv_id, session_id, sequence,
motor.name, motor.temperature i ALERT_MSG. Temperatura ponad 50°C jest bazową regułą
dla wszystkich czterech silników, niezależnie od kierunku ruchu. Nie diagnozuje
zatarcia ani nie przewiduje awarii. Alarm w UI wygasa bez świeżych ostrzeżeń.
