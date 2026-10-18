# Przewodnik po zmianach projektu AGV

Stan: 2026-10-13. Punktem odniesienia jest poprzednia wersja zapisana w Git
(HEAD 5fd763c). Zmiany pozostają lokalne na codex/uporzadkowanie-projektu.

## 1. Co nadal jest tym samym systemem

Nie zmienił się główny przepływ:
emulator / Raspberry Pi -> Kafka -> baza, Spark oraz backend -> przeglądarka.
TimescaleDB przechowuje historię, Grafana pokazuje wykresy, Three.js pokazuje model.
Panel Windows steruje kontenerami; nie wykonuje obliczeń telemetrycznych.

## 2. Błąd uruchomienia i poprawka z 13 października

Log db-init:
refresh interval overlaps with an existing continuous aggregate policy on "telemetry_agg_1m".

W istniejącej bazie działa już zadanie 1002:
start_offset=null (bez dolnej granicy), end_offset=1 minuta.
Nowy skrypt próbował dodać politykę z start_offset=1 dzień.
if_not_exists nie zapobiegło konfliktowi tych zakresów.

create_aggregations.py sprawdza teraz, czy widok ma politykę odświeżania.
Jeżeli ma, pozostawia jej identyfikator i konfigurację. Jeżeli nie, dodaje nową.
Nie usuwa widoku, tabel ani istniejącej polityki. Inne błędy nadal przerywają start.
Dodano tests/test_aggregations.py i włączono go do scripts/test.ps1.

Poprawka została sprawdzona na istniejącej bazie oraz na osobnej tymczasowej bazie.
Baza testowa obejmowała: stary harmonogram, brak harmonogramu i wielokrotny start.
Wcześniejsze testy z 11 października obejmowały bazę utworzoną przez nowy skrypt,
więc nie wykryły konfliktu ze starym harmonogramem.

## 3. Jak teraz wygląda uruchomienie

AGV.cmd -> scripts/panel.ps1 -> start.ps1 -> Docker Compose.

Compose uruchamia infrastrukturę. Kafka przechodzi kontrolę gotowości, następnie
kafka-init zakłada telemetry_topic, lidar_topic i alerts_topic.
PostgreSQL przechodzi kontrolę gotowości, następnie db-init tworzy brakujące
struktury i sprawdza agregacje. Dopiero sukces db-init odblokowuje zapis oraz Grafanę.
Frontend, Spark i emulator zależą od inicjalizacji Kafki, dlatego mogą działać
nawet przy nieudanym db-init. To wyjaśnia częściowy start widoczny na zrzucie.

db-init i kafka-init są jednorazowe: Exited (0) oznacza prawidłowe zakończenie.
Exited (1) oznacza błąd. Running/healthy dotyczy usług działających stale.

| Plik | Wcześniej | Teraz |
|---|---|---|
| AGV.cmd (nowy) | Brak | Otwiera panel Windows dwuklikiem. |
| scripts/panel.ps1 (nowy) | Brak | Przyciski start/stop, stan, logi, wizualizacja, wykresy i konfiguracja; operacje w tle. |
| start.ps1 | Stałe pauzy i automatyczne otwieranie wielu stron | Kontrola błędów, oczekiwanie na gotowość, wybór Local/Remote, LiDAR i narzędzi. |
| docker-compose.yaml | Wszystkie moduły startowały razem | Kolejność inicjalizacji, kontrole gotowości, profile opcjonalnych źródeł/narzędzi i trwałe dane. |

Panel nie uruchamia automatycznie Docker Desktop. Konfiguracja otwiera .env
w Notatniku. Zamknięcie panelu pozostawia kontenery uruchomione.
Zatrzymaj zatrzymuje kontenery i zachowuje wolumeny.

## 4. Profile i sieć

- simulation: lokalny emulator telemetrii.
- lidar: lokalny emulator LiDAR z DBSCAN.
- tools: Kafka UI i Adminer.
- Bez profili: centralna infrastruktura, zapis, backend, Spark i Grafana.
- Local w panelu włącza simulation.
- Remote wyłącza poprzedni lokalny emulator telemetrii; dane ma dostarczać Pi.
- Opcja LiDAR jest osobna od Local/Remote.

Adres kafka:9092 służy procesom wewnątrz sieci Docker.
Adres KOMPUTER:29092 służy Raspberry Pi.
Usunięto publikację portu 9092 na hoście; wewnętrzny port nadal działa.
KAFKA_EXTERNAL_HOST zastępuje wpisany wcześniej na sztywno adres IP.
PostgreSQL, Spark UI, Kafka UI i Adminer są publikowane lokalnie.
Frontend i Grafana pozostają dostępne przez porty 8000 i 3000.

PGAdmin usunięto z Compose, pozostawiono Adminer jako opcjonalne narzędzie.
Nie migrowano ustawień PGAdmin. Narzędzia administracyjne nie są wymagane
do działania systemu.

Kod frontend/Spark nie jest już montowany z katalogów hosta w trybie bieżącego
uruchomienia. Jest kopiowany podczas budowania obrazów. Po edycji trzeba
przebudować obraz; przycisk Uruchom wykonuje --build.

