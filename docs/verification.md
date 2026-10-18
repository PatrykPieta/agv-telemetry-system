# Weryfikacja zmian — 2026-10-11

Gałąź: codex/uporzadkowanie-projektu. Testy wykonano na Windows / Docker Desktop,
w odrębnym projekcie Compose agv-check. Użyto osobnych wolumenów; istniejąca baza
projekt_agv i jego dashboardy nie były używane do testów.

## Wyniki

- Walidacja docker compose config: poprawna.
- Budowanie wszystkich obrazów aplikacji: poprawne.
- Inicjalizacja tabel, hypertable, agregacji i tematów Kafki: poprawna.
- Ponowna inicjalizacja istniejącego środowiska testowego: poprawna.
- 6 testów telemetrii i LiDAR: poprawne.
- 3 testy transakcyjne PostgreSQL: poprawne, w tym odtworzenie po wycofaniu
  paczki, powtórny odczyt offsetu i archiwizacja błędnej wiadomości.
- Test kinematyki JS: ten sam dystans przy 30/144 FPS, prawidłowe jednostki,
  zatrzymanie po nieaktualnej telemetrii i brak skoku po uśpieniu karty.
- 50 potwierdzonych wiadomości: wszystkie w bazie i archiwum metadanych.
- Ostrzeżenia Sparka: odebrane dla każdego z czterech silników.
- Dwóch jednoczesnych klientów WebSocket: telemetria i LiDAR odebrane.
- Pliki backendu nie są udostępnione jako statyczne: HTTP 404.
- Przeglądarka: widoczny model, ONLINE, zmieniające się RPM i napięcie,
  oba wykresy Grafany z danymi. Brak błędów konsoli w tym sprawdzeniu.
- Po zatrzymaniu źródeł: stan Brak aktualnej telemetrii, pola pomiarowe
  zastąpione kreskami, przeszkody ukryte.
- Windows PowerShell: skrypt startowy działa w trybie Remote i Local z LiDAR.
- Panel: konstrukcja kontrolek w trybie -CheckUi i składnia PowerShell poprawne.
- Gotowy scripts/test.ps1: cały zestaw zakończony powodzeniem i kontenery
  testowe usunięte. Wolumeny agv-check pozostawione do diagnostyki.

## Granice weryfikacji

Nie wykonano testu na Raspberry Pi/ARM64, rzeczywistych czujnikach ani testu
długotrwałego obciążenia. Nie jest to pomiar skuteczności diagnostycznej lub
opóźnień dla pracy inżynierskiej. Awarię transakcji sprawdzono przez kontrolowane
wstrzyknięcie błędu; nie testowano jeszcze fizycznego zerwania sieci.

Panel jest pierwszą wersją Windows Forms, sprawdzoną konstrukcyjnie;
operacje startu i zmiany trybu sprawdzono przez ten sam skrypt, którego używa panel.
Pełny test interakcji użytkownika z każdym przyciskiem pozostaje do wykonania.

## Aktualizacja — 2026-10-13: istniejąca polityka agregacji

Na właściwej bazie wykryto konflikt przy próbie dodania polityki odświeżania
telemetry_agg_1m: stara polityka miała start_offset=NULL, nowa żądała 1 dnia.
if_not_exists nie zapobiegło błędowi nakładających się zakresów. Testy z 11 października
nie obejmowały tego przejścia ze starego harmonogramu.

Poprawiono create_aggregations.py: istniejąca polityka jest wykrywana i zachowywana.
Dodano tests/test_aggregations.py oraz jego uruchamianie w scripts/test.ps1.

- 3 nowe testy na osobnej tymczasowej bazie: wszystkie poprawne.
- Sprawdzono zachowanie istniejącej polityki i danych, dodanie brakującej polityki
  oraz wielokrotne wykonanie inicjalizacji.
- Na właściwej bazie db-init zakończył się kodem 0; zachowano job 1002 i jego konfigurację.
- data-consumer i Grafana uruchomione; konsument przeszedł kontrolę gotowości.
- W końcowym odczycie baza zawierała 600 próbek z ostatniej minuty.
- Tymczasowy kontener agv-policy-check zatrzymano i automatycznie usunięto.

W tym kroku nie powtarzano całego wcześniejszego zestawu testów przepływu.
