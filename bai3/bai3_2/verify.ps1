$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Path output -Force | Out-Null
docker compose run --rm --no-deps producer python verify.py | Tee-Object -FilePath output/kiem_tra.txt
if ($LASTEXITCODE -ne 0) { throw 'Kiem tra that bai. Xem output/kiem_tra.txt' }
Write-Host 'PASS - queue kiem tra rieng da duoc xoa, queue chinh khong bi thay doi.'
