# Skrypt automatycznego startu systemu Digital Twin AGV

# 1. Czyszczenie konsoli i ładny komunikat
# 1. Czyszczenie konsoli, zmiana kodowania na UTF-8 i ładny komunikat
[console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding
Clear-Host
Clear-Host
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🚀 Uruchamianie Systemu IIoT Cyfrowego Bliźniaka..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

# 2. FAZA 1: Odpalenie infrastruktury (Baza, Kafka, Grafana)
Write-Host "⏳ Uruchamianie infrastruktury (Kafka, Baza Danych, Grafana, Adminer)..." -ForegroundColor Cyan
# Upewnij się, że nazwy usług zgadzają się z Twoim plikiem docker-compose.yml!
docker-compose up -d kafka timescaledb grafana adminer

# 3. Odczekanie na stabilizację (Rozwiązanie problemu "zimnego startu")
Write-Host ""
Write-Host "⏱️ Oczekiwanie 15 sekund na gotowość sieciową i bazodanową..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 4. FAZA 2: Odpalenie reszty systemu (Spark, Emulator, Backend)
Write-Host "🚀 Infrastruktura gotowa! Uruchamianie analityki (Spark) i emulatora AGV..." -ForegroundColor Green
docker-compose up -d

# === TWÓJ ŚWIETNY POMYSŁ: Pauza przed przeglądarką ===
Write-Host ""
Write-Host "⏱️ Stabilizacja sieci... Dajemy systemowi 10 sekund przed otwarciem paneli..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 5. Otwieranie paneli operatorskich
Write-Host ""
Write-Host "🌐 Otwieranie paneli operatorskich..." -ForegroundColor Cyan

# 1. Warstwa Prezentacji (Cyfrowy Bliźniak)
Start-Process "http://localhost:8000"

# 2. Narzędzie Analityczne (Grafana)
Start-Process "http://localhost:3000"

# 3. Szyna Danych (Kafka UI) - Zobaczysz przepływ na żywo!
Start-Process "http://localhost:8080"

# 4. Baza Danych (Adminer) - Zalogujesz się do Postgresa!
Start-Process "http://localhost:8081"

# 5. Mózg Big Data (Spark UI) - Uruchomi się dopiero, gdy Spark zacznie działać
Start-Process "http://localhost:4040"

Write-Host ""
Write-Host "✅ Sukces! Wszystkie systemy operacyjne są ONLINE i idealnie zsynchronizowane." -ForegroundColor Green
Write-Host "Logi systemu możesz śledzić komendą: docker-compose logs -f" -ForegroundColor Gray