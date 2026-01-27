"""
SEO Monster - Diagnostics API Routes
API endpoints для модуля диагностики и автоисправления
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

# Добавляем путь к сервисам
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.diagnostics_service import get_diagnostics_service, DiagnosticStatus

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


# ==================== МОДЕЛИ ====================

class AutoModeRequest(BaseModel):
    enabled: bool


class AutoFixRequest(BaseModel):
    enabled: bool


class CheckIntervalRequest(BaseModel):
    seconds: int


class SingleCheckRequest(BaseModel):
    check_id: str


class ApplyFixRequest(BaseModel):
    check_id: str


# ==================== ENDPOINTS ====================

@router.get("/status")
async def get_diagnostics_status():
    """Получение текущего статуса диагностики"""
    service = get_diagnostics_service()
    return service.get_status()


@router.get("/checks")
async def get_available_checks():
    """Получение списка доступных проверок"""
    service = get_diagnostics_service()
    return {"checks": service.get_available_checks()}


@router.post("/run-all")
async def run_all_diagnostics():
    """Запуск всех диагностических проверок"""
    service = get_diagnostics_service()
    results = await service.run_all_checks()
    
    # Преобразуем результаты в словари
    return {
        "results": [
            {
                "check_id": r.check_id,
                "category": r.category.value,
                "name": r.name,
                "status": r.status.value,
                "message": r.message,
                "details": r.details,
                "fix_available": r.fix_available,
                "fix_applied": r.fix_applied,
                "timestamp": r.timestamp
            }
            for r in results
        ],
        "summary": {
            "total": len(results),
            "ok": len([r for r in results if r.status == DiagnosticStatus.OK]),
            "warnings": len([r for r in results if r.status == DiagnosticStatus.WARNING]),
            "errors": len([r for r in results if r.status == DiagnosticStatus.ERROR]),
            "critical": len([r for r in results if r.status == DiagnosticStatus.CRITICAL]),
            "fixed": len([r for r in results if r.status == DiagnosticStatus.FIXED])
        }
    }


@router.post("/run-single")
async def run_single_check(request: SingleCheckRequest):
    """Запуск одной диагностической проверки"""
    service = get_diagnostics_service()
    result = await service.run_single_check(request.check_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"Check '{request.check_id}' not found")
    
    return {
        "check_id": result.check_id,
        "category": result.category.value,
        "name": result.name,
        "status": result.status.value,
        "message": result.message,
        "details": result.details,
        "fix_available": result.fix_available,
        "fix_applied": result.fix_applied,
        "timestamp": result.timestamp
    }


@router.post("/fix")
async def apply_single_fix(request: ApplyFixRequest):
    """Применение исправления для конкретной проверки"""
    service = get_diagnostics_service()
    result = await service.apply_fix(request.check_id)
    
    return {
        "check_id": result.check_id,
        "success": result.success,
        "message": result.message,
        "before_status": result.before_status.value,
        "after_status": result.after_status.value,
        "timestamp": result.timestamp
    }


@router.post("/fix-all")
async def apply_all_fixes():
    """Применение всех доступных исправлений"""
    service = get_diagnostics_service()
    results = await service.apply_all_fixes()
    
    return {
        "results": [
            {
                "check_id": r.check_id,
                "success": r.success,
                "message": r.message,
                "before_status": r.before_status.value,
                "after_status": r.after_status.value,
                "timestamp": r.timestamp
            }
            for r in results
        ],
        "summary": {
            "total": len(results),
            "successful": len([r for r in results if r.success]),
            "failed": len([r for r in results if not r.success])
        }
    }


@router.post("/auto-mode")
async def set_auto_mode(request: AutoModeRequest):
    """Включение/выключение автоматического режима диагностики"""
    service = get_diagnostics_service()
    service.set_auto_mode(request.enabled)
    
    return {
        "success": True,
        "auto_mode_enabled": service.auto_mode_enabled,
        "message": f"Auto mode {'enabled' if request.enabled else 'disabled'}"
    }


@router.post("/auto-fix")
async def set_auto_fix(request: AutoFixRequest):
    """Включение/выключение автоматического исправления"""
    service = get_diagnostics_service()
    service.set_auto_fix(request.enabled)
    
    return {
        "success": True,
        "auto_fix_enabled": service.auto_fix_enabled,
        "message": f"Auto fix {'enabled' if request.enabled else 'disabled'}"
    }


@router.post("/check-interval")
async def set_check_interval(request: CheckIntervalRequest):
    """Установка интервала автоматических проверок"""
    service = get_diagnostics_service()
    service.set_check_interval(request.seconds)
    
    return {
        "success": True,
        "check_interval": service.check_interval,
        "message": f"Check interval set to {service.check_interval} seconds"
    }


@router.get("/history")
async def get_diagnostics_history(limit: int = 50, status: Optional[str] = None):
    """Получение истории диагностики"""
    service = get_diagnostics_service()
    history = service.get_history(limit=limit, status_filter=status)
    
    return {"history": history, "total": len(history)}


@router.get("/fixes-history")
async def get_fixes_history(limit: int = 50):
    """Получение истории исправлений"""
    service = get_diagnostics_service()
    history = service.get_fixes_history(limit=limit)
    
    return {"history": history, "total": len(history)}


@router.get("/last-results")
async def get_last_results():
    """Получение последних результатов по каждой проверке"""
    service = get_diagnostics_service()
    results = service.get_last_results()
    
    # Подсчитываем статистику
    ok_count = len([r for r in results if r.get("status") == "ok"])
    warning_count = len([r for r in results if r.get("status") == "warning"])
    error_count = len([r for r in results if r.get("status") == "error"])
    critical_count = len([r for r in results if r.get("status") == "critical"])
    
    return {
        "results": results,
        "summary": {
            "total": len(results),
            "ok": ok_count,
            "warnings": warning_count,
            "errors": error_count,
            "critical": critical_count
        }
    }


@router.get("/health-summary")
async def get_health_summary():
    """Получение краткой сводки о здоровье системы"""
    service = get_diagnostics_service()
    status = service.get_status()
    last_results = service.get_last_results()
    
    # Определяем общий статус
    if any(r.get("status") == "critical" for r in last_results):
        overall_status = "critical"
    elif any(r.get("status") == "error" for r in last_results):
        overall_status = "error"
    elif any(r.get("status") == "warning" for r in last_results):
        overall_status = "warning"
    else:
        overall_status = "healthy"
    
    return {
        "overall_status": overall_status,
        "auto_mode": status["auto_mode_enabled"],
        "auto_fix": status["auto_fix_enabled"],
        "checks_count": status["total_checks"],
        "last_check_results": len(last_results),
        "issues_count": len([r for r in last_results if r.get("status") not in ["ok", "fixed"]])
    }
