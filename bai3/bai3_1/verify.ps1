$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.env')) { throw 'Copy .env.example to .env first.' }
$config = @{}
Get-Content -LiteralPath '.env' | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)=(.*)$') { $config[$matches[1]] = $matches[2].Trim() }
}
$pair = $config['RABBITMQ_USER'] + ':' + $config['RABBITMQ_PASSWORD']
$headers = @{ Authorization = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($pair)) }
$port = $config['MANAGEMENT_PORT']
if (-not $port) { $port = '15672' }
$base = "http://localhost:$port/api"
$queueUrl = "$base/queues/%2F/it4735.nhom16.telemetry"
New-Item -ItemType Directory -Path 'output' -Force | Out-Null

function Invoke-Compose {
    param([string[]]$ComposeArgs)
    & docker compose @ComposeArgs
    if ($LASTEXITCODE -ne 0) { throw ('docker compose failed: ' + ($ComposeArgs -join ' ')) }
}
function Get-QueueState {
    $q = Invoke-RestMethod -Uri $queueUrl -Headers $headers
    [pscustomobject]@{
        time = [DateTimeOffset]::Now.ToString('o')
        queue = $q.name
        ready = [int]$q.messages_ready
        unacked = [int]$q.messages_unacknowledged
        consumers = [int]$q.consumers
    }
}
function Wait-Empty {
    for ($i=0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 2
        $state = Get-QueueState
        if ($state.ready -eq 0 -and $state.unacked -eq 0 -and $state.consumers -eq 1) { return $state }
    }
    throw 'Queue did not drain or consumer is not connected.'
}
function Publish-TestMessage {
    param([string]$Payload)
    $body = @{ properties = @{}; routing_key = 'it4735.nhom16.telemetry';
        payload = $Payload; payload_encoding = 'string' } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$base/exchanges/%2F/amq.default/publish" -Headers $headers -Method Post -ContentType 'application/json' -Body $body
    if (-not $response.routed) { throw 'Test message was not routed.' }
}

$result = [ordered]@{ group = 16; status = 'RUNNING' }
Start-Transcript -Path 'output/kiem_tra.txt' -Force | Out-Null
try {
    Invoke-Compose -ComposeArgs @('stop', 'producer')
    $result.before = Wait-Empty
    Invoke-Compose -ComposeArgs @('stop', 'consumer')
    Invoke-Compose -ComposeArgs @('start', 'producer')
    Write-Output 'Waiting 30 seconds with consumer stopped...'
    Start-Sleep -Seconds 30
    Invoke-Compose -ComposeArgs @('stop', 'producer')
    Start-Sleep -Seconds 6
    $result.stopped_30_seconds = Get-QueueState
    if ($result.stopped_30_seconds.ready -lt 5 -or $result.stopped_30_seconds.consumers -ne 0) {
        throw 'Expected at least 5 waiting messages and 0 consumers.'
    }
    Invoke-Compose -ComposeArgs @('start', 'consumer')
    $result.resumed = Wait-Empty
    $since = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    Publish-TestMessage 'hello'
    Publish-TestMessage '{"temperature":23,"humidity":33}'
    Start-Sleep -Seconds 3
    $logs = & docker compose logs --no-color --since $since consumer 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) { throw 'Could not read consumer logs.' }
    Write-Output $logs
    if ($logs -notmatch 'JSON ERROR' -or $logs -notmatch 'temperature=23 C \| humidity=33') {
        throw 'Expected JSON error followed by successful valid telemetry.'
    }
    $result.invalid_then_valid = 'PASS'
    $result.status = 'PASS'
    $result | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -LiteralPath 'output/kiem_tra.json'
    Write-Output ($result | ConvertTo-Json -Depth 5)
} catch {
    $result.status = 'FAIL'
    $result.error = $_.Exception.Message
    $result | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -LiteralPath 'output/kiem_tra.json'
    throw
} finally {
    try { Invoke-Compose -ComposeArgs @('start', 'producer', 'consumer') }
    finally { Stop-Transcript | Out-Null }
}
