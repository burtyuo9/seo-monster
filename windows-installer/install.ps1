# ============================================
# SEO Monster - Windows PowerShell Installer v2.0
# Автоматическая установка всех зависимостей
# ============================================

param(
    [switch]$SkipDependencies,
    [switch]$Force,
    [string]$InstallPath = "$env:USERPROFILE\seo-monster-app"
)

# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Конфигурация
$RepoUrl = "https://github.com/burtyuo9/seo-monster.git"
$PythonVersion = "3.11.0"
$NodeVersion = "20.10.0"

# Цвета
function Write-Step { param($msg) Write-Host "`n==> $msg" -ForegroundColor Blue }
function Write-Success { param($msg) Write-Host "[✓] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "[✗] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "    $msg" -ForegroundColor Cyan }

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
║          Windows Installer v2.0                           ║
╚═══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

Write-Host "Директория установки: $InstallPath" -ForegroundColor Gray
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Рекомендуется запустить от имени администратора для автоматической установки зависимостей."
    Write-Host ""
}

# Функция для проверки команды
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Функция для скачивания файла
function Download-File {
    param($Url, $Output)
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $Output -UseBasicParsing
        return $true
    } catch {
        return $false
    }
}

# ============================================
# 1. Проверка и установка Chocolatey
# ============================================
Write-Step "1/7 Проверка Chocolatey (менеджер пакетов)..."

if (-not (Test-Command "choco")) {
    Write-Warning "Chocolatey не найден. Устанавливаем..."
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Обновляем PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Success "Chocolatey установлен"
    } catch {
        Write-Warning "Не удалось установить Chocolatey автоматически"
        Write-Info "Продолжаем без Chocolatey..."
    }
} else {
    $chocoVer = choco --version
    Write-Success "Chocolatey $chocoVer найден"
}

# ============================================
# 2. Проверка и установка Python
# ============================================
Write-Step "2/7 Проверка Python..."

if (-not (Test-Command "python")) {
    Write-Warning "Python не найден. Устанавливаем..."
    
    if (Test-Command "choco") {
        choco install python --version=$PythonVersion -y
    } else {
        Write-Info "Скачивание Python $PythonVersion..."
        $pythonInstaller = "$env:TEMP\python-installer.exe"
        
        if (Download-File "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe" $pythonInstaller) {
            Write-Info "Установка Python..."
            Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
            Remove-Item $pythonInstaller -Force
        } else {
            Write-Error "Не удалось скачать Python"
            Write-Info "Пожалуйста, установите Python вручную: https://www.python.org/downloads/"
            exit 1
        }
    }
    
    # Обновляем PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Success "Python установлен"
} else {
    $pythonVer = python --version
    Write-Success "$pythonVer найден"
}

# ============================================
# 3. Проверка и установка Node.js
# ============================================
Write-Step "3/7 Проверка Node.js..."

if (-not (Test-Command "node")) {
    Write-Warning "Node.js не найден. Устанавливаем..."
    
    if (Test-Command "choco") {
        choco install nodejs-lts -y
    } else {
        Write-Info "Скачивание Node.js $NodeVersion..."
        $nodeInstaller = "$env:TEMP\node-installer.msi"
        
        if (Download-File "https://nodejs.org/dist/v$NodeVersion/node-v$NodeVersion-x64.msi" $nodeInstaller) {
            Write-Info "Установка Node.js..."
            Start-Process msiexec.exe -ArgumentList "/i", $nodeInstaller, "/quiet", "/norestart" -Wait
            Remove-Item $nodeInstaller -Force
        } else {
            Write-Error "Не удалось скачать Node.js"
            Write-Info "Пожалуйста, установите Node.js вручную: https://nodejs.org/"
            exit 1
        }
    }
    
    # Обновляем PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Success "Node.js установлен"
} else {
    $nodeVer = node --version
    Write-Success "Node.js $nodeVer найден"
}

# ============================================
# 4. Проверка и установка Git
# ============================================
Write-Step "4/7 Проверка Git..."

if (-not (Test-Command "git")) {
    Write-Warning "Git не найден. Устанавливаем..."
    
    if (Test-Command "choco") {
        choco install git -y
    } else {
        Write-Info "Скачивание Git..."
        $gitInstaller = "$env:TEMP\git-installer.exe"
        
        if (Download-File "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe" $gitInstaller) {
            Write-Info "Установка Git..."
            Start-Process -FilePath $gitInstaller -ArgumentList "/VERYSILENT", "/NORESTART" -Wait
            Remove-Item $gitInstaller -Force
        } else {
            Write-Error "Не удалось скачать Git"
            Write-Info "Пожалуйста, установите Git вручную: https://git-scm.com/download/win"
            exit 1
        }
    }
    
    # Обновляем PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Success "Git установлен"
} else {
    $gitVer = git --version
    Write-Success "$gitVer найден"
}

# ============================================
# 5. Установка pnpm
# ============================================
Write-Step "5/7 Проверка pnpm..."

if (-not (Test-Command "pnpm")) {
    Write-Warning "pnpm не найден. Устанавливаем..."
    npm install -g pnpm
    Write-Success "pnpm установлен"
} else {
    $pnpmVer = pnpm --version
    Write-Success "pnpm $pnpmVer найден"
}

