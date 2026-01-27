"""
API роутер для Session Manager
Управление аккаунтами и сессиями
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os

# Добавляем путь к services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.session_manager import session_manager
from services.browser_session import browser_handler, LOGIN_URLS

router = APIRouter(prefix="/sessions", tags=["Sessions"])


# Pydantic модели
class AccountCreate(BaseModel):
    platform: str
    username: str
    password: str
    metadata: Optional[Dict] = None


class AccountsBulkImport(BaseModel):
    accounts_text: str
    default_platform: str = "auto"


class LoginRequest(BaseModel):
    account_id: str
    platform: Optional[str] = None
    custom_url: Optional[str] = None


class SessionSave(BaseModel):
    account_id: str


# Эндпоинты для аккаунтов
@router.post("/accounts", summary="Добавить аккаунт")
async def add_account(account: AccountCreate):
    """
    Добавление нового аккаунта.
    
    Пароль шифруется перед сохранением.
    """
    result = await session_manager.add_account(
        platform=account.platform,
        username=account.username,
        password=account.password,
        metadata=account.metadata
    )
    return result


@router.post("/accounts/bulk", summary="Массовый импорт аккаунтов")
async def bulk_import_accounts(data: AccountsBulkImport):
    """
    Массовый импорт аккаунтов.
    
    Форматы:
    - platform:username:password
    - username:password (платформа определяется автоматически)
    """
    result = await session_manager.import_accounts_bulk(
        accounts_text=data.accounts_text,
        default_platform=data.default_platform
    )
    return result


@router.get("/accounts", summary="Список аккаунтов")
async def list_accounts(platform: Optional[str] = None, status: Optional[str] = None):
    """
    Получение списка аккаунтов.
    
    Пароли не возвращаются в ответе.
    """
    accounts = await session_manager.list_accounts(platform=platform, status=status)
    return {"accounts": accounts, "total": len(accounts)}


@router.get("/accounts/{account_id}", summary="Информация об аккаунте")
async def get_account(account_id: str):
    """Получение информации об аккаунте."""
    account = await session_manager.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Убираем пароль из ответа
    account.pop("password", None)
    return account


@router.delete("/accounts/{account_id}", summary="Удалить аккаунт")
async def delete_account(account_id: str):
    """Удаление аккаунта и связанной сессии."""
    deleted = await session_manager.delete_account(account_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"status": "deleted", "account_id": account_id}


# Эндпоинты для сессий
@router.post("/login/open", summary="Открыть страницу входа")
async def open_login_page(request: LoginRequest):
    """
    Открывает браузер для ручного входа.
    
    После успешного входа вызовите /sessions/login/save для сохранения сессии.
    """
    # Определяем URL
    if request.custom_url:
        url = request.custom_url
    elif request.platform:
        url = LOGIN_URLS.get(request.platform.lower())
        if not url:
            raise HTTPException(status_code=400, detail=f"Unknown platform: {request.platform}")
    else:
        raise HTTPException(status_code=400, detail="Specify platform or custom_url")
    
    try:
        result = await browser_handler.open_login_page(
            account_id=request.account_id,
            url=url
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/save", summary="Сохранить сессию")
async def save_login_session(data: SessionSave):
    """
    Сохраняет сессию после успешного входа.
    
    Cookies и localStorage сохраняются в зашифрованном виде.
    """
    result = await browser_handler.save_browser_session(data.account_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to save session"))
    
    return result


@router.get("/session/{account_id}", summary="Получить сессию")
async def get_session(account_id: str):
    """Проверка наличия и валидности сессии."""
    session = await session_manager.load_session(account_id)
    
    if not session:
        return {"valid": False, "account_id": account_id}
    
    return {
        "valid": session.get("valid", False),
        "account_id": account_id,
        "saved_at": session.get("saved_at"),
        "expires_at": session.get("expires_at"),
        "cookies_count": len(session.get("cookies", []))
    }


@router.get("/random/{platform}", summary="Случайная активная сессия")
async def get_random_session(platform: str):
    """Получение случайной активной сессии для платформы."""
    result = await session_manager.get_random_active_session(platform)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"No active sessions for {platform}")
    
    # Не возвращаем чувствительные данные
    return {
        "account_id": result["account"]["id"],
        "platform": result["account"]["platform"],
        "username": result["account"]["username"],
        "session_valid": True
    }


# Эндпоинты для экспорта/импорта
@router.post("/export", summary="Экспорт сессий")
async def export_sessions(output_path: str = "data/sessions_backup.json"):
    """Экспорт всех аккаунтов и сессий для бэкапа."""
    result = await session_manager.export_sessions(output_path)
    return {"status": "exported", "file": result}


@router.post("/import", summary="Импорт сессий")
async def import_sessions(input_path: str):
    """Импорт аккаунтов и сессий из бэкапа."""
    result = await session_manager.import_sessions(input_path)
    return {"status": "imported", **result}


# Статистика
@router.get("/stats", summary="Статистика сессий")
async def get_stats():
    """Получение статистики по аккаунтам и сессиям."""
    return session_manager.get_stats()


# Список поддерживаемых платформ
@router.get("/platforms", summary="Список платформ")
async def list_platforms():
    """Список поддерживаемых платформ с URL для входа."""
    return {
        "platforms": [
            {"id": k, "name": k.title(), "login_url": v}
            for k, v in LOGIN_URLS.items()
        ]
    }
