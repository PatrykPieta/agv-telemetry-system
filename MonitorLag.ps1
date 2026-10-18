param([string]$OutputFile = 'wyniki_lag.csv', [string]$Group = 'agv_db_writers')
Push-Location $PSScriptRoot
try {
    'TimestampUtc,LagMessages,Status' | Set-Content -LiteralPath $OutputFile -Encoding UTF8
    while ($true) {
        $rows = & docker compose exec -T kafka kafka-consumer-groups --bootstrap-server kafka:9092 --describe --group $Group 2>&1
        $exitCode = $LASTEXITCODE
        $lag = 0L
        $found = $false
        foreach ($row in $rows) {
            $parts = "$row".Trim() -split '\s+'
            if ($parts.Count -ge 6 -and $parts[0] -eq $Group -and $parts[1] -eq 'telemetry_topic') {
                $value = 0L
                if ([long]::TryParse($parts[5], [ref]$value)) {
                    $lag += $value
                    $found = $true
                }
            }
        }
        $timestamp = [DateTime]::UtcNow.ToString('o')
        if ($exitCode -eq 0 -and $found) { "$timestamp,$lag,ok" | Add-Content -LiteralPath $OutputFile }
        else { "$timestamp,,unavailable" | Add-Content -LiteralPath $OutputFile }
        Start-Sleep -Seconds 2
    }
} finally { Pop-Location }
