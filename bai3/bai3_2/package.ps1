# Allowlist packaging: credentials, local environment and Docker volumes never enter ZIP.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$files = @('common.py', 'producer.py', 'consumer.py', 'verify.py', 'requirements.txt',
    'Dockerfile', 'compose.yaml', '.dockerignore', '.gitignore', '.env.example',
    'init.ps1', 'verify.ps1', 'package.ps1', 'HUONG_DAN_CHAY.txt')
$envTemplate = Get-Content -LiteralPath '.env.example'
if ($envTemplate -notcontains 'RABBITMQ_PASSWORD=') { throw '.env.example phai de trong mat khau.' }
foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Thieu file: $file" }
}
$zip = Join-Path $PSScriptRoot 'Bai3_2_Ma_nguon.zip'
Compress-Archive -LiteralPath $files -DestinationPath $zip -Force
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::OpenRead($zip)
try {
    if ($archive.Entries.Count -ne $files.Count) { throw 'So file ZIP khong dung allowlist.' }
    $passwordLine = Get-Content -LiteralPath '.env' -ErrorAction SilentlyContinue | Where-Object { $_.StartsWith('RABBITMQ_PASSWORD=') }
    $secret = if ($passwordLine) { $passwordLine.Substring('RABBITMQ_PASSWORD='.Length) } else { '' }
    foreach ($entry in $archive.Entries) {
        if ($entry.FullName -eq '.env' -or $entry.FullName -notin $files) { throw 'ZIP co file ngoai allowlist.' }
        $reader = [IO.StreamReader]::new($entry.Open())
        try { $content = $reader.ReadToEnd() } finally { $reader.Dispose() }
        if ($secret -and $content.Contains($secret)) { throw 'Phat hien mat khau trong ZIP.' }
        if ($content -match 'amqps?://[^\s:/]+:[^\s@]+@') { throw 'Phat hien URL co tai khoan trong ZIP.' }
    }
} finally { $archive.Dispose() }
Write-Host 'Da tao Bai3_2_Ma_nguon.zip; da kiem tra khong chua .env hay mat khau hien tai.'
