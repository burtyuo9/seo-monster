@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ============================================
:: SEO Monster - Windows Installer v2.0
:: Автоматическая установка всех зависимостей
:: ============================================

title SEO Monster - Установщик

:: Цвета для вывода
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

:: Конфигурация
set "REPO_URL=https://github.com/burtyuo9/seo-monster.git"
set "INSTALL_DIR=%USERPROFILE%\seo-monster-app"
set "PYTHON_VERSION=3.11.0"
set "NODE_VERSION=20.10.0"

echo.
echo %BLUE%============================================%RESET%
echo %BLUE%   SEO Monster - Windows Installer v2.0%RESET%
echo %BLUE%============================================%RESET%
echo.

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%[!] Рекомендуется запустить от имени администратора%RESET%
    echo %YELLOW%    для автоматической установки зависимостей.%RESET%
    echo.
    pause
)

:: ============================================
:: 1. Проверка и установка Python
:: ============================================
echo %BLUE%[1/6] Проверка Python...%RESET%

where python >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%[!] Python не найден. Устанавливаем...%RESET%
    
    :: Скачиваем Python
    echo %BLUE%    Скачивание Python %PYTHON_VERSION%...%RESET%
    curl -L -o "%TEMP%\python-installer.exe" "https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
    
    if exist "%TEMP%\python-installer.exe" (
        echo %BLUE%    Установка Python...%RESET%
        "%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        
        :: Обновляем PATH
        set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
        set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts"
        
        del "%TEMP%\python-installer.exe"
        echo %GREEN%[✓] Python установлен%RESET%
    ) else (
        echo %RED%[✗] Не удалось скачать Python%RESET%
        echo %YELLOW%    Пожалуйста, установите Python вручную: https://www.python.org/downloads/%RESET%
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
    echo %GREEN%[✓] !PYTHON_VER! найден%RESET%
)

:: ============================================
:: 2. Проверка и установка Node.js
:: ============================================
echo.
echo %BLUE%[2/6] Проверка Node.js...%RESET%

where node >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%[!] Node.js не найден. Устанавливаем...%RESET%
    
    :: Скачиваем Node.js
    echo %BLUE%    Скачивание Node.js %NODE_VERSION%...%RESET%
    curl -L -o "%TEMP%\node-installer.msi" "https://nodejs.org/dist/v%NODE_VERSION%/node-v%NODE_VERSION%-x64.msi"
    
    if exist "%TEMP%\node-installer.msi" (
        echo %BLUE%    Установка Node.js...%RESET%
        msiexec /i "%TEMP%\node-installer.msi" /quiet /norestart
        
        :: Обновляем PATH
        set "PATH=%PATH%;C:\Program Files\nodejs"
        
        del "%TEMP%\node-installer.msi"
        echo %GREEN%[✓] Node.js установлен%RESET%
    ) else (
        echo %RED%[✗] Не удалось скачать Node.js%RESET%
        echo %YELLOW%    Пожалуйста, установите Node.js вручную: https://nodejs.org/%RESET%
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
    echo %GREEN%[✓] Node.js !NODE_VER! найден%RESET%
)

:: ============================================
:: 3. Проверка и установка Git
:: ============================================
echo.
echo %BLUE%[3/6] Проверка Git...%RESET%

where git >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%[!] Git не найден. Устанавливаем...%RESET%
    
    :: Скачиваем Git
    echo %BLUE%    Скачивание Git...%RESET%
    curl -L -o "%TEMP%\git-installer.exe" "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
    
    if exist "%TEMP%\git-installer.exe" (
        echo %BLUE%    Установка Git...%RESET%
        "%TEMP%\git-installer.exe" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
        
        :: Обновляем PATH
        set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"
        
        del "%TEMP%\git-installer.exe"
        echo %GREEN%[✓] Git установлен%RESET%
    ) else (
        echo %RED%[✗] Не удалось скачать Git%RESET%
        echo %YELLOW%    Пожалуйста, установите Git вручную: https://git-scm.com/download/win%RESET%
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('git --version 2^>^&1') do set GIT_VER=%%i
    echo %GREEN%[✓] !GIT_VER! найден%RESET%
)

:: ============================================
:: 4. Установка pnpm
:: ============================================
echo.
echo %BLUE%[4/6] Проверка pnpm...%RESET%

where pnpm >nul 2>&1
if %errorLevel% neq 0 (
    echo %YELLOW%[!] pnpm не найден. Устанавливаем...%RESET%
    call npm install -g pnpm
    echo %GREEN%[✓] pnpm установлен%RESET%
) else (
    for /f "tokens=*" %%i in ('pnpm --version 2^>^&1') do set PNPM_VER=%%i
    echo %GREEN%[✓] pnpm !PNPM_VER! найден%RESET%
)

