"""
API Routes для интеграции трекера с рекламными кампаниями
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.ads_tracker_integration import ads_tracker_integration, CloakingMode
from services.cloaking_system import cloaking_system

router = APIRouter(prefix="/api/ads-tracker", tags=["Ads-Tracker Integration"])


# Модели запросов
class CloakingRuleCreate(BaseModel):
    name: str
    mode: str = "safe_page"
    safe_page_url: str = ""
    redirect_url: str = ""
    target_platforms: List[str] = []
    blocked_ips: List[str] = []
    blocked_user_agents: List[str] = []
    allowed_countries: List[str] = []
    blocked_countries: List[str] = []


class PostbackCreate(BaseModel):
    name: str
    platform: str
    event_type: str
    url_template: str
    method: str = "GET"
    headers: Dict[str, str] = {}
    params: Dict[str, str] = {}


class TrackingLinkCreate(BaseModel):
    campaign_id: str
    base_url: str
    name: str = ""
    source: str = ""
    sub1: str = ""
    sub2: str = ""
    sub3: str = ""
    sub4: str = ""
    sub5: str = ""
    custom_params: Dict[str, str] = {}


class VisitorData(BaseModel):
    ip: str
    user_agent: str
    referrer: str = ""
    country: str = ""
    headers: Dict[str, str] = {}


class ConversionData(BaseModel):
    platform: str
    click_id: str
    value: float = 0.0
    currency: str = "USD"
    transaction_id: str = ""
    custom_data: Dict[str, Any] = {}


class SafePageCreate(BaseModel):
    name: str
    url: str
    html_content: str = ""
    page_type: str = "redirect"


class ListUpdate(BaseModel):
    ip: str = None
    user_agent: str = None


# ═══════════════════════════════════════════════════════════════
# КЛОАКИНГ
# ═══════════════════════════════════════════════════════════════

@router.get("/cloaking/stats")
async def get_cloaking_stats():
    """Получение статистики клоакинга"""
    integration_stats = ads_tracker_integration.get_integration_stats()
    cloaking_stats = cloaking_system.get_stats()
    return {
        "integration": integration_stats,
        "cloaking": cloaking_stats
    }


@router.get("/cloaking/rules")
async def get_cloaking_rules():
    """Получение правил клоакинга"""
    return {"rules": ads_tracker_integration.get_cloaking_rules()}


@router.post("/cloaking/rules")
async def create_cloaking_rule(rule: CloakingRuleCreate):
    """Создание правила клоакинга"""
    new_rule = ads_tracker_integration.create_cloaking_rule(
        name=rule.name,
        mode=rule.mode,
        safe_page_url=rule.safe_page_url,
        redirect_url=rule.redirect_url,
        target_platforms=rule.target_platforms,
        blocked_ips=rule.blocked_ips,
        blocked_user_agents=rule.blocked_user_agents,
        allowed_countries=rule.allowed_countries,
        blocked_countries=rule.blocked_countries
    )
    return {"success": True, "rule": new_rule}


@router.post("/cloaking/check")
async def check_cloaking(visitor: VisitorData):
    """Проверка посетителя через клоакинг"""
    # Проверка через расширенную систему
    decision = cloaking_system.make_decision({
        "ip": visitor.ip,
        "user_agent": visitor.user_agent,
        "referrer": visitor.referrer,
        "headers": visitor.headers
    })
    
    return {
        "is_bot": decision.is_bot,
        "is_moderator": decision.is_moderator,
        "action": decision.action,
        "reason": decision.reason,
        "moderator_type": decision.moderator_type,
        "confidence": decision.confidence,
        "checks_performed": decision.checks_performed,
        "redirect_url": decision.redirect_url
    }


@router.post("/cloaking/apply/{rule_id}")
async def apply_cloaking_rule(rule_id: str, visitor: VisitorData):
    """Применение правила клоакинга к посетителю"""
    result = ads_tracker_integration.apply_cloaking(rule_id, {
        "ip": visitor.ip,
        "user_agent": visitor.user_agent,
        "referrer": visitor.referrer,
        "country": visitor.country
    })
    return result


# ═══════════════════════════════════════════════════════════════
# БЕЗОПАСНЫЕ СТРАНИЦЫ
# ═══════════════════════════════════════════════════════════════

@router.get("/safe-pages")
async def get_safe_pages():
    """Получение списка безопасных страниц"""
    return {"pages": cloaking_system.get_safe_pages()}


@router.post("/safe-pages")
async def create_safe_page(page: SafePageCreate):
    """Создание безопасной страницы"""
    new_page = cloaking_system.create_safe_page(
        name=page.name,
        url=page.url,
        html_content=page.html_content,
        page_type=page.page_type
    )
    return {"success": True, "page": new_page}


@router.delete("/safe-pages/{page_id}")
async def delete_safe_page(page_id: str):
    """Удаление безопасной страницы"""
    success = cloaking_system.delete_safe_page(page_id)
    if not success:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"success": True}


# ═══════════════════════════════════════════════════════════════
# WHITELIST / BLACKLIST
# ═══════════════════════════════════════════════════════════════

@router.get("/lists")
async def get_lists():
    """Получение whitelist и blacklist"""
    return cloaking_system.get_lists()


@router.post("/whitelist/add")
async def add_to_whitelist(data: ListUpdate):
    """Добавление в whitelist"""
    cloaking_system.add_to_whitelist(ip=data.ip, user_agent=data.user_agent)
    return {"success": True}


@router.post("/whitelist/remove")
async def remove_from_whitelist(data: ListUpdate):
    """Удаление из whitelist"""
    cloaking_system.remove_from_whitelist(ip=data.ip, user_agent=data.user_agent)
    return {"success": True}


@router.post("/blacklist/add")
async def add_to_blacklist(data: ListUpdate):
    """Добавление в blacklist"""
    cloaking_system.add_to_blacklist(ip=data.ip, user_agent=data.user_agent)
    return {"success": True}


@router.post("/blacklist/remove")
async def remove_from_blacklist(data: ListUpdate):
    """Удаление из blacklist"""
    cloaking_system.remove_from_blacklist(ip=data.ip, user_agent=data.user_agent)
    return {"success": True}


# ═══════════════════════════════════════════════════════════════
# ПОСТБЭКИ
# ═══════════════════════════════════════════════════════════════

@router.get("/postbacks")
async def get_postbacks():
    """Получение списка постбэков"""
    return {"postbacks": ads_tracker_integration.get_postbacks()}


@router.post("/postbacks")
async def create_postback(postback: PostbackCreate):
    """Создание постбэка"""
    new_pb = ads_tracker_integration.create_postback(
        name=postback.name,
        platform=postback.platform,
        event_type=postback.event_type,
        url_template=postback.url_template,
        method=postback.method,
        headers=postback.headers,
        params=postback.params
    )
    return {"success": True, "postback": new_pb}


@router.get("/postbacks/templates")
async def get_postback_templates():
    """Получение шаблонов постбэков для популярных платформ"""
    return {"templates": ads_tracker_integration.get_postback_templates()}


@router.post("/postbacks/{postback_id}/send")
async def send_postback(postback_id: str, data: Dict[str, Any]):
    """Отправка постбэка"""
    result = await ads_tracker_integration.send_postback(postback_id, data)
    return result


@router.post("/conversions/send")
async def send_conversion(conversion: ConversionData):
    """Отправка конверсии во все активные постбэки платформы"""
    results = await ads_tracker_integration.send_conversion(
        platform=conversion.platform,
        conversion_data={
            "click_id": conversion.click_id,
            "value": conversion.value,
            "currency": conversion.currency,
            "transaction_id": conversion.transaction_id,
            **conversion.custom_data
        }
    )
    return {"success": True, "results": results}


# ═══════════════════════════════════════════════════════════════
# ТРЕКИНГОВЫЕ ССЫЛКИ
# ═══════════════════════════════════════════════════════════════

@router.post("/tracking-links")
async def create_tracking_link(link: TrackingLinkCreate):
    """Создание трекинговой ссылки"""
    new_link = ads_tracker_integration.generate_tracking_link(
        campaign_id=link.campaign_id,
        base_url=link.base_url,
        name=link.name,
        source=link.source,
        sub1=link.sub1,
        sub2=link.sub2,
        sub3=link.sub3,
        sub4=link.sub4,
        sub5=link.sub5,
        custom_params=link.custom_params
    )
    return {"success": True, "link": new_link}


@router.post("/tracking-links/{link_id}/click")
async def track_click(link_id: str, visitor: VisitorData):
    """Трекинг клика"""
    # Сначала проверяем через клоакинг
    decision = cloaking_system.make_decision({
        "ip": visitor.ip,
        "user_agent": visitor.user_agent,
        "referrer": visitor.referrer,
        "headers": visitor.headers
    })
    
    if decision.is_bot or decision.is_moderator:
        return {
            "success": False,
            "blocked": True,
            "reason": decision.reason,
            "redirect_url": decision.redirect_url
        }
    
    # Трекаем клик
    result = ads_tracker_integration.track_click(link_id, {
        "ip": visitor.ip,
        "user_agent": visitor.user_agent,
        "referrer": visitor.referrer,
        "country": visitor.country
    })
    
    return result


# ═══════════════════════════════════════════════════════════════
# ДЕТЕКЦИЯ МОДЕРАТОРОВ
# ═══════════════════════════════════════════════════════════════

@router.post("/detect-moderator")
async def detect_moderator(visitor: VisitorData):
    """Определение модератора рекламной сети"""
    moderator = ads_tracker_integration.detect_moderator(
        ip=visitor.ip,
        user_agent=visitor.user_agent,
        referrer=visitor.referrer
    )
    
    is_moderator = ads_tracker_integration.is_moderator(
        ip=visitor.ip,
        user_agent=visitor.user_agent,
        referrer=visitor.referrer
    )
    
    return {
        "is_moderator": is_moderator,
        "moderator_type": moderator.value if moderator else None
    }


# ═══════════════════════════════════════════════════════════════
# ОБЩАЯ СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

@router.get("/stats")
async def get_integration_stats():
    """Получение общей статистики интеграции"""
    return ads_tracker_integration.get_integration_stats()
