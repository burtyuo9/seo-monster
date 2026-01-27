"""
SEO Monster - Diagnostics API Routes v2.0
Расширенные API endpoints для модуля диагностики и автоисправления
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

# Добавляем путь к сервисам
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.diagnostics_service import (
    get_diagnostics_service, 
    DiagnosticStatus, 
    DiagnosticCategory,
    DiagnosticSeverity
)

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


class CategoryCheckRequest(BaseModel):
    category: str


class ConfigUpdateRequest(BaseModel):
    enabled_checks: Optional[List[str]] = None
    disabled_checks: Optional[List[str]] = None
    quick_check_ids: Optional[List[str]] = None
    notify_on_error: Optional[bool] = None
    notify_on_critical: Optional[bool] = None


# ==================== ОСНОВНЫЕ ENDPOINTS ====================

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


@router.get("/categories")
async def get_categories():
    """Получение списка категорий проверок"""
    service = get_diagnostics_service()
    return {"categories": service.get_categories()}


# ==================== ЗАПУСК ПРОВЕРОК ====================

@router.post("/run-all")
async def run_all_diagnostics():
    """Запуск всех диагностических проверок"""
    service = get_diagnostics_service()
    results = await service.run_all_checks()
    
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
                "severity": r.severity.value,
                "recommendations": r.recommendations,
                "duration_ms": r.duration_ms,
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
            "fixed": len([r for r in results if r.status == DiagnosticStatus.FIXED]),
            "skipped": len([r for r in results if r.status == DiagnosticStatus.SKIPPED])
        }
    }


@router.post("/run-quick")
async def run_quick_diagnostics():
    """Быстрая проверка критических компонентов"""
    service = get_diagnostics_service()
    results = await service.run_quick_check()
    
    return {
        "results": [
            {
                "check_id": r.check_id,
                "category": r.category.value,
                "name": r.name,
                "status": r.status.value,
                "message": r.message,
                "severity": r.severity.value,
                "timestamp": r.timestamp
            }
            for r in results
        ],
        "summary": {
            "total": len(results),
            "ok": len([r for r in results if r.status == DiagnosticStatus.OK]),
            "issues": len([r for r in results if r.status not in [DiagnosticStatus.OK, DiagnosticStatus.SKIPPED]])
        }
    }


@router.post("/run-category")
async def run_category_diagnostics(request: CategoryCheckRequest):
    """Запуск проверок по категории"""
    service = get_diagnostics_service()
    
    # Преобразуем строку в enum
    try:
        category = DiagnosticCategory(request.category)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid category: {request.category}. Valid categories: {[c.value for c in DiagnosticCategory]}"
        )
    
    results = await service.run_category_checks(category)
    
    return {
        "category": request.category,
        "results": [
            {
                "check_id": r.check_id,
                "name": r.name,
                "status": r.status.value,
                "message": r.message,
                "details": r.details,
                "fix_available": r.fix_available,
                "severity": r.severity.value,
                "recommendations": r.recommendations,
                "timestamp": r.timestamp
            }
            for r in results
        ],
        "summary": {
            "total": len(results),
            "ok": len([r for r in results if r.status == DiagnosticStatus.OK]),
            "issues": len([r for r in results if r.status not in [DiagnosticStatus.OK, DiagnosticStatus.SKIPPED]])
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
        "severity": result.severity.value,
        "recommendations": result.recommendations,
        "duration_ms": result.duration_ms,
        "timestamp": result.timestamp
    }


# ==================== ИСПРАВЛЕНИЯ ====================

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
        "actions_taken": result.actions_taken,
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
                "actions_taken": r.actions_taken,
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


# ==================== ОТЧЕТЫ ====================

@router.get("/health-report")
async def get_health_report():
    """Генерация полного отчета о здоровье системы"""
    service = get_diagnostics_service()
    report = await service.generate_health_report()
    
    return {
        "overall_status": report.overall_status.value,
        "health_score": report.health_score,
        "total_checks": report.total_checks,
        "passed_checks": report.passed_checks,
        "warning_checks": report.warning_checks,
        "error_checks": report.error_checks,
        "critical_checks": report.critical_checks,
        "fixed_checks": report.fixed_checks,
        "categories_summary": report.categories_summary,
        "top_issues": report.top_issues,
        "recommendations": report.recommendations,
        "timestamp": report.timestamp
    }


@router.get("/health-reports-history")
async def get_health_reports_history(limit: int = Query(10, ge=1, le=100)):
    """Получение истории отчетов о здоровье"""
    service = get_diagnostics_service()
    reports = service.get_health_reports(limit=limit)
    
    return {"reports": reports, "total": len(reports)}


@router.get("/health-summary")
async def get_health_summary():
    """Получение краткой сводки о здоровье системы"""
    service = get_diagnostics_service()
    status = service.get_status()
    last_results = service.get_last_results()
    
    # Подсчет по severity
    critical_issues = [r for r in last_results if r.get("status") == "critical"]
    high_issues = [r for r in last_results if r.get("status") == "error" and r.get("severity") == "high"]
    
    # Определяем общий статус
    if critical_issues:
        overall_status = "critical"
        health_score = 20
    elif high_issues:
        overall_status = "error"
        health_score = 50
    elif any(r.get("status") == "error" for r in last_results):
        overall_status = "error"
        health_score = 60
    elif any(r.get("status") == "warning" for r in last_results):
        overall_status = "warning"
        health_score = 80
    else:
        overall_status = "healthy"
        health_score = 100
    
    # Группировка проблем по категориям
    issues_by_category = {}
    for r in last_results:
        if r.get("status") not in ["ok", "fixed", "skipped"]:
            cat = r.get("category", "unknown")
            if cat not in issues_by_category:
                issues_by_category[cat] = 0
            issues_by_category[cat] += 1
    
    return {
        "overall_status": overall_status,
        "health_score": health_score,
        "auto_mode": status["auto_mode_enabled"],
        "auto_fix": status["auto_fix_enabled"],
        "checks_count": status["total_checks"],
        "fixes_count": status["total_fixes"],
        "last_check_results": len(last_results),
        "issues_count": len([r for r in last_results if r.get("status") not in ["ok", "fixed", "skipped"]]),
        "critical_issues": len(critical_issues),
        "issues_by_category": issues_by_category,
        "last_full_check": status.get("last_full_check")
    }


# ==================== НАСТРОЙКИ ====================

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
    if request.seconds < 60:
        raise HTTPException(status_code=400, detail="Minimum interval is 60 seconds")
    
    service = get_diagnostics_service()
    service.set_check_interval(request.seconds)
    
    return {
        "success": True,
        "check_interval": service.check_interval,
        "message": f"Check interval set to {service.check_interval} seconds"
    }


@router.post("/config")
async def update_config(request: ConfigUpdateRequest):
    """Обновление конфигурации диагностики"""
    service = get_diagnostics_service()
    
    if request.enabled_checks is not None:
        service.config["enabled_checks"] = request.enabled_checks
    if request.disabled_checks is not None:
        service.config["disabled_checks"] = request.disabled_checks
    if request.quick_check_ids is not None:
        service.config["quick_check_ids"] = request.quick_check_ids
    if request.notify_on_error is not None:
        service.config["notify_on_error"] = request.notify_on_error
    if request.notify_on_critical is not None:
        service.config["notify_on_critical"] = request.notify_on_critical
    
    service._save_config()
    
    return {
        "success": True,
        "config": service.config
    }


@router.get("/config")
async def get_config():
    """Получение текущей конфигурации"""
    service = get_diagnostics_service()
    return {"config": service.config}


# ==================== ИСТОРИЯ ====================

@router.get("/history")
async def get_diagnostics_history(
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    category: Optional[str] = None
):
    """Получение истории диагностики"""
    service = get_diagnostics_service()
    history = service.get_history(limit=limit, status_filter=status, category_filter=category)
    
    return {"history": history, "total": len(history)}


@router.get("/fixes-history")
async def get_fixes_history(limit: int = Query(50, ge=1, le=500)):
    """Получение истории исправлений"""
    service = get_diagnostics_service()
    history = service.get_fixes_history(limit=limit)
    
    return {"history": history, "total": len(history)}


@router.get("/last-results")
async def get_last_results():
    """Получение последних результатов по каждой проверке"""
    service = get_diagnostics_service()
    results = service.get_last_results()
    
    # Группировка по категориям
    by_category = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(r)
    
    # Подсчитываем статистику
    ok_count = len([r for r in results if r.get("status") == "ok"])
    warning_count = len([r for r in results if r.get("status") == "warning"])
    error_count = len([r for r in results if r.get("status") == "error"])
    critical_count = len([r for r in results if r.get("status") == "critical"])
    fixed_count = len([r for r in results if r.get("status") == "fixed"])
    
    return {
        "results": results,
        "by_category": by_category,
        "summary": {
            "total": len(results),
            "ok": ok_count,
            "warnings": warning_count,
            "errors": error_count,
            "critical": critical_count,
            "fixed": fixed_count
        }
    }


# ==================== УТИЛИТЫ ====================

@router.delete("/history")
async def clear_history():
    """Очистка истории диагностики"""
    service = get_diagnostics_service()
    service.history = []
    service._save_json(service.history_file, [])
    
    return {"success": True, "message": "History cleared"}


@router.delete("/fixes-history")
async def clear_fixes_history():
    """Очистка истории исправлений"""
    service = get_diagnostics_service()
    service.fixes_history = []
    service._save_json(service.fixes_file, [])
    
    return {"success": True, "message": "Fixes history cleared"}


@router.post("/restart-auto-mode")
async def restart_auto_mode():
    """Перезапуск автоматического режима"""
    service = get_diagnostics_service()
    
    if service.auto_mode_enabled:
        service.stop_auto_mode()
        service.start_auto_mode()
        return {"success": True, "message": "Auto mode restarted"}
    else:
        return {"success": False, "message": "Auto mode is not enabled"}