:: ============================================
:: 5. Клонирование репозитория
:: ============================================
echo.
echo %BLUE%[5/6] Клонирование SEO Monster...%RESET%

if exist "%INSTALL_DIR%" (
    echo %YELLOW%[!] Директория уже существует: %INSTALL_DIR%%RESET%
    echo %YELLOW%    Обновляем репозиторий...%RESET%
    cd /d "%INSTALL_DIR%"
    git pull origin main
) else (
    echo %BLUE%    Клонирование из %REPO_URL%...%RESET%
    git clone "%REPO_URL%" "%INSTALL_DIR%"
)

if not exist "%INSTALL_DIR%" (
    echo %RED%[✗] Не удалось клонировать репозиторий%RESET%
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"
echo %GREEN%[✓] Репозиторий готов%RESET%

:: ============================================
:: 6. Установка зависимостей
:: ============================================
echo.
echo %BLUE%[6/6] Установка зависимостей...%RESET%

:: Backend
echo %BLUE%    Настройка Backend...%RESET%
cd /d "%INSTALL_DIR%\backend"

:: Создаём виртуальное окружение
if not exist "venv" (
    python -m venv venv
)

:: Активируем и устанавливаем зависимости
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
call venv\Scripts\deactivate.bat

:: Создаём .env если не существует
if not exist ".env" (
    echo OPENAI_API_KEY=YOUR_OPENAI_API_KEY> .env
    echo DATABASE_URL=sqlite:///./data/main.db>> .env
    echo # Добавьте ваши API ключи ниже>> .env
    echo # GROQ_API_KEY=>> .env
    echo # TOGETHER_API_KEY=>> .env
)

echo %GREEN%[✓] Backend настроен%RESET%

:: Frontend
echo %BLUE%    Настройка Frontend...%RESET%
cd /d "%INSTALL_DIR%\frontend"
call pnpm install
call pnpm run build
echo %GREEN%[✓] Frontend настроен%RESET%

:: Копируем GUI и скрипты запуска
echo %BLUE%    Копирование утилит...%RESET%
cd /d "%INSTALL_DIR%"

:: Создаём скрипт запуска
echo @echo off> start.bat
echo chcp 65001 ^>nul>> start.bat
echo title SEO Monster>> start.bat
echo echo Starting SEO Monster...>> start.bat
echo start "Backend" cmd /c "cd /d %%~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn main:app --host 0.0.0.0 --port 8000">> start.bat
echo timeout /t 3 /nobreak ^>nul>> start.bat
echo start "Frontend" cmd /c "cd /d %%~dp0frontend && pnpm preview --host 0.0.0.0 --port 5200">> start.bat
echo timeout /t 3 /nobreak ^>nul>> start.bat
echo start http://localhost:5200>> start.bat
echo echo SEO Monster запущен!>> start.bat
echo echo Backend: http://localhost:8000>> start.bat
echo echo Frontend: http://localhost:5200>> start.bat

:: Создаём скрипт остановки
echo @echo off> stop.bat
echo chcp 65001 ^>nul>> stop.bat
echo title Stopping SEO Monster>> stop.bat
echo echo Stopping SEO Monster...>> stop.bat
echo for /f "tokens=5" %%%%a in ('netstat -aon ^^^| findstr :8000') do taskkill /F /PID %%%%a 2^>nul>> stop.bat
echo for /f "tokens=5" %%%%a in ('netstat -aon ^^^| findstr :5200') do taskkill /F /PID %%%%a 2^>nul>> stop.bat
echo echo SEO Monster остановлен!>> stop.bat
echo pause>> stop.bat

echo %GREEN%[✓] Утилиты созданы%RESET%

:: ============================================
:: Завершение
:: ============================================
echo.
echo %GREEN%============================================%RESET%
echo %GREEN%   Установка завершена успешно!%RESET%
echo %GREEN%============================================%RESET%
echo.
echo %BLUE%Директория установки: %INSTALL_DIR%%RESET%
echo.
echo %YELLOW%Для запуска SEO Monster:%RESET%
echo   1. Откройте: %INSTALL_DIR%
echo   2. Запустите: start.bat
echo.
echo %YELLOW%Или используйте команды:%RESET%
echo   cd /d "%INSTALL_DIR%"
echo   start.bat
echo.
echo %YELLOW%Не забудьте настроить API ключи в:%RESET%
echo   %INSTALL_DIR%\backend\.env
echo.
echo %BLUE%Приложение будет доступно по адресу:%RESET%
echo   http://localhost:5200
echo.

:: Спрашиваем о запуске
set /p LAUNCH="Запустить SEO Monster сейчас? (y/n): "
if /i "%LAUNCH%"=="y" (
    cd /d "%INSTALL_DIR%"
    call start.bat
)

pause
