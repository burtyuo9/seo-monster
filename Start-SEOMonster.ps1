# ============================================
# SEO Monster - PowerShell Start Script
# ============================================

param(
    [switch]$NoBrowser,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5200
)

# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Цвета
function Write-Step { param($msg) Write-Host "`n==> $msg" -ForegroundColor Blue }
function Write-Success { param($msg) Write-Host "[✓] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "[✗] $msg" -ForegroundColor Red }

# Баннер
Write-Host @"

╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗███████╗ ██████╗     ███╗   ███╗ ██████╗ ███╗   ║
║   ██╔════╝██╔════╝██╔═══██╗    ████╗ ████║██╔═══██╗████╗  ║
║   ███████╗█████╗  ██║   ██║    ██╔████╔██║██║   ██║██╔██╗ ║
║   ╚════██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██║   ██║██║╚██╗║
║   ███████║███████╗╚██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██║ ╚██║
║   ╚══════╝╚══════╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Проверка структуры проекта
if (-not (Test-Path "backend\main.py")) {
    Write-Error "Backend не найден! Убедитесь, что скрипт находится в корне проекта."
    exit 1
}

if (-not (Test-Path "frontend\package.json")) {
    Write-Error "Frontend не найден! Убедитесь, что скрипт находится в корне проекта."
    exit 1
}

# Проверка виртуального окружения
if (-not (Test-Path "backend\venv\Scripts\Activate.ps1")) {
    Write-Warning "Виртуальное окружение не найдено. Создаём..."
    Set-Location backend
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    python -m pip install --upgrade pip | Out-Null
    pip install -r requirements.txt | Out-Null
    deactivate
    Set-Location ..
    Write-Success "Виртуальное окружение создано"
}

# Проверка node_modules
if (-not (Test-Path "frontend\node_modules")) {
    Write-Warning "Node модули не найдены. Устанавливаем..."
    Set-Location frontend
    pnpm install | Out-Null
    pnpm run build | Out-Null
    Set-Location ..
    Write-Success "Node модули установлены"
}

# Проверка dist
if (-not (Test-Path "frontend\dist")) {
    Write-Warning "Frontend не собран. Собираем..."
    Set-Location frontend
    pnpm run build | Out-Null
    Set-Location ..
    Write-Success "Frontend собран"
}

# Запуск Backend
Write-Step "Запуск Backend (API)..."
$backendPath = Join-Path $ScriptDir "backend"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$backendPath'; .\venv\Scripts\Activate.ps1; python -m uvicorn main:app --host 0.0.0.0 --port $BackendPort"
) -WindowStyle Normal

Write-Host "    Ожидание запуска Backend..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Запуск Frontend
Write-Step "Запуск Frontend (UI)..."
$frontendPath = Join-Path $ScriptDir "frontend"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$frontendPath'; pnpm preview --host 0.0.0.0 --port $FrontendPort"
) -WindowStyle Normal

Write-Host "    Ожидание запуска Frontend..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Открытие браузера
if (-not $NoBrowser) {
    Write-Step "Открытие браузера..."
    Start-Process "http://localhost:$FrontendPort"
}

# Итоговая информация
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         SEO Monster успешно запущен!                      ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:  " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:$BackendPort" -ForegroundColor Yellow
Write-Host "Frontend UI:  " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:$FrontendPort" -ForegroundColor Yellow
Write-Host "API Docs:     " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:$BackendPort/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Для остановки закройте окна терминалов или запустите:" -ForegroundColor Gray
Write-Host "  .\Stop-SEOMonster.ps1" -ForegroundColor White
Write-Host ""