# ============================================
# 6. Клонирование репозитория
# ============================================
Write-Step "6/7 Клонирование SEO Monster..."

if (Test-Path $InstallPath) {
    if ($Force) {
        Write-Warning "Удаление существующей директории..."
        Remove-Item -Path $InstallPath -Recurse -Force
    } else {
        Write-Warning "Директория уже существует: $InstallPath"
        Write-Info "Обновляем репозиторий..."
        Set-Location $InstallPath
        git pull origin main
    }
}

if (-not (Test-Path $InstallPath)) {
    Write-Info "Клонирование из $RepoUrl..."
    git clone $RepoUrl $InstallPath
}

if (-not (Test-Path $InstallPath)) {
    Write-Error "Не удалось клонировать репозиторий"
    exit 1
}

Set-Location $InstallPath
Write-Success "Репозиторий готов"

# ============================================
# 7. Установка зависимостей проекта
# ============================================
Write-Step "7/7 Установка зависимостей проекта..."

# Backend
Write-Info "Настройка Backend..."
Set-Location "$InstallPath\backend"

# Создаём виртуальное окружение
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Активируем и устанавливаем зависимости
& ".\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip | Out-Null
pip install -r requirements.txt | Out-Null
deactivate

# Создаём .env если не существует
if (-not (Test-Path ".env")) {
    @"
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
DATABASE_URL=sqlite:///./data/main.db

# Бесплатные AI провайдеры (рекомендуется)
# GROQ_API_KEY=
# TOGETHER_API_KEY=
# HUGGINGFACE_API_KEY=
# COHERE_API_KEY=
# MISTRAL_API_KEY=
# DEEPSEEK_API_KEY=
# GOOGLE_AI_API_KEY=
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

Write-Success "Backend настроен"

# Frontend
Write-Info "Настройка Frontend..."
Set-Location "$InstallPath\frontend"
pnpm install | Out-Null
pnpm run build | Out-Null
Write-Success "Frontend настроен"

# Создаём скрипты запуска
Set-Location $InstallPath

# start.bat
@"
@echo off
chcp 65001 >nul
title SEO Monster
echo.
echo ========================================
echo    Starting SEO Monster...
echo ========================================
echo.
start "SEO Monster Backend" cmd /c "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak >nul
start "SEO Monster Frontend" cmd /c "cd /d %~dp0frontend && pnpm preview --host 0.0.0.0 --port 5200"
timeout /t 3 /nobreak >nul
start http://localhost:5200
echo.
echo SEO Monster запущен!
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5200
echo.
echo Нажмите любую клавишу для закрытия этого окна...
pause >nul
"@ | Out-File -FilePath "start.bat" -Encoding ASCII

# stop.bat
@"
@echo off
chcp 65001 >nul
title Stopping SEO Monster
echo.
echo Stopping SEO Monster...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5200') do taskkill /F /PID %%a 2>nul
echo.
echo SEO Monster остановлен!
pause
"@ | Out-File -FilePath "stop.bat" -Encoding ASCII

# Start-SEOMonster.ps1
@"
# SEO Monster - PowerShell Launcher
`$ErrorActionPreference = 'SilentlyContinue'

Write-Host "Starting SEO Monster..." -ForegroundColor Cyan

# Start Backend
`$backendPath = "`$PSScriptRoot\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '`$backendPath'; .\venv\Scripts\Activate.ps1; python -m uvicorn main:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 5

# Start Frontend
`$frontendPath = "`$PSScriptRoot\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '`$frontendPath'; pnpm preview --host 0.0.0.0 --port 5200" -WindowStyle Normal

Start-Sleep -Seconds 3

# Open browser
Start-Process "http://localhost:5200"

Write-Host ""
Write-Host "SEO Monster запущен!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5200" -ForegroundColor Yellow
"@ | Out-File -FilePath "Start-SEOMonster.ps1" -Encoding UTF8

Write-Success "Скрипты запуска созданы"

# ============================================
# Завершение
# ============================================
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         Установка завершена успешно!                      ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Директория установки: $InstallPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Для запуска SEO Monster:" -ForegroundColor Yellow
Write-Host "  1. Откройте: $InstallPath" -ForegroundColor White
Write-Host "  2. Запустите: start.bat" -ForegroundColor White
Write-Host ""
Write-Host "Или используйте PowerShell:" -ForegroundColor Yellow
Write-Host "  cd '$InstallPath'" -ForegroundColor White
Write-Host "  .\Start-SEOMonster.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Не забудьте настроить API ключи в:" -ForegroundColor Yellow
Write-Host "  $InstallPath\backend\.env" -ForegroundColor White
Write-Host ""
Write-Host "Приложение будет доступно по адресу:" -ForegroundColor Yellow
Write-Host "  http://localhost:5200" -ForegroundColor Cyan
Write-Host ""

# Спрашиваем о запуске
$launch = Read-Host "Запустить SEO Monster сейчас? (y/n)"
if ($launch -eq "y" -or $launch -eq "Y") {
    Set-Location $InstallPath
    & ".\Start-SEOMonster.ps1"
}
