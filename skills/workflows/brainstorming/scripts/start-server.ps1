# Start the visual companion server and output connection info.
# Supports Windows PowerShell 5.1 and PowerShell 7.

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Write-ErrorJson {
    param([string]$Message)

    Write-Output (@{ error = $Message } | ConvertTo-Json -Compress)
    exit 1
}

function Get-RequiredValue {
    param(
        [string[]]$Arguments,
        [int]$Index,
        [string]$Name
    )

    if ($Index + 1 -ge $Arguments.Count) {
        Write-ErrorJson "Missing value for $Name"
    }

    return $Arguments[$Index + 1]
}

function Invoke-WithChildEnvironment {
    param(
        [hashtable]$Environment,
        [scriptblock]$Script
    )

    $original = @{}
    foreach ($name in $Environment.Keys) {
        $original[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
        [Environment]::SetEnvironmentVariable($name, $Environment[$name], 'Process')
    }

    try {
        & $Script
    }
    finally {
        foreach ($name in $original.Keys) {
            [Environment]::SetEnvironmentVariable($name, $original[$name], 'Process')
        }
    }
}

function Write-Utf8NoBom {
    param(
        [string]$Path,
        [string]$Content
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($Path, $Content, $encoding)
}

$projectDir = $null
$foreground = $false
$bindHost = '127.0.0.1'
$urlHost = $null
$idleTimeoutMinutes = $null

for ($index = 0; $index -lt $args.Count; $index++) {
    switch ($args[$index]) {
        '--project-dir' {
            $projectDir = Get-RequiredValue $args $index '--project-dir'
            $index++
        }
        '--host' {
            $bindHost = Get-RequiredValue $args $index '--host'
            $index++
        }
        '--url-host' {
            $urlHost = Get-RequiredValue $args $index '--url-host'
            $index++
        }
        '--idle-timeout-minutes' {
            $idleTimeoutMinutes = Get-RequiredValue $args $index '--idle-timeout-minutes'
            $index++
        }
        { $_ -in @('--foreground', '--no-daemon') } {
            $foreground = $true
        }
        { $_ -in @('--background', '--daemon') } {
            $foreground = $false
        }
        default {
            Write-ErrorJson "Unknown argument: $($args[$index])"
        }
    }
}

if ([string]::IsNullOrEmpty($urlHost)) {
    if ($bindHost -in @('127.0.0.1', 'localhost')) {
        $urlHost = 'localhost'
    }
    else {
        $urlHost = $bindHost
    }
}

$idleTimeoutMs = $null
if ($null -ne $idleTimeoutMinutes) {
    $parsedMinutes = 0L
    if (-not [long]::TryParse($idleTimeoutMinutes, [ref]$parsedMinutes) -or $parsedMinutes -lt 1) {
        Write-ErrorJson '--idle-timeout-minutes must be a positive integer'
    }
    if ($parsedMinutes -gt ([long]::MaxValue / 60000)) {
        Write-ErrorJson '--idle-timeout-minutes is too large'
    }
    $idleTimeoutMs = ($parsedMinutes * 60000).ToString([Globalization.CultureInfo]::InvariantCulture)
}

$scriptDir = Split-Path -Parent $PSCommandPath
$nodeCommand = Get-Command node -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $nodeCommand) {
    Write-ErrorJson 'node executable was not found in PATH'
}

$nodeExecutable = [string](& $nodeCommand.Source -p 'process.execPath' 2>$null | Select-Object -First 1)
$nodeExecutable = $nodeExecutable.Trim()
if (-not [IO.File]::Exists($nodeExecutable)) {
    Write-ErrorJson 'failed to resolve the Node.js executable'
}

$epochSeconds = [long]([DateTime]::UtcNow - [DateTime]'1970-01-01T00:00:00Z').TotalSeconds
$sessionId = "$PID-$epochSeconds"
$portFile = $null
$tokenFile = $null

if (-not [string]::IsNullOrEmpty($projectDir)) {
    $projectRoot = [IO.Path]::GetFullPath($projectDir)
    $brainstormRoot = Join-Path $projectRoot '.brainstorming'
    $sessionDir = Join-Path $brainstormRoot $sessionId
    $portFile = Join-Path $brainstormRoot '.last-port'
    $tokenFile = Join-Path $brainstormRoot '.last-token'
}
else {
    $sessionDir = Join-Path ([IO.Path]::GetTempPath()) "brainstorm-$sessionId"
}

$stateDir = Join-Path $sessionDir 'state'
$contentDir = Join-Path $sessionDir 'content'
$pidFile = Join-Path $stateDir 'server.pid'
$serverInfoFile = Join-Path $stateDir 'server-info'
$serverIdFile = Join-Path $stateDir 'server-instance-id'
$serverStartTimeFile = Join-Path $stateDir 'server-start-time'

[IO.Directory]::CreateDirectory($contentDir) | Out-Null
[IO.Directory]::CreateDirectory($stateDir) | Out-Null

$randomBytes = New-Object byte[] 24
$random = [Security.Cryptography.RandomNumberGenerator]::Create()
try {
    $random.GetBytes($randomBytes)
}
finally {
    $random.Dispose()
}
$serverId = ([BitConverter]::ToString($randomBytes)).Replace('-', '').ToLowerInvariant()
Write-Utf8NoBom $serverIdFile ($serverId + [Environment]::NewLine)

$childEnvironment = @{
    BRAINSTORM_DIR = $sessionDir
    BRAINSTORM_HOST = $bindHost
    BRAINSTORM_URL_HOST = $urlHost
    BRAINSTORM_OWNER_PID = $null
    BRAINSTORM_PORT_FILE = $portFile
    BRAINSTORM_TOKEN_FILE = $tokenFile
}
if ($null -ne $idleTimeoutMs) {
    $childEnvironment['BRAINSTORM_IDLE_TIMEOUT_MS'] = $idleTimeoutMs
}

$nodeArguments = @('server.cjs', "--brainstorm-server-id=$serverId")

try {
    if ($foreground) {
        $process = Invoke-WithChildEnvironment $childEnvironment {
            Start-Process -FilePath $nodeExecutable -ArgumentList $nodeArguments `
                -WorkingDirectory $scriptDir -NoNewWindow -PassThru
        }
        Write-Utf8NoBom $pidFile ($process.Id.ToString() + [Environment]::NewLine)
        Write-Utf8NoBom $serverStartTimeFile ($process.StartTime.ToUniversalTime().Ticks.ToString() + [Environment]::NewLine)
        $process.WaitForExit()
        exit $process.ExitCode
    }

    $process = Invoke-WithChildEnvironment $childEnvironment {
        Start-Process -FilePath $nodeExecutable -ArgumentList $nodeArguments `
            -WorkingDirectory $scriptDir -WindowStyle Hidden -PassThru
    }
    Write-Utf8NoBom $pidFile ($process.Id.ToString() + [Environment]::NewLine)
    Write-Utf8NoBom $serverStartTimeFile ($process.StartTime.ToUniversalTime().Ticks.ToString() + [Environment]::NewLine)
}
catch {
    Write-ErrorJson "Failed to start server: $($_.Exception.Message)"
}

for ($attempt = 0; $attempt -lt 50; $attempt++) {
    if ($process.HasExited) {
        Write-ErrorJson "Server exited before startup with exit code $($process.ExitCode)"
    }

    if (Test-Path -LiteralPath $serverInfoFile) {
        for ($aliveCheck = 0; $aliveCheck -lt 20; $aliveCheck++) {
            if ($process.HasExited) {
                Write-ErrorJson 'Server started but was killed; retry with --foreground in a persistent terminal'
            }
            Start-Sleep -Milliseconds 100
        }

        Write-Output (Get-Content -Raw -LiteralPath $serverInfoFile).Trim()
        exit 0
    }

    Start-Sleep -Milliseconds 100
}

Write-ErrorJson 'Server failed to start within 5 seconds'
