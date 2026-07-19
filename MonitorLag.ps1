$filename = "wyniki_lag_kafka500hz.csv"

Write-Host "Uruchamiam system monitorowania opoznien (Lag)..." -ForegroundColor Cyan
Write-Host "Nacisnij Ctrl+C, aby zakonczyc pomiar." -ForegroundColor Yellow

# Zapisanie naglowkow do pliku CSV
"Czas,Lag" | Out-File -FilePath $filename -Encoding utf8

while ($true) {
    # Odpytanie Kafki przez wbudowane narzedzia CLI kontenera
    $output = docker-compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group agv_db_writers 2>$null
    
    $current_lag = 0
    foreach ($line in $output) {
        if ($line -match "telemetry_topic") {
            # Rozbicie linii po spacjach i wyciagniecie 6. kolumny (indeks 5)
            $parts = $line -split '\s+' | Where-Object { $_ -ne '' }
            if ($parts.Count -ge 6) {
                $current_lag = $parts[5]
            }
        }
    }

    # Zapis do pliku
    $now = Get-Date -Format "HH:mm:ss"
    "$now,$current_lag" | Out-File -FilePath $filename -Encoding utf8 -Append
    
    # Wyswietlenie na ekranie (nadpisywanie tej samej linii)
    Write-Host "`r[$now] Aktualny Lag: $current_lag wiadomosci   " -NoNewline
    
    Start-Sleep -Milliseconds 500
}