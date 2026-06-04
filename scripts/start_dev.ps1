param(
    [string]$DatabaseUrl = "postgresql+psycopg://news:news@localhost:5432/newsdb"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Python = Join-Path $Backend ".venv\Scripts\python.exe"
$Activate = Join-Path $Backend ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $Python)) {
    Write-Host "Создаю Python venv для backend..."
    Push-Location $Backend
    python -m venv .venv
    & $Python -m pip install -r requirements.txt
    Pop-Location
}

Write-Host "Применяю миграции Alembic..."
Push-Location $Backend
$env:DATABASE_URL = $DatabaseUrl
& $Python -m alembic upgrade head
Pop-Location

if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    Write-Host "Устанавливаю npm-зависимости frontend..."
    Push-Location $Frontend
    npm install
    Pop-Location
}

$backendCommand = @"
cd '$Backend'
`$env:DATABASE_URL='$DatabaseUrl'
. '$Activate'
uvicorn app.main:app --reload
"@

$frontendCommand = @"
cd '$Frontend'
npm start
"@

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCommand
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCommand

Write-Host ""
Write-Host "Запуск выполнен."
Write-Host "Backend:  http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:4200"