## 5. Konfiguracja i wiadomości

| Plik | Rola |
|---|---|
| .env.example (nowy) | Wzór ustawień: host Kafki, AGV_ID, baza, częstotliwość, scenariusz, ziarno i czas emulatora. |
| edge-emulator/config.py (nowy) | Czytanie konfiguracji przez procesy Python zamiast powtarzania stałych. |
| edge-emulator/telemetry.py (nowy) | Lista silników i walidacja wymaganych pól, jednostek oraz liczb. |
| edge-emulator/transport.py (nowy) | Wspólny producent Kafka: klucz agv_id, potwierdzenia brokera i ponawianie dostarczenia. |
| docs/telemetry.md (nowy) | Opis formatu wiadomości, jednostek i układów współrzędnych. |

Dotychczasowe telemetry.power_supply, motors i imu pozostają.
Dodano schema_version, session_id i sequence. timestamp to Unix UTC w sekundach.
Stare wiadomości bez schema_version są akceptowane, jeśli mają wymagane pola.
LiDAR także przeszedł z czasu ISO na liczbowy czas Unix.

.env nie jest wysyłany do Git; .env.example jest wzorem do repozytorium.
Zmiana hasła w .env nie zmienia hasła istniejącej bazy.

## 6. Emulator i LiDAR

| Plik | Zmiana |
|---|---|
| edge-emulator/main.py | Rozdzielono generowanie próbki i pętlę wysyłki. Parametry z konfiguracji, ziarno losowania, czas sesji, licznik próbek i scenariusz overheat od 10. sekundy. Wysyłka czeka na potwierdzenie. |
| edge-emulator/edge_processor.py | Oddzielna funkcja cluster_scan, wspólny transport/config, puste skany także publikowane, numery skanów, frame_id i sprzątanie zasobów. Rozmiar klastra to przekątna jego zakresu XY. |
| edge-emulator/mock_lidar.py | Bez zmian; nadal symulacja sensora. |

W emulatorze wszystkie nominalne temperatury wynoszą teraz 42°C.
Zrezygnowano z poprzedniej sztucznej zmiennej prędkości żyroskopu; gyro ma zera.
Poprzednie pole edge_diagnostics.cpu_temp_C nie jest teraz generowane.
IMU pozostaje zaślepką i nie odzwierciedla dynamiki ruchu.
Nie dodano obsługi rzeczywistego LiDAR ani czujników AGV.

## 7. Baza

| Plik | Wcześniej | Teraz |
|---|---|---|
| edge-emulator/consumer.py | Bufor 200 rekordów, czyszczenie także po błędzie | Zapis każdej pobranej paczki w transakcji; offsety zatwierdzane dopiero po zapisie. |
| edge-emulator/create_aggregations.py | Ręczny skrypt agregacji | Automatyczny etap db-init, z zachowaniem już istniejącej polityki. |
| edge-emulator/health.py (nowy) | Brak | Kontrola aktualności sygnału działania konsumenta. |

Tabele:
- telemetry: te same kolumny pomiarowe; dodany indeks AGV/czas.
- ingested_messages: topic/partycja/offset, czas zapisu, pełny JSON.
  Zapobiega ponownemu zapisowi tego samego offsetu.
- rejected_messages: surowa błędna wiadomość i powód odrzucenia.
- telemetry_agg_1m: agregacja minutowa, zachowana nazwa i kolumny.

Awaria transakcji wycofuje całą paczkę; restart może ją bezpiecznie odczytać ponownie.
To nie usuwa kopii opublikowanych jako nowe offsety.
Archiwum nie ma jeszcze retencji i zajmuje dodatkowe miejsce.
max_vibration_z nadal zawiera grawitację, więc nie jest zweryfikowaną miarą drgań.

## 8. Backend i przeglądarka

| Plik | Zmiana |
|---|---|
| frontend/server.py | Jeden asynchroniczny konsument Kafka zamiast blokującego konsumenta dla każdej przeglądarki. Osobne ograniczone kolejki klientów; /health i /api/config. Statycznie udostępnia tylko pliki UI. Dodana rewalidacja cache. |
| frontend/js/network.js | Odbiera {topic,payload}, filtruje AGV i świeżość, wznawia WebSocket, odrzuca stare próbki. Po 2 s braku danych zeruje RPM stanu i ukrywa stare wartości oraz przeszkody. |
| frontend/js/physics.js | Używa rzeczywistego dt; ruch i obrót mają jednostki czasowe. Zatrzymuje ruch dla starych danych. Usunięto sztuczne zatrzymywanie na granicy hali. |
| frontend/js/main.js | Oblicza dt, przekazuje go do kinematyki, ogranicza rozdzielczość renderowania, pokazuje błąd modelu, usuwa część debugowania i odświeża importy modułów. |
| frontend/js/gui.js | Ustawienia sceny są domyślnie ukryte, otwierane przyciskiem. |
| frontend/index.html | Status/ostrzeżenie i przycisk ustawień; dokładniejszy opis RPM. Iframe Grafany używa hosta strony, nowego UID i AGV_ID. |
| frontend/styles.css | Ustawienia sceny przeniesione w lewy dolny róg; ograniczony rozmiar i przewijanie. |
| frontend/package.json (nowy) | Tryb modułów ES dla lokalnych testów Node. Nie wprowadza osobnego serwera Node. |

