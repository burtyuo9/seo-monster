@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ============================================
:: SEO Monster - Stop Script for Windows
:: ============================================

title SEO Monster - Stop

set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

echo.
echo %BLUE%============================================%RESET%
echo %BLUE%   SEO Monster - Остановка сервисов%RESET%
echo %BLUE%============================================%RESET%
echo.

:: Остановка Backend (порт 8000)
echo %YELLOW%[1/2] Остановка Backend (порт 8000)...%RESET%
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo      Завершение процесса PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: Остановка Frontend (порт 5200)
echo %YELLOW%[2/2] Остановка Frontend (порт 5200)...%RESET%
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5200" ^| findstr "LISTENING"') do (
    echo      Завершение процесса PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: Дополнительно убиваем процессы uvicorn и node
taskkill /F /IM "uvicorn.exe" >nul 2>&1
taskkill /F /IM "node.exe" /FI "WINDOWTITLE eq SEO Monster*" >nul 2>&1

echo.
echo %GREEN%============================================%RESET%
echo %GREEN%   SEO Monster остановлен!%RESET%
echo %GREEN%============================================%RESET%
echo.

pause
