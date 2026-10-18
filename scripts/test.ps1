$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
function Docker-Test([string[]]$DockerArgs) {
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & docker @DockerArgs 2>&1 | ForEach-Object { "$_" }
    $result = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference
    if ($result -ne 0) { throw "Docker test failed (exit $result)" }
}
try {
    Docker-Test @('compose', '-p', 'agv-check', '--profile', 'simulation', '--profile', 'lidar',
                  'up', '-d', '--build', '--wait', '--wait-timeout', '240')
    $mount = "type=bind,source=$root,target=/workspace,readonly"
    foreach ($file in @('test_telemetry.py', 'test_database.py', 'test_aggregations.py')) {
        Docker-Test @('run', '--rm', '-e', 'AGV_POLICY_TEST=1', '--network', 'agv-check_default', '--mount', $mount,
            '-w', '/workspace', 'agv-check-edge-emulator', 'python', '-m', 'unittest',
            'discover', '-s', 'tests', '-p', $file, '-v')
    }
    Docker-Test @('run', '--rm', '--network', 'agv-check_default', '--mount', $mount,
        '-w', '/workspace', 'agv-check-edge-emulator', 'python', 'tests/smoke_pipeline.py')
    Docker-Test @('run', '--rm', '--network', 'agv-check_default', '--mount', $mount,
        '-w', '/workspace', 'agv-check-frontend', 'python', 'tests/smoke_websocket.py')
    Write-Output 'All Docker integration tests passed.'
} finally {
    & docker compose -p agv-check --profile simulation --profile lidar down
    Pop-Location
}
