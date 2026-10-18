param(
    [ValidateSet('Local', 'Remote')][string]$Mode = 'Local',
    [switch]$Lidar,
    [switch]$Tools,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'
function Invoke-Docker([string[]]$DockerArgs) {
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & docker @DockerArgs 2>&1 | ForEach-Object { "$_" }
    $result = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference
    if ($result -ne 0) { throw "Docker zakonczyl operacje bledem ($result). Sprawdz logi i Docker Desktop." }
}
Push-Location $PSScriptRoot
try {
    Invoke-Docker @('info', '--format', '{{.ServerVersion}}')
    $composeArgs = @('compose')
    if ($Mode -eq 'Local') { $composeArgs += @('--profile', 'simulation') }
    if ($Lidar) { $composeArgs += @('--profile', 'lidar') }
    if ($Tools) { $composeArgs += @('--profile', 'tools') }
    # Stop sources from a previous mode to prevent two AGVs sharing the same ID.
    $sourcesToStop = @()
    if ($Mode -eq 'Remote') { $sourcesToStop += 'edge-emulator' }
    if (-not $Lidar) { $sourcesToStop += 'edge-processor' }
    if ($sourcesToStop.Count) {
        Invoke-Docker (@('compose', '--profile', 'simulation', '--profile', 'lidar', 'stop') + $sourcesToStop)
    }
    Invoke-Docker ($composeArgs + @('up', '-d', '--build', '--wait', '--wait-timeout', '240'))
    Write-Output 'Uslugi uruchomione. Gotowosc telemetrii sprawdz w wizualizacji; Spark moze jeszcze pobierac konektor.'
    if (-not $NoBrowser) { Start-Process 'http://localhost:8000' }
} finally {
    Pop-Location
}
