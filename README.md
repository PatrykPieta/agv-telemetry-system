# Cyfrowy bliźniak AGV — Edge Computing

Prototyp pracy inżynierskiej: telemetria napędu i IMU, Kafka, TimescaleDB,
Spark, Grafana oraz wizualizacja Three.js.

## Uruchomienie na Windows

1. Uruchom Docker Desktop z kontenerami Linux i zaczekaj na gotowość silnika.
2. Dwuklik pliku **AGV.cmd** otwiera panel systemu.
3. Wybierz **Emulator na komputerze**, opcjonalnie emulator LiDAR i narzędzia.
4. Kliknij **Uruchom**. Pierwszy start wymaga Internetu i pobrania zależności.
5. Po zakończeniu operacji otwórz **Wizualizacja 3D** lub **Wykresy**.

Panel udostępnia start, zatrzymanie, stan usług, ostatnie logi i otwarcie
konfiguracji. Jest to lokalny panel Windows, nie spakowany instalator EXE.
Konfiguracja otwiera się obecnie w edytorze pliku .env.
Zamknięcie panelu pozostawia kontenery uruchomione. Przycisk Zatrzymaj zachowuje dane.
Podczas operacji panel pozostaje aktywny; poczekaj na jej zakończenie przed zamknięciem.

Nie jest wymagany lokalny Python ani Node do uruchomienia systemu.
Python działa w kontenerach; Node jest potrzebny tylko do testu kinematyki.

Alternatywnie w PowerShell:

~~~powershell
.\start.ps1
.\start.ps1 -Lidar -Tools
.\start.ps1 -Mode Remote -NoBrowser
~~~

Bez panelu i skryptu: `docker compose --profile simulation up -d --build --wait`.
Samo `docker compose up -d` uruchamia centralne usługi bez lokalnego źródła.

## Konfiguracja i Raspberry Pi 5

Przycisk Konfiguracja tworzy .env z .env.example, jeśli plik jeszcze nie istnieje.
Zmiany są stosowane przy kolejnym uruchomieniu.

| Zmienna | Znaczenie |
|---|---|
| KAFKA_EXTERNAL_HOST | localhost do pracy lokalnej; adres LAN komputera dla Raspberry Pi |
| AGV_ID | Identyfikator źródła i pojazdu pokazywanego w UI |
| EMULATOR_HZ | Żądana częstotliwość, domyślnie 10 Hz |
| EMULATOR_SCENARIO | normal albo overheat (usterka od 10. sekundy) |
| EMULATOR_SEED | Ziarno losowania, domyślnie 42 |
| EMULATOR_DURATION_S | 0 = bez limitu, dodatnia liczba = czas sesji |
| POSTGRES_* | Parametry bazy, zgodne z istniejącym wolumenem |

Zmiana POSTGRES_PASSWORD w .env nie zmienia hasła już istniejącej bazy.
Porty 8000, 3000, 29092 muszą być wolne. Narzędzia zajmują dodatkowo 8080 i 8081.

Na komputerze ustaw KAFKA_EXTERNAL_HOST na jego adres LAN i wybierz tryb
Dane z Raspberry Pi. Wyłącz opcję lokalnego LiDAR, jeśli dane LiDAR także pochodzą z Pi.
Tryb Remote zatrzymuje poprzedni lokalny emulator telemetrii.

Na Raspberry Pi z Dockerem, w kopii repozytorium:

~~~bash
docker build -t agv-edge ./edge-emulator
docker run --rm --name agv-edge \
  -e KAFKA_SERVER=192.168.1.100:29092 \
  -e AGV_ID=AGV-01 -e EMULATOR_HZ=10 \
  -e EMULATOR_SCENARIO=normal agv-edge
~~~

Zastąp przykładowy adres adresem komputera. Sprawdź dostępność portu 29092 w sieci
i synchronizację zegarów Pi oraz komputera. KAFKA_SERVER wewnątrz centralnego
Compose zawsze wskazuje kafka:9092. Nie uruchamiaj drugiego źródła o tym samym AGV_ID.

Emulator może działać na Pi, ale build ARM64 i rzeczywiste czujniki wymagają
osobnego sprawdzenia na sprzęcie. Moduł LiDAR nadal korzysta z MockRPLidar.

## Usługi i pliki

| Ścieżka | Odpowiedzialność |
|---|---|
| edge-emulator/main.py | Generator telemetrii z parametrami i scenariuszami |
| edge-emulator/telemetry.py | Walidacja i jednostki danych |
| edge-emulator/transport.py | Producent Kafka, klucz agv_id i potwierdzenie dostarczenia |
| edge-emulator/consumer.py | Transakcyjny zapis, obsługa ponownego odczytu i błędnych danych |
| edge-emulator/create_aggregations.py | Inicjalizacja tabel i agregacji |
| edge-emulator/edge_processor.py | Filtracja i DBSCAN LiDAR |
| frontend/server.py | Asynchroniczny odbiór Kafki i WebSocket |
| frontend/js/ | Model 3D, kinematyka, sieć i scena |
| spark-analytics/ | Bazowe ostrzeżenia o temperaturze napędu |
| infra/grafana/ | Źródło danych i dashboard tworzone automatycznie |
| scripts/panel.ps1 | Panel Windows |
| tests/ | Testy jednostkowe, transakcyjne i przepływu |
| docs/ | Kontrakt danych, ograniczenia i wyniki weryfikacji |

