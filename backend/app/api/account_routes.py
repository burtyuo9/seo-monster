"""
SEO Monster - Account Manager API Routes
API эндпоинты для управления аккаунтами
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict
import tempfile
import os

import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.account_manager import get_account_manager

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


# Pydantic модели
class ImportTextRequest(BaseModel):
    content: str
    format_type: str = "platform:username:password"
    default_platform: Optional[str] = None


class ImportCookiesRequest(BaseModel):
    account_id: str
    cookies: str  # JSON или key=value формат


class SetStatusRequest(BaseModel):
    status: str


class SetCooldownRequest(BaseModel):
    minutes: int


# API Endpoints

@router.get("/stats")
async def get_account_stats():
    """Получение статистики аккаунтов"""
    manager = get_account_manager()
    return manager.get_stats()


@router.get("/")
async def get_accounts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    account_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Получение списка аккаунтов"""
    manager = get_account_manager()
    return manager.get_accounts(platform, status, account_type, limit, offset)


@router.get("/{account_id}")
async def get_account(account_id: str, decrypt: bool = False):
    """Получение информации об аккаунте"""
    manager = get_account_manager()
    account = manager.get_account(account_id, decrypt)
    
    if not account:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")
    
    return account


@router.get("/next/{platform}")
async def get_next_account(platform: str):
    """
    Получение следующего доступного аккаунта для платформы
    
    Автоматически выбирает аккаунт с учетом ротации и cooldown
    """
    manager = get_account_manager()
    account = manager.get_next_account(platform)
    
    if not account:
        raise HTTPException(status_code=404, detail=f"Нет доступных аккаунтов для {platform}")
    
    return account


# ==================== ИМПОРТ ====================

@router.post("/import/text")
async def import_from_text(request: ImportTextRequest):
    """
    Импорт аккаунтов из текста
    
    Форматы:
    - platform:username:password
    - username:password (требует default_platform)
    - platform:username:password:email
    - platform:username:password:email:proxy
    """
    manager = get_account_manager()
    
    imported, skipped, errors = manager.import_from_text(
        content=request.content,
        format_type=request.format_type,
        default_platform=request.default_platform
    )
    
    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:10],  # Первые 10 ошибок
        "total_errors": len(errors)
    }


@router.post("/import/file")
async def import_from_file(
    file: UploadFile = File(...),
    default_platform: Optional[str] = Form(None)
):
    """
    Импорт аккаунтов из файла
    
    Поддерживаемые форматы: .txt, .csv, .json
    """
    manager = get_account_manager()
    
    # Определяем тип файла
    filename = file.filename.lower()
    
    # Сохраняем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        if filename.endswith('.csv'):
            imported, skipped, errors = manager.import_from_csv(tmp_path)
        elif filename.endswith('.json'):
            imported, skipped, errors = manager.import_from_json(tmp_path)
        else:
            # Текстовый файл
            with open(tmp_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            imported, skipped, errors = manager.import_from_text(
                content=text_content,
                default_platform=default_platform
            )
        
        return {
            "imported": imported,
            "skipped": skipped,
            "errors": errors[:10],
            "total_errors": len(errors),
            "filename": file.filename
        }
        
    finally:
        os.unlink(tmp_path)


# ==================== COOKIES ====================

@router.post("/cookies/import")
async def import_cookies(request: ImportCookiesRequest):
    """
    Импорт cookies для аккаунта
    
    Поддерживаемые форматы:
    - JSON массив cookies
    - JSON объект {name: value}
    - Строка key=value; key2=value2
    """
    manager = get_account_manager()
    
    success = manager.import_cookies_from_text(request.account_id, request.cookies)
    
    if not success:
        raise HTTPException(status_code=400, detail="Ошибка импорта cookies")
    
    return {"success": True, "account_id": request.account_id}


@router.post("/cookies/import-file/{account_id}")
async def import_cookies_from_file(account_id: str, file: UploadFile = File(...)):
    """Импорт cookies из файла"""
    manager = get_account_manager()
    
    # Сохраняем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        success = manager.import_cookies_from_file(account_id, tmp_path)
        
        if not success:
            raise HTTPException(status_code=400, detail="Ошибка импорта cookies")
        
        return {"success": True, "account_id": account_id}
        
    finally:
        os.unlink(tmp_path)


@router.post("/cookies/bulk-import")
async def bulk_import_cookies(cookies_dir: str):
    """
    Массовый импорт cookies из директории
    
    Ожидает файлы в формате: platform_username.json
    """
    manager = get_account_manager()
    
    imported, failed = manager.bulk_import_cookies(cookies_dir)
    
    return {
        "imported": imported,
        "failed": failed
    }


@router.get("/cookies/{account_id}")
async def get_cookies(account_id: str, format_type: str = "json"):
    """
    Получение cookies аккаунта
    
    Форматы: json, netscape, header
    """
    manager = get_account_manager()
    
    cookies = manager.export_cookies(account_id, format_type)
    
    if cookies is None:
        raise HTTPException(status_code=404, detail="Cookies не найдены")
    
    return {"account_id": account_id, "format": format_type, "cookies": cookies}


# ==================== УПРАВЛЕНИЕ ====================

@router.post("/{account_id}/mark-used")
async def mark_account_used(account_id: str, success: bool = True):
    """Отметка использования аккаунта"""
    manager = get_account_manager()
    manager.mark_used(account_id, success)
    return {"success": True}


@router.post("/{account_id}/cooldown")
async def set_account_cooldown(account_id: str, request: SetCooldownRequest):
    """Установка cooldown для аккаунта"""
    manager = get_account_manager()
    manager.set_cooldown(account_id, request.minutes)
    return {"success": True, "cooldown_minutes": request.minutes}


@router.put("/{account_id}/status")
async def set_account_status(account_id: str, request: SetStatusRequest):
    """Установка статуса аккаунта"""
    manager = get_account_manager()
    
    if not manager.set_status(account_id, request.status):
        raise HTTPException(status_code=400, detail="Неверный статус")
    
    return {"success": True, "status": request.status}


@router.delete("/{account_id}")
async def delete_account(account_id: str):
    """Удаление аккаунта"""
    manager = get_account_manager()
    
    if not manager.delete_account(account_id):
        raise HTTPException(status_code=404, detail="Аккаунт не найден")
    
    return {"deleted": account_id}


@router.delete("/platform/{platform}")
async def delete_platform_accounts(platform: str):
    """Удаление всех аккаунтов платформы"""
    manager = get_account_manager()
    
    deleted = manager.delete_by_platform(platform)
    
    return {"platform": platform, "deleted": deleted}


# ==================== ЭКСПОРТ ====================

@router.get("/export/{format_type}")
async def export_accounts(format_type: str = "json", platform: Optional[str] = None):
    """
    Экспорт аккаунтов
    
    Форматы: json, csv, text
    """
    manager = get_account_manager()
    
    data = manager.export_accounts(format_type, platform)
    
    return {
        "format": format_type,
        "platform": platform,
        "data": data
    }
