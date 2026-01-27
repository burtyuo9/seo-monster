"""
SEO Monster - AI Chat API Routes
API эндпоинты для чат-интерфейса
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.ai_chat_service import get_chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Pydantic модели
class ChatMessageRequest(BaseModel):
    session_id: str
    message: str


class CreateSessionRequest(BaseModel):
    session_id: Optional[str] = None


# API Endpoints

@router.post("/session")
async def create_session(request: CreateSessionRequest = None):
    """Создание новой сессии чата"""
    service = get_chat_service()
    
    session_id = None
    if request:
        session_id = request.session_id
    
    new_session_id = service.create_session(session_id)
    
    return {
        "session_id": new_session_id,
        "message": "Сессия создана. Начните диалог!"
    }


@router.post("/message")
async def send_message(request: ChatMessageRequest):
    """
    Отправка сообщения в чат
    
    Система понимает естественный язык и выполняет команды:
    - "Создай кампанию для example.com"
    - "Покажи статистику"
    - "Сгенерируй контент на тему SEO"
    - И многое другое
    """
    service = get_chat_service()
    
    result = await service.chat(request.session_id, request.message)
    
    return {
        "session_id": request.session_id,
        "response": result["response"],
        "action_result": result.get("action_result"),
        "suggestions": result.get("suggestions", [])
    }


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """Получение истории чата"""
    service = get_chat_service()
    
    history = service.get_history(session_id, limit)
    
    return {
        "session_id": session_id,
        "messages": history
    }


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Очистка сессии чата"""
    service = get_chat_service()
    
    if not service.clear_session(session_id):
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    return {"cleared": session_id}


@router.get("/help")
async def get_help():
    """Получение справки по командам"""
    return {
        "commands": [
            {
                "category": "Кампании",
                "examples": [
                    "Создай кампанию для example.com",
                    "Запусти кампанию",
                    "Покажи кампании",
                    "Приостанови кампанию"
                ]
            },
            {
                "category": "Аккаунты",
                "examples": [
                    "Покажи статистику аккаунтов",
                    "Импортируй аккаунты"
                ]
            },
            {
                "category": "Контент",
                "examples": [
                    "Сгенерируй контент на тему X",
                    "Напиши статью про SEO"
                ]
            },
            {
                "category": "Индексация",
                "examples": [
                    "Проиндексируй https://example.com/page",
                    "Отправь на индексацию"
                ]
            },
            {
                "category": "Общее",
                "examples": [
                    "Покажи статистику",
                    "Помощь"
                ]
            }
        ]
    }