Adresy: [wizualizacja](http://localhost:8000), [Grafana](http://localhost:3000/d/agv-system),
[Kafka UI](http://localhost:8080), [Adminer](http://localhost:8081), [Spark](http://localhost:4040).
Kafka UI i Adminer wymagają opcji narzędzi. PostgreSQL, Spark UI i narzędzia
administracyjne są udostępnione tylko lokalnie. Kafka i UI są przeznaczone do
zaufanej sieci laboratoryjnej; konfiguracja nie obejmuje TLS ani autoryzacji Kafki.

Nowy dashboard ma UID agv-system; istniejące dashboardy nie są nadpisywane.
Bazowe konta i hasła służą środowisku demonstracyjnemu.

## Trwałość i obsługa błędów

- Inicjalizacja zachowuje istniejącą politykę odświeżania agregacji minutowej;
  tworzy politykę tylko wtedy, gdy jej brakuje.
- Kafka, ZooKeeper, baza, Grafana i checkpoint Sparka mają wolumeny.
- Najpierw zatwierdzana jest transakcja bazy, następnie offsety Kafki.
- ingested_messages rozpoznaje ponowny odczyt tego samego topic/partition/offset.
- rejected_messages zapisuje odrzucone wiadomości wraz z powodem.
- Awaria zapisu lub commit offsetów kończy proces; Docker uruchamia go ponownie.
- Każdy wynik poll jest zapisywany bez czekania na 200 próbek.
- Archiwum ingested_messages zachowuje pełny JSON i czas zapisu.
- Nie ma jeszcze retencji archiwum ani trwałego bufora na Raspberry Pi.
- Deduplikacja offsetów nie usuwa kopii wysłanych ponownie jako nowe rekordy Kafki.
- Nie kasuj tematów Kafki i nie odtwarzaj ich z offsetami od zera przy zachowaniu
  dotychczasowego rejestru ingested_messages. Potrzebna jest wtedy kontrolowana migracja.
- Dane sprzed wdrożenia rejestru nie są automatycznie deduplikowane.
- Nie używaj down -v do zwykłego zatrzymywania — usuwa wolumeny danych.

Zadana częstotliwość emulatora jest celem. Potwierdzanie każdej wiadomości
ogranicza maksymalną przepustowość; należy mierzyć faktyczną częstotliwość.
IMU jest obecnie syntetyczne i nie stanowi modelu dynamiki ani źródła danych do FFT.

## Testy

~~~powershell
node tests/physics.test.mjs
.\scripts\test.ps1
~~~

Skrypt testowy wymaga Docker Desktop i wolnych portów systemu.
Korzysta z osobnego projektu agv-check i jego własnych wolumenów, a na końcu
usuwa kontenery testowe, zachowując wolumeny do diagnostyki.
Nie uruchamiaj go równocześnie z właściwym systemem używającym tych samych portów.

Testy obejmują schemat danych, deterministyczny emulator, DBSCAN, kinematykę,
zachowanie istniejącego harmonogramu agregacji,
wycofanie transakcji, ponowny odczyt, błędne dane, 50 wiadomości przez Kafkę do bazy,
ostrzeżenie Sparka i dwóch klientów WebSocket.
MonitorLag.ps1 zapisuje liczbę zaległych wiadomości, nie opóźnienie w milisekundach.
Brak odczytu oznacza unavailable zamiast fałszywego zera.

## Pozostałe prace

- Wspólny stan/odometria pojazdu po stronie Edge lub backendu; obecnie każda
  przeglądarka zaczyna estymację pozycji od początku.
- Kalibracja geometrii i osi obrotu rzeczywistego modelu/napędu.
- Buforowanie danych podczas utraty sieci na Pi, adaptery czujników i test ARM64.
- Wiarygodny model IMU, przetwarzanie sygnału oraz diagnostyka zweryfikowana na danych.
- Metryki opóźnień etapów, percentyle, CPU/RAM, scenariusze awarii i retencja.
- Migracja bazowych obrazów Python 3.9 do nowszego wspieranego środowiska wraz ze Sparkiem.
- Pełne blokady zależności przechodnich i usunięcie zależności startu od Internetu.
- Docelowy formularz konfiguracji i pakiet instalacyjny panelu.

Wykres max_vibration_z zachowuje starą nazwę kolumny dla zgodności.
Jest maksimum |accel_z| razem ze składową grawitacji, nie zweryfikowaną miarą drgań.
