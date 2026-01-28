@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ============================================
:: SEO Monster - Quick Start Script for Windows
:: ============================================

title SEO Monster

:: Цвета
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "RESET=[0m"

echo.
echo %CYAN%╔═══════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║                                                           ║%RESET%
echo %CYAN%║   ███████╗███████╗ ██████╗     ███╗   ███╗ ██████╗ ███╗   ║%RESET%
echo %CYAN%║   ██╔════╝██╔════╝██╔═══██╗    ████╗ ████║██╔═══██╗████╗  ║%RESET%
echo %CYAN%║   ███████╗█████╗  ██║   ██║    ██╔████╔██║██║   ██║██╔██╗ ║%RESET%
echo %CYAN%║   ╚════██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██║   ██║██║╚██╗║%RESET%
echo %CYAN%║   ███████║███████╗╚██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██║ ╚██║%RESET%
echo %CYAN%║   ╚══════╝╚══════╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═║%RESET%
echo %CYAN%║                                                           ║%RESET%
echo %CYAN%╚═══════════════════════════════════════════════════════════╝%RESET%
echo.

:: Определяем директорию скрипта
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Проверяем наличие backend и frontend
if not exist "backend\main.py" (
    echo %RED%[ERROR] Backend не найден!%RESET%
    echo %YELLOW%Убедитесь, что скрипт находится в корне проекта SEO Monster.%RESET%
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo %RED%[ERROR] Frontend не найден!%RESET%
    echo %YELLOW%Убедитесь, что скрипт находится в корне проекта SEO Monster.%RESET%
    pause
    exit /b 1
)

:: Проверяем виртуальное окружение
if not exist "backend\venv\Scripts\activate.bat" (
    echo %YELLOW%[!] Виртуальное окружение не найдено. Создаём...%RESET%
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
    call venv\Scripts\deactivate.bat
    cd ..
    echo %GREEN%[✓] Виртуальное окружение создано%RESET%
)

:: Проверяем node_modules
if not exist "frontend\node_modules" (
    echo %YELLOW%[!] Node модули не найдены. Устанавливаем...%RESET%
    cd frontend
    call pnpm install
    call pnpm run build
    cd ..
    echo %GREEN%[✓] Node модули установлены%RESET%
)

:: Проверяем dist
if not exist "frontend\dist" (
    echo %YELLOW%[!] Frontend не собран. Собираем...%RESET%
    cd frontend
    call pnpm run build
    cd ..
    echo %GREEN%[✓] Frontend собран%RESET%
)

echo %BLUE%[1/3] Запуск Backend (API)...%RESET%
start "SEO Monster - Backend" cmd /c "cd /d "%SCRIPT_DIR%backend" && call venv\Scripts\activate.bat && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

echo %BLUE%[2/3] Ожидание запуска Backend...%RESET%
timeout /t 5 /nobreak >nul

echo %BLUE%[3/3] Запуск Frontend (UI)...%RESET%
start "SEO Monster - Frontend" cmd /c "cd /d "%SCRIPT_DIR%frontend" && npx vite preview --host 0.0.0.0 --port 5200"

timeout /t 3 /nobreak >nul

echo.
echo %GREEN%╔═══════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║         SEO Monster успешно запущен!                      ║%RESET%
echo %GREEN%╚═══════════════════════════════════════════════════════════╝%RESET%
echo.
echo %CYAN%Backend API:%RESET%  http://localhost:8000
echo %CYAN%Frontend UI:%RESET%  http://localhost:5200
echo %CYAN%API Docs:%RESET%     http://localhost:8000/docs
echo.

:: Открываем браузер
echo %BLUE%Открываем браузер...%RESET%
start http://localhost:5200

echo.
echo %YELLOW%Для остановки закройте окна терминалов или запустите stop.bat%RESET%
echo.
pause
