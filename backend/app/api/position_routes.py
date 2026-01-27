"""
SEO Monster - Position Tracking API Routes
API эндпоинты для отслеживания позиций в поисковиках
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List

import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.position_tracker import get_position_tracker

router = APIRouter(prefix="/api/positions", tags=["positions"])


# Pydantic модели
class AddKeywordRequest(BaseModel):
    domain: str
    keyword: str
    target_url: Optional[str] = None


class ImportKeywordsRequest(BaseModel):
    domain: str
    keywords: str  # Ключевые слова, разделённые переносом строки


class CheckPositionsRequest(BaseModel):
    domain: Optional[str] = None


# API Endpoints

@router.get("/keywords")
async def get_keywords(domain: Optional[str] = None):
    """Получение списка отслеживаемых ключевых слов"""
    tracker = get_position_tracker()
    keywords = tracker.get_keywords(domain)
    return {"keywords": keywords, "total": len(keywords)}


@router.post("/keywords")
async def add_keyword(request: AddKeywordRequest):
    """Добавление ключевого слова для отслеживания"""
    tracker = get_position_tracker()
    result = tracker.add_keyword(request.domain, request.keyword, request.target_url)
    return result


@router.delete("/keywords/{keyword_id}")
async def remove_keyword(keyword_id: int):
    """Удаление ключевого слова"""
    tracker = get_position_tracker()
    return tracker.remove_keyword(keyword_id)


@router.post("/keywords/import")
async def import_keywords(request: ImportKeywordsRequest):
    """
    Импорт ключевых слов из текста
    Формат: одно ключевое слово на строку
    """
    tracker = get_position_tracker()
    result = tracker.import_keywords(request.keywords, request.domain)
    return result


@router.get("/latest")
async def get_latest_positions(domain: Optional[str] = None):
    """Получение последних позиций"""
    tracker = get_position_tracker()
    positions = tracker.get_latest_positions(domain)
    return {"positions": positions}


@router.get("/summary")
async def get_position_summary(domain: Optional[str] = None):
    """Получение сводки по позициям"""
    tracker = get_position_tracker()
    summary = tracker.get_position_summary(domain)
    return summary


@router.get("/history/{keyword_id}")
async def get_position_history(keyword_id: int, days: int = 30):
    """Получение истории позиций для ключевого слова"""
    tracker = get_position_tracker()
    history = tracker.get_position_history(keyword_id, days)
    return {"history": history}


@router.post("/check")
async def check_positions(request: CheckPositionsRequest, background_tasks: BackgroundTasks):
    """
    Запуск проверки позиций
    Выполняется в фоне, так как может занять время
    """
    tracker = get_position_tracker()
    
    # Для небольшого количества ключевых слов проверяем сразу
    keywords = tracker.get_keywords(request.domain)
    
    if len(keywords) == 0:
        return {"error": "No keywords to check"}
    
    if len(keywords) <= 5:
        # Проверяем сразу
        import asyncio
        results = await tracker.check_all_positions(request.domain)
        return {"status": "completed", "results": results}
    else:
        # Запускаем в фоне
        async def run_check():
            await tracker.check_all_positions(request.domain)
        
        background_tasks.add_task(run_check)
        return {
            "status": "started",
            "message": f"Checking {len(keywords)} keywords in background",
            "keywords_count": len(keywords)
        }


@router.get("/report")
async def get_position_report():
    """Получение секции отчёта по позициям"""
    tracker = get_position_tracker()
    report = tracker.generate_report_section()
    return {"report": report}
