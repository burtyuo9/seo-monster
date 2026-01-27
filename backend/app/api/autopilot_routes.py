"""
SEO Monster - Autopilot API Routes
API эндпоинты для автономного движка продвижения
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio

import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.autopilot_engine import get_autopilot_engine, CampaignStatus

router = APIRouter(prefix="/api/autopilot", tags=["autopilot"])


# Pydantic модели
class CreateCampaignRequest(BaseModel):
    domain: str
    settings: Optional[Dict] = None


class UpdateCampaignSettings(BaseModel):
    settings: Dict


# API Endpoints

@router.get("/stats")
async def get_autopilot_stats():
    """Общая статистика автопилота"""
    engine = get_autopilot_engine()
    return engine.get_stats()


@router.get("/campaigns")
async def get_all_campaigns():
    """Получение всех кампаний"""
    engine = get_autopilot_engine()
    campaigns = engine.get_all_campaigns()
    
    return [
        {
            "id": c.id,
            "domain": c.domain,
            "status": c.status.value if hasattr(c.status, 'value') else c.status,
            "stats": c.stats,
            "created_at": c.created_at,
            "last_activity": c.last_activity,
            "next_action": c.next_action
        }
        for c in campaigns
    ]


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Получение информации о кампании"""
    engine = get_autopilot_engine()
    campaign = engine.get_campaign(campaign_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    
    return {
        "id": campaign.id,
        "domain": campaign.domain,
        "status": campaign.status.value if hasattr(campaign.status, 'value') else campaign.status,
        "settings": campaign.settings,
        "stats": campaign.stats,
        "created_at": campaign.created_at,
        "last_activity": campaign.last_activity,
        "next_action": campaign.next_action,
        "learning_data": campaign.learning_data
    }


@router.post("/campaigns")
async def create_campaign(request: CreateCampaignRequest, background_tasks: BackgroundTasks):
    """
    Создание новой кампании продвижения
    
    После создания кампания автоматически начинает:
    1. Анализ сайта
    2. Анализ конкурентов
    3. Генерацию и публикацию контента
    4. Индексацию
    5. Отслеживание позиций
    """
    engine = get_autopilot_engine()
    
    # Проверяем что домен не пустой
    if not request.domain:
        raise HTTPException(status_code=400, detail="Домен обязателен")
    
    # Создаем кампанию
    campaign = engine.create_campaign(
        domain=request.domain,
        settings=request.settings
    )
    
    return {
        "id": campaign.id,
        "domain": campaign.domain,
        "status": campaign.status.value,
        "message": "Кампания создана. Используйте /start для запуска автопилота."
    }


@router.post("/campaigns/{campaign_id}/start")
async def start_campaign(campaign_id: str, background_tasks: BackgroundTasks):
    """Запуск автопилота для кампании"""
    engine = get_autopilot_engine()
    
    campaign = engine.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    
    # Запускаем в фоне
    background_tasks.add_task(engine.start_campaign, campaign_id)
    
    return {
        "campaign_id": campaign_id,
        "status": "starting",
        "message": "Автопилот запускается. Система начнет автоматическое продвижение."
    }


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Приостановка кампании"""
    engine = get_autopilot_engine()
    
    if not engine.pause_campaign(campaign_id):
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    
    return {"campaign_id": campaign_id, "status": "paused"}


@router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign(campaign_id: str, background_tasks: BackgroundTasks):
    """Возобновление кампании"""
    engine = get_autopilot_engine()
    
    campaign = engine.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    
    background_tasks.add_task(engine.resume_campaign, campaign_id)
    
    return {"campaign_id": campaign_id, "status": "resuming"}


@router.put("/campaigns/{campaign_id}/settings")
async def update_campaign_settings(campaign_id: str, request: UpdateCampaignSettings):
    """Обновление настроек кампании"""
    engine = get_autopilot_engine()
    
    campaign = engine.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    
    campaign.settings.update(request.settings)
    engine._save_campaigns()
    
    return {"campaign_id": campaign_id, "settings": campaign.settings}


@router.get("/campaigns/{campaign_id}/logs")
async def get_campaign_logs(campaign_id: str, limit: int = 100):
    """Получение логов кампании"""
    engine = get_autopilot_engine()
    
    logs = engine.get_campaign_logs(campaign_id, limit)
    return {"campaign_id": campaign_id, "logs": logs}


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Удаление кампании"""
    engine = get_autopilot_engine()
    
    # Сначала останавливаем
    engine.pause_campaign(campaign_id)
    
    if not engine.delete_campaign(campaign_id):
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    
    return {"deleted": campaign_id}


@router.get("/learning")
async def get_learning_data():
    """Получение данных обучения системы"""
    engine = get_autopilot_engine()
    
    return {
        "successful_strategies_count": len(engine.learning_data.get("successful_strategies", [])),
        "best_posting_times": engine.learning_data.get("best_posting_times", {}),
        "best_platforms": engine.learning_data.get("best_platforms", {}),
        "keyword_performance_domains": list(engine.learning_data.get("keyword_performance", {}).keys())
    }