Alarm nie maluje już trwale całego modelu na czerwono; jest świeżym komunikatem
tekstowym. Przeszkody uwzględniają pozycję i obrót modelu. Wcześniejsze kolorowanie
według reflectivity uproszczono; pole nadal jest przesyłane.
Przeglądarka pokazuje jeden AGV_ID. Każda nadal szacuje pozycję od własnego startu;
nie wdrożono jeszcze wspólnej odometrii. Geometria i osie kół wymagają kalibracji.

## 9. Spark i Grafana

| Plik | Zmiana |
|---|---|
| spark-analytics/analytics.py | Ostrzeżenia temperatury dla 4 silników, poprawny typ czasu i konfigurowalny broker. Usunięto nieuzasadnione rozpoznawanie zatarcia po temperaturze/RPM. Checkpoint jest trwały. |
| infra/grafana/provisioning/datasources/agv.yaml (nowy) | Automatycznie dodaje źródło PostgreSQL/TimescaleDB. |
| infra/grafana/provisioning/dashboards/agv.yaml (nowy) | Wskazuje katalog dashboardów. |
| infra/grafana/dashboards/agv.json (nowy) | Dashboard agv-system: RPM, temperatury, napięcie/prąd, wybór AGV. |

Istniejące dashboardy Grafany pozostają w wolumenie.
Strona pokazuje teraz nowy dashboard agv-system zamiast starego advbjcq.
Nowa reguła temperatury jest demonstracyjną diagnostyką progową, nie ML.
Spark nadal może pobierać konektor przy pierwszym starcie; ma teraz trwały cache.

## 10. Testy, zależności i porządek

| Plik | Rola |
|---|---|
| tests/test_telemetry.py | Format danych, ziarno generatora, scenariusz usterki i DBSCAN. |
| tests/test_database.py | Transakcje, błędne wiadomości i ponowny odczyt offsetów. |
| tests/test_aggregations.py | Nowy test konfliktu starej polityki i wielokrotnej inicjalizacji. |
| tests/physics.test.mjs | Jednostki, niezależność od FPS i zatrzymanie nieaktualnego modelu. |
| tests/smoke_pipeline.py | 50 wiadomości przez Kafkę do bazy i ostrzeżenia Sparka dla 4 silników. |
| tests/smoke_websocket.py | Dwóch klientów, telemetria/LiDAR, gotowość i brak ekspozycji kodu serwera. |
| scripts/test.ps1 | Uruchamia odrębny projekt testowy agv-check; wymaga wolnych portów. |
| MonitorLag.ps1 | Sumuje zaległości partycji, używa UTC; niedostępność oznacza unavailable. To liczba wiadomości, nie milisekundy. |
| edge-emulator/requirements.txt | Przypięte bezpośrednie wersje bibliotek. |
| frontend/requirements.txt | Przypięte bezpośrednie wersje, usunięty nieużywany kafka-python. |
| .dockerignore w trzech modułach | Pomija cache i środowiska lokalne przy budowaniu. |
| .gitignore | Pomija .vs, venv i wyniki testów. |
| .gitattributes (nowy) | Zasady końców linii i traktowanie modelu GLB jako binarnego. |
| README.md (nowy) | Instrukcja startu, konfiguracji, testów, Pi i ograniczeń. |
| docs/verification.md (nowy) | Co rzeczywiście sprawdzono i czego jeszcze nie sprawdzono. |
| docs/changes-walkthrough.md (nowy) | Ten przewodnik. |

.vs i frontend/__pycache__ usunięto ze śledzenia Git, zachowując lokalne pliki.
Obrazy TimescaleDB/Grafany/narzędzi przypięto do konkretnych digestów.
Dockerfiles, spark-analytics/requirements.txt, loader.js, environment.js i model
agv.glb nie były modyfikowane w tym pakiecie zmian.

docs/agenda_pracy_inzynierskiej.tex jest obecnie w katalogu, ale nie powstał
w opisywanym pakiecie poprawek i nie był zmieniany przy diagnozie tego błędu.

## 11. Co zrobić jako użytkownik

1. Uruchomić Docker Desktop.
2. Otworzyć AGV.cmd.
3. Do lokalnej pracy wybrać Emulator na komputerze.
4. Zaznaczyć LiDAR, jeśli mają być przeszkody, i narzędzia, jeśli są potrzebne.
5. Kliknąć Uruchom, poczekać na wynik i otworzyć wizualizację lub wykresy.
6. Przy błędzie odczytać log konkretnej usługi. Sam exit 1 nie mówi o przyczynie.
7. Zatrzymać system przyciskiem Zatrzymaj.

Po obecnej poprawce zapis i Grafana zostały wznowione. Nie ma potrzeby kasowania
bazy ani wolumenów. Zmiany nie zostały zacommitowane ani wysłane na GitHub.
