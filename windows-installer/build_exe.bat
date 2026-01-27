@echo off
chcp 65001 >nul
setlocal

:: ============================================
:: SEO Monster - Build EXE Script
:: Создание исполняемого файла для Windows
:: ============================================

title SEO Monster - Build EXE

echo.
echo ============================================
echo    SEO Monster - Build EXE
echo ============================================
echo.

:: Проверка Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python не найден!
    echo Пожалуйста, установите Python и добавьте его в PATH.
    pause
    exit /b 1
)

:: Установка PyInstaller
echo [1/3] Проверка PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorLevel% neq 0 (
    echo      Установка PyInstaller...
    pip install pyinstaller
)
echo      PyInstaller готов.

:: Создание exe
echo.
echo [2/3] Сборка исполняемого файла...
pyinstaller --onefile --windowed --name "SEO Monster" seo_monster_gui.py

if exist "dist\SEO Monster.exe" (
    echo.
    echo [3/3] Копирование файлов...
    
    :: Создаём директорию для релиза
    if not exist "release" mkdir release
    
    copy "dist\SEO Monster.exe" "release\" >nul
    copy "install.bat" "release\" >nul
    copy "install.ps1" "release\" >nul
    
    echo.
    echo ============================================
    echo    Сборка завершена успешно!
    echo ============================================
    echo.
    echo Файлы находятся в директории: release\
    echo.
    echo Содержимое:
    echo   - SEO Monster.exe  (GUI приложение)
    echo   - install.bat      (CMD установщик)
    echo   - install.ps1      (PowerShell установщик)
    echo.
) else (
    echo.
    echo [ERROR] Сборка не удалась!
    echo Проверьте логи выше для диагностики.
)

pause
