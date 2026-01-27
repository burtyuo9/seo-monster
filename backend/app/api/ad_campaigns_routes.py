"""
SEO Monster - Ad Campaigns API Routes
API для управления рекламными кампаниями
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.ad_campaigns_service import ad_campaigns_service
from services.tds_ads_integration import tds_ads_integration


router = APIRouter(prefix="/api/ad-campaigns", tags=["Ad Campaigns"])


# ==================== МОДЕЛИ ====================

class ModuleToggle(BaseModel):
    enabled: bool

class AutoModeToggle(BaseModel):
    enabled: bool

class AddAccountRequest(BaseModel):
    platform: str
    name: str
    credentials: Dict[str, str]
    currency: str = "USD"
    daily_budget_limit: float = 0.0

class UpdateBalanceRequest(BaseModel):
    balance: float

class CreateCampaignRequest(BaseModel):
    account_id: str
    domain_id: str
    name: str
    campaign_type: str = "ads_only"
    budget: float
    daily_budget: float
    keywords: List[str] = []
    geo_targets: List[str] = []
    language_targets: List[str] = []
    landing_url: str
    ad_texts: List[Dict[str, str]] = []
    white_list: List[str] = []
    black_list: List[str] = []
    cloaking_enabled: bool = True
    auto_keywords: bool = True

class UpdateBudgetRequest(BaseModel):
    budget: Optional[float] = None
    daily_budget: Optional[float] = None

class AddKeywordsRequest(BaseModel):
    keywords: List[str]

class UpdateListsRequest(BaseModel):
    white_list: Optional[List[str]] = None
    black_list: Optional[List[str]] = None

class TrackClickRequest(BaseModel):
    ad_campaign_id: str
    click_id: str
    is_fraud: bool = False
    cpc: float = 0.0
    source: str = "unknown"

class RecordConversionRequest(BaseModel):
    click_id: str
    revenue: float = 0.0


# ==================== УПРАВЛЕНИЕ МОДУЛЕМ ====================

@router.get("/status")
async def get_status():
    """Получить статус модуля"""
    return await ad_campaigns_service.get_status()

@router.post("/enable")
async def enable_module():
    """Включить модуль"""
    return await ad_campaigns_service.enable()

@router.post("/disable")
async def disable_module():
    """Выключить модуль"""
    return await ad_campaigns_service.disable()

@router.post("/auto-mode")
async def set_auto_mode(request: AutoModeToggle):
    """Установить автоматический режим"""
    return await ad_campaigns_service.set_auto_mode(request.enabled)


# ==================== АККАУНТЫ ====================

@router.get("/accounts")
async def get_accounts(platform: Optional[str] = None):
    """Получить список аккаунтов"""
    return await ad_campaigns_service.get_accounts(platform)

@router.post("/accounts")
async def add_account(request: AddAccountRequest):
    """Добавить рекламный аккаунт"""
    return await ad_campaigns_service.add_account(
        platform=request.platform,
        name=request.name,
        credentials=request.credentials,
        currency=request.currency,
        daily_budget_limit=request.daily_budget_limit
    )

@router.put("/accounts/{account_id}/balance")
async def update_balance(account_id: str, request: UpdateBalanceRequest):
    """Обновить баланс аккаунта"""
    return await ad_campaigns_service.update_account_balance(account_id, request.balance)

@router.delete("/accounts/{account_id}")
async def delete_account(account_id: str):
    """Удалить аккаунт"""
    return await ad_campaigns_service.delete_account(account_id)


# ==================== КАМПАНИИ ====================

@router.get("/campaigns")
async def get_campaigns(
    domain_id: Optional[str] = None,
    account_id: Optional[str] = None,
    status: Optional[str] = None
):
    """Получить список кампаний"""
    return await ad_campaigns_service.get_campaigns(domain_id, account_id, status)

@router.post("/campaigns")
async def create_campaign(request: CreateCampaignRequest):
    """Создать рекламную кампанию"""
    return await ad_campaigns_service.create_campaign(
        account_id=request.account_id,
        domain_id=request.domain_id,
        name=request.name,
        campaign_type=request.campaign_type,
        budget=request.budget,
        daily_budget=request.daily_budget,
        keywords=request.keywords,
        geo_targets=request.geo_targets,
        language_targets=request.language_targets,
        landing_url=request.landing_url,
        ad_texts=request.ad_texts,
        white_list=request.white_list,
        black_list=request.black_list,
        cloaking_enabled=request.cloaking_enabled,
        auto_keywords=request.auto_keywords
    )

@router.post("/campaigns/{campaign_id}/start")
async def start_campaign(campaign_id: str):
    """Запустить кампанию"""
    return await ad_campaigns_service.start_campaign(campaign_id)

@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Приостановить кампанию"""
    return await ad_campaigns_service.pause_campaign(campaign_id)

