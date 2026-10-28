param([ValidatePattern('^[0-9]+$')][string]$Mssv = '202416203')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (Test-Path -LiteralPath '.env') {
    Write-Host '.env da ton tai. Giu nguyen tai khoan va du lieu.'
    exit 0
}
$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
$bytes = New-Object byte[] 24
$rng.GetBytes($bytes)
$rng.Dispose()
$password = [Convert]::ToBase64String($bytes)
$lines = @("MSSV=$Mssv", 'RABBITMQ_USER=student', "RABBITMQ_PASSWORD=$password", 'AMQP_PORT=5673', 'MANAGEMENT_PORT=15673')
[IO.File]::WriteAllLines((Join-Path $PSScriptRoot '.env'), $lines, [Text.UTF8Encoding]::new($false))
Write-Host 'Da tao .env voi mat khau ngau nhien. Xem file nay tren may de dang nhap web.'
Write-Host 'Khong chup .env vao anh bao cao. Goi ZIP se loai file nay.'
