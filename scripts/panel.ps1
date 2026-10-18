param([switch]$CheckUi)
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$script:projectRoot = Split-Path $PSScriptRoot -Parent
$script:operation = $null

$form = New-Object System.Windows.Forms.Form
$form.Text = 'AGV Digital Twin - panel systemu'
$form.Size = New-Object System.Drawing.Size(930, 680)
$form.MinimumSize = $form.Size
$form.StartPosition = 'CenterScreen'
$form.Font = New-Object System.Drawing.Font('Segoe UI', 10)
$heading = New-Object System.Windows.Forms.Label
$heading.Text = 'AGV Digital Twin'
$heading.Font = New-Object System.Drawing.Font('Segoe UI', 19, [System.Drawing.FontStyle]::Bold)
$heading.SetBounds(20, 15, 500, 40)
$form.Controls.Add($heading)

$mode = New-Object System.Windows.Forms.ComboBox
$mode.DropDownStyle = 'DropDownList'
[void]$mode.Items.AddRange(@('Emulator na komputerze', 'Dane z Raspberry Pi'))
$mode.SelectedIndex = 0
$mode.SetBounds(20, 70, 260, 30)
$form.Controls.Add($mode)
$lidar = New-Object System.Windows.Forms.CheckBox
$lidar.Text = 'Emulator LiDAR'
$lidar.SetBounds(300, 70, 180, 30)
$form.Controls.Add($lidar)
$tools = New-Object System.Windows.Forms.CheckBox
$tools.Text = 'Narzedzia administracyjne'
$tools.SetBounds(500, 70, 270, 30)
$form.Controls.Add($tools)

$hint = New-Object System.Windows.Forms.Label
$hint.Text = 'Wymagany Docker Desktop. Pierwszy start pobiera obrazy i biblioteki.'
$hint.SetBounds(20, 108, 850, 30)
$form.Controls.Add($hint)
$script:buttons = @()
function Add-Button($text, $x, $y, $action, $operationButton = $true) {
    $button = New-Object System.Windows.Forms.Button
    $button.Text = $text
    $button.SetBounds($x, $y, 165, 38)
    $button.Add_Click($action)
    $form.Controls.Add($button)
    if ($operationButton) { $script:buttons += $button }
}

$output = New-Object System.Windows.Forms.TextBox
$output.Multiline = $true
$output.ReadOnly = $true
$output.ScrollBars = 'Both'
$output.WordWrap = $false
$output.Font = New-Object System.Drawing.Font('Consolas', 10)
$output.SetBounds(20, 245, 870, 370)
$output.Anchor = 'Top, Bottom, Left, Right'
$output.Text = "Gotowy. Wybierz tryb i kliknij Uruchom. Zamkniecie panelu pozostawia system uruchomiony."
$form.Controls.Add($output)

function Begin-Operation([string]$action) {
    if ($script:operation) { return }
    $script:buttons | ForEach-Object { $_.Enabled = $false }
    $output.Clear()
    $selectedMode = if ($mode.SelectedIndex -eq 0) { 'Local' } else { 'Remote' }
    $script:operation = Start-Job -ArgumentList $script:projectRoot, $action, $selectedMode, $lidar.Checked, $tools.Checked -ScriptBlock {
        param($root, $action, $selectedMode, $useLidar, $useTools)
        Set-Location -LiteralPath $root
        try {
            switch ($action) {
                'Start' { & (Join-Path $root 'start.ps1') -Mode $selectedMode -Lidar:$useLidar -Tools:$useTools -NoBrowser }
                'Stop' {
                    & docker compose --profile simulation --profile lidar --profile tools stop 2>&1 | ForEach-Object { "$_" }
                    if ($LASTEXITCODE -ne 0) { throw 'Zatrzymanie nie powiodlo sie.' }
                }
                'Status' {
                    & docker compose --profile simulation --profile lidar --profile tools ps -a 2>&1 | ForEach-Object { "$_" }
                    if ($LASTEXITCODE -ne 0) { throw 'Nie mozna odczytac stanu Dockera.' }
                    try { Invoke-RestMethod 'http://localhost:8000/health' -TimeoutSec 3 | ConvertTo-Json }
                    catch { 'Backend nie jest gotowy lub nie ma polaczenia z Kafka.' }
                }
                'Logs' { & docker compose --profile simulation --profile lidar --profile tools logs --no-color --tail 60 2>&1 | ForEach-Object { "$_" } }
            }
        } catch { "BLAD: $($_.Exception.Message)" }
    }
}
Add-Button 'Uruchom' 20 145 { Begin-Operation 'Start' }
Add-Button 'Zatrzymaj' 195 145 { Begin-Operation 'Stop' }
Add-Button 'Stan uslug' 370 145 { Begin-Operation 'Status' }
Add-Button 'Pokaz logi' 545 145 { Begin-Operation 'Logs' }
Add-Button 'Wizualizacja 3D' 20 195 { Start-Process 'http://localhost:8000' } $false
Add-Button 'Wykresy' 195 195 { Start-Process 'http://localhost:3000/d/agv-system' } $false
Add-Button 'Konfiguracja' 370 195 {
    $configPath = Join-Path $script:projectRoot '.env'
    if (-not (Test-Path -LiteralPath $configPath)) {
        Copy-Item -LiteralPath (Join-Path $script:projectRoot '.env.example') -Destination $configPath
    }
    Start-Process notepad.exe -ArgumentList ('"' + $configPath + '"')
} $false
Add-Button 'Instrukcja' 545 195 {
    Start-Process notepad.exe -ArgumentList ('"' + (Join-Path $script:projectRoot 'README.md') + '"')
} $false

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 300
$timer.Add_Tick({
    if ($script:operation) {
        $lines = @(Receive-Job $script:operation 2>&1)
        foreach ($line in $lines) { $output.AppendText("$line" + [Environment]::NewLine) }
        if ($script:operation.State -in @('Completed', 'Failed', 'Stopped')) {
            Remove-Job $script:operation
            $script:operation = $null
            $script:buttons | ForEach-Object { $_.Enabled = $true }
            $output.AppendText("Operacja zakonczona." + [Environment]::NewLine)
        }
    }
})
$form.Add_FormClosing({
    param($sender, $eventArgs)
    if ($script:operation) {
        $eventArgs.Cancel = $true
        [void][System.Windows.Forms.MessageBox]::Show('Zaczekaj na zakonczenie operacji.', 'AGV')
    }
})
if ($CheckUi) {
    $form.Dispose()
    $timer.Dispose()
    Write-Output 'Panel controls constructed successfully.'
    return
}
$timer.Start()
[void]$form.ShowDialog()
$timer.Dispose()
$form.Dispose()
