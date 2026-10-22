$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Install Docker Desktop, start its Linux engine, then run this script again.' }
docker info --format '{{.ServerVersion}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop and wait for the engine to be ready.' }
if (-not (Test-Path -LiteralPath '.env')) {
    $randomBytes = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($randomBytes)
    $generatedPassword = -join ($randomBytes | ForEach-Object { $_.ToString('x2') })
    "POSTGRES_PASSWORD=$generatedPassword`nDEALER_PORT=8090" | Set-Content -LiteralPath '.env'
}
docker compose up --build -d --wait --wait-timeout 180
if ($LASTEXITCODE -ne 0) { throw 'Startup failed. Read docker compose logs; existing data has been preserved.' }
docker compose exec app python -m scripts.create_user manager --role manager --if-empty
if ($LASTEXITCODE -ne 0) { throw 'Account setup failed. Application data has been preserved.' }
$portLine = Get-Content -LiteralPath '.env' | Where-Object { $_ -match '^DEALER_PORT=' } | Select-Object -Last 1
$appPort = if ($portLine) { ($portLine -split '=',2)[1] } else { '8090' }
Write-Host "Open http://127.0.0.1:$appPort - local to this computer. Stop with: docker compose stop"
