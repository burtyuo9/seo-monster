# ============================================
# SEO Monster - PowerShell Stop Script
# ============================================

param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5200
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "============================================" -ForegroundColor Blue
Write-Host "   SEO Monster - Остановка сервисов" -ForegroundColor Blue
Write-Host "============================================" -ForegroundColor Blue
Write-Host ""

# Функция для остановки процесса на порту
function Stop-ProcessOnPort {
    param([int]$Port)
    
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        if ($conn.OwningProcess -ne 0) {
            try {
                $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "    Завершение процесса: $($process.Name) (PID: $($process.Id))" -ForegroundColor Gray
                    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                }
            } catch {
                # Игнорируем ошибки
            }
        }
    }
}

# Остановка Backend
Write-Host "[1/2] Остановка Backend (порт $BackendPort)..." -ForegroundColor Yellow
Stop-ProcessOnPort -Port $BackendPort

# Остановка Frontend
Write-Host "[2/2] Остановка Frontend (порт $FrontendPort)..." -ForegroundColor Yellow
Stop-ProcessOnPort -Port $FrontendPort

# Дополнительная очистка
Get-Process -Name "python", "node" -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*SEO Monster*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "   SEO Monster остановлен!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