@router.put("/campaigns/{campaign_id}/budget")
async def update_campaign_budget(campaign_id: str, request: UpdateBudgetRequest):
    """Обновить бюджет кампании"""
    return await ad_campaigns_service.update_campaign_budget(
        campaign_id,
        budget=request.budget,
        daily_budget=request.daily_budget
    )

@router.post("/campaigns/{campaign_id}/keywords")
async def add_keywords(campaign_id: str, request: AddKeywordsRequest):
    """Добавить ключевые слова"""
    return await ad_campaigns_service.add_keywords(campaign_id, request.keywords)

@router.put("/campaigns/{campaign_id}/lists")
async def update_lists(campaign_id: str, request: UpdateListsRequest):
    """Обновить белый/чёрный списки"""
    return await ad_campaigns_service.update_white_black_lists(
        campaign_id,
        white_list=request.white_list,
        black_list=request.black_list
    )


# ==================== СТАТИСТИКА ====================

@router.get("/stats")
async def get_stats():
    """Получить общую статистику"""
    return await ad_campaigns_service.get_stats()

@router.get("/campaigns/{campaign_id}/stats")
async def get_campaign_stats(campaign_id: str):
    """Получить статистику кампании"""
    return await ad_campaigns_service.get_campaign_stats(campaign_id)


# ==================== ИНТЕГРАЦИЯ С ТРЕКЕРОМ ====================

@router.post("/tracker/link")
async def link_to_tracker(ad_campaign_id: str, tds_campaign_id: str):
    """Связать рекламную кампанию с TDS"""
    return tds_ads_integration.link_ad_campaign_to_tds(ad_campaign_id, tds_campaign_id)

@router.post("/tracker/click")
async def track_click(request: TrackClickRequest):
    """Отслеживание клика"""
    return tds_ads_integration.track_ad_click({
        "ad_campaign_id": request.ad_campaign_id,
        "click_id": request.click_id,
        "is_fraud": request.is_fraud,
        "cpc": request.cpc,
        "source": request.source
    })

@router.post("/tracker/conversion")
async def record_conversion(request: RecordConversionRequest):
    """Запись конверсии"""
    return tds_ads_integration.record_conversion(request.click_id, request.revenue)

@router.get("/tracker/campaign-stats/{ad_campaign_id}")
async def get_tracker_campaign_stats(ad_campaign_id: str):
    """Получить статистику кампании из трекера"""
    return tds_ads_integration.get_campaign_stats(ad_campaign_id)

@router.get("/tracker/fraud-stats")
async def get_fraud_stats():
    """Получить статистику фрода"""
    return tds_ads_integration.get_fraud_stats()

@router.get("/tracker/generate-url")
async def generate_tracking_url(landing_url: str, ad_campaign_id: str, source: str = "ads"):
    """Генерация tracking URL"""
    return {
        "tracking_url": tds_ads_integration.generate_tracking_url(
            landing_url, ad_campaign_id, source
        )
    }
