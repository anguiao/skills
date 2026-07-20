# Stop the visual companion server and clean up temporary sessions.
# Supports Windows PowerShell 5.1 and PowerShell 7.

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Write-Json {
    param([hashtable]$Value)

    Write-Output ($Value | ConvertTo-Json -Compress)
}

function Write-Utf8NoBom {
    param(
        [string]$Path,
        [string]$Content
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Test-ProcessAlive {
    param([int]$ProcessId)

    return $null -ne (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)
}

function Set-StoppedMarker {
    param(
        [string]$StateDirectory,
        [string]$Reason
    )

    $serverInfoFile = Join-Path $StateDirectory 'server-info'
    Remove-Item -LiteralPath $serverInfoFile -Force -ErrorAction SilentlyContinue

    $epochSeconds = [long]([DateTime]::UtcNow - [DateTime]'1970-01-01T00:00:00Z').TotalSeconds
    $content = @{ reason = $Reason; timestamp = $epochSeconds } | ConvertTo-Json -Compress
    Write-Utf8NoBom (Join-Path $StateDirectory 'server-stopped') ($content + [Environment]::NewLine)
}

if ($args.Count -ne 1 -or [string]::IsNullOrEmpty($args[0])) {
    Write-Json @{ error = 'Usage: stop-server.ps1 <session_dir>' }
    exit 1
}

$sessionDir = [IO.Path]::GetFullPath($args[0])
$stateDir = Join-Path $sessionDir 'state'
$pidFile = Join-Path $stateDir 'server.pid'
$serverIdFile = Join-Path $stateDir 'server-instance-id'
$serverStartTimeFile = Join-Path $stateDir 'server-start-time'

if (-not (Test-Path -LiteralPath $pidFile -PathType Leaf)) {
    Write-Json @{ status = 'not_running' }
    exit 0
}

$processId = 0
$pidText = (Get-Content -Raw -LiteralPath $pidFile).Trim()
if (-not [int]::TryParse($pidText, [ref]$processId)) {
    Remove-Item -LiteralPath $pidFile, $serverIdFile, $serverStartTimeFile -Force -ErrorAction SilentlyContinue
    Set-StoppedMarker $stateDir 'stale_pid'
    Write-Json @{ status = 'stale_pid' }
    exit 0
}

$expectedId = if (Test-Path -LiteralPath $serverIdFile -PathType Leaf) {
    (Get-Content -Raw -LiteralPath $serverIdFile).Trim()
}
else {
    ''
}

$isExpectedServer = $false
$expectedStartTicks = 0L
$startTimeText = if (Test-Path -LiteralPath $serverStartTimeFile -PathType Leaf) {
    (Get-Content -Raw -LiteralPath $serverStartTimeFile).Trim()
}
else {
    ''
}

if ($expectedId -match '^[A-Za-z0-9_-]{32,64}$' -and
    [long]::TryParse($startTimeText, [ref]$expectedStartTicks) -and
    (Test-ProcessAlive $processId)) {
    try {
        $processInfo = Get-Process -Id $processId -ErrorAction Stop
        $actualStartTicks = $processInfo.StartTime.ToUniversalTime().Ticks
        $isExpectedServer = $actualStartTicks -eq $expectedStartTicks
    }
    catch {
        $isExpectedServer = $false
    }
}

if (-not $isExpectedServer) {
    Remove-Item -LiteralPath $pidFile, $serverIdFile, $serverStartTimeFile -Force -ErrorAction SilentlyContinue
    Set-StoppedMarker $stateDir 'stale_pid'
    Write-Json @{ status = 'stale_pid' }
    exit 0
}

Stop-Process -Id $processId -ErrorAction SilentlyContinue
for ($attempt = 0; $attempt -lt 20; $attempt++) {
    if (-not (Test-ProcessAlive $processId)) {
        break
    }
    Start-Sleep -Milliseconds 100
}

if (Test-ProcessAlive $processId) {
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 100
}

if (Test-ProcessAlive $processId) {
    Write-Json @{ status = 'failed'; error = 'process still running' }
    exit 1
}

Remove-Item -LiteralPath $pidFile, $serverIdFile, $serverStartTimeFile -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $stateDir 'server.log'), (Join-Path $stateDir 'server-error.log') `
    -Force -ErrorAction SilentlyContinue
Set-StoppedMarker $stateDir 'stop-server.ps1'

# Only remove temporary sessions created by this script. Keep persistent .brainstorming sessions.
$tempRootPath = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
while ($tempRootPath.EndsWith('\') -or $tempRootPath.EndsWith('/')) {
    $tempRootPath = $tempRootPath.Substring(0, $tempRootPath.Length - 1)
}
$tempRoot = $tempRootPath + [IO.Path]::DirectorySeparatorChar
$sessionPath = [IO.Path]::GetFullPath($sessionDir)
$sessionLeaf = Split-Path -Leaf $sessionPath
$isTemporarySession = $sessionPath.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -and
    $sessionLeaf -match '^brainstorm-\d+-\d+$'

if ($isTemporarySession) {
    Remove-Item -LiteralPath $sessionPath -Recurse -Force
}

Write-Json @{ status = 'stopped' }
