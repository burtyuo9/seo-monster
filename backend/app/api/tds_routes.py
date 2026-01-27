"""
SEO Monster - TDS API Routes
API для Traffic Distribution System
"""

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

router = APIRouter(prefix="/api/tds", tags=["TDS"])

# Импорт сервисов
from services.tds_core import get_tds_core
from services.tds_filters import get_tds_filters
from services.tds_flows import get_tds_flows
from services.tds_landings import get_tds_landings
from services.tds_antifraud import get_tds_antifraud


# ═══════════════════════════════════════════════════════════════
# МОДЕЛИ ЗАПРОСОВ
# ═══════════════════════════════════════════════════════════════

class CampaignCreate(BaseModel):
    name: str
    domain: str = ""
    traffic_source: str = ""
    cost_model: str = "cpc"
    cost_value: float = 0

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    status: Optional[str] = None
    traffic_source: Optional[str] = None

class FilterCreate(BaseModel):
    name: str
    filter_type: str
    mode: str = "include"
    values: List[str] = []

class FlowCreate(BaseModel):
    name: str
    campaign_id: str
    schema: str = "direct"

class FlowPathCreate(BaseModel):
    name: str
    action: str
    redirect_url: str = ""
    redirect_type: str = "302"
    landing_id: str = ""
    offer_id: str = ""
    weight: int = 100

class LandingCreate(BaseModel):
    name: str
    url: str
    landing_type: str = "url"

class OfferCreate(BaseModel):
    name: str
    url: str
    payout: float = 0
    payout_type: str = "cpa"
    countries: List[str] = []

class OfferGroupCreate(BaseModel):
    name: str
    offer_ids: List[str] = []
    rotation_mode: str = "weight"

class BlacklistEntry(BaseModel):
    entry_type: str
    value: str
    reason: str = ""
    hours: int = 0

class AntifraudSettings(BaseModel):
    enabled: Optional[bool] = None
    block_bots: Optional[bool] = None
    block_empty_ua: Optional[bool] = None
    block_datacenters: Optional[bool] = None
    max_clicks_per_ip: Optional[int] = None
    max_clicks_per_ip_daily: Optional[int] = None


# ═══════════════════════════════════════════════════════════════
# КАМПАНИИ
# ═══════════════════════════════════════════════════════════════

@router.get("/campaigns")
async def get_campaigns(status: str = None):
    """Получение списка кампаний"""
    tds = get_tds_core()
    return tds.get_campaigns(status=status)

@router.post("/campaigns")
async def create_campaign(data: CampaignCreate):
    """Создание кампании"""
    tds = get_tds_core()
    return tds.create_campaign(
        name=data.name,
        domain=data.domain,
        traffic_source=data.traffic_source,
        cost_model=data.cost_model,
        cost_value=data.cost_value
    )

@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Получение кампании"""
    tds = get_tds_core()
    campaign = tds.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    return campaign

@router.put("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, data: CampaignUpdate):
    """Обновление кампании"""
    tds = get_tds_core()
    return tds.update_campaign(campaign_id, **data.dict(exclude_none=True))

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Удаление кампании"""
    tds = get_tds_core()
    return tds.delete_campaign(campaign_id)

@router.get("/campaigns/{campaign_id}/stats")
async def get_campaign_stats(campaign_id: str, period: str = "today"):
    """Получение статистики кампании"""
    tds = get_tds_core()
    return tds.get_campaign_stats(campaign_id, period)


# ═══════════════════════════════════════════════════════════════
# КЛИКИ И ТРЕКИНГ
# ═══════════════════════════════════════════════════════════════

@router.get("/click/{campaign_id}")
async def track_click(campaign_id: str, request: Request):
    """
    Основной endpoint для трекинга кликов
    Перенаправляет посетителя согласно настройкам кампании
    """
    tds = get_tds_core()
    flows = get_tds_flows()
    landings = get_tds_landings()
    antifraud = get_tds_antifraud()
    
    # Сбор данных посетителя
    visitor_data = {
        "ip": request.client.host if request.client else "",
        "user_agent": request.headers.get("user-agent", ""),
        "referrer": request.headers.get("referer", ""),
        "accept_language": request.headers.get("accept-language", ""),
        "campaign_id": campaign_id
    }
    
    # Получение query параметров
    for key, value in request.query_params.items():
        if key.startswith("sub"):
            visitor_data[f"sub_id_{key[-1]}"] = value
        else:
            visitor_data[key] = value
    
    # Проверка антифрода
    passed, reason, action = antifraud.check_visitor(visitor_data)
    if not passed:
        if action == "redirect" and antifraud.settings.fraud_redirect_url:
            return RedirectResponse(antifraud.settings.fraud_redirect_url, status_code=302)
        return HTMLResponse("<html><body>Access Denied</body></html>", status_code=403)
    
    # Регистрация клика
    click = tds.track_click(campaign_id, visitor_data)
    if "error" in click:
        return HTMLResponse("<html><body>Campaign not found</body></html>", status_code=404)
    
    visitor_data["click_id"] = click.get("click_id", "")
    
    # Получение потока для кампании
    flow_id = flows.get_flow_for_campaign(campaign_id, visitor_data)
    
    if not flow_id:
        # Нет потока - показываем 404
        return HTMLResponse("<html><body>Not Found</body></html>", status_code=404)
    
    # Обработка клика через поток
    result = flows.process_click(flow_id, visitor_data)
    
    # Выполнение действия
    if result["action"] == "redirect":
        redirect_type = result.get("redirect_type", "302")
        url = result.get("url", "")
        
        if redirect_type == "301":
            return RedirectResponse(url, status_code=301)
        elif redirect_type == "302":
            return RedirectResponse(url, status_code=302)
        elif redirect_type == "meta":
            return HTMLResponse(f'''
                <html><head>
                <meta http-equiv="refresh" content="0;url={url}">
                </head><body></body></html>
            ''')
        elif redirect_type == "js":
            return HTMLResponse(f'''
                <html><head>
                <script>window.location.href="{url}";</script>
                </head><body></body></html>
            ''')
        else:
            return RedirectResponse(url, status_code=302)
    
    elif result["action"] == "landing":
        landing_id = result.get("landing_id", "")
        landing = landings.get_landing(landing_id)
        if landing:
            landings.record_landing_click(landing_id)
            url = landings.build_landing_url(landing_id, visitor_data)
            return RedirectResponse(url, status_code=302)
    
    elif result["action"] == "offer":
        offer_id = result.get("offer_id", "")
        offer = landings.get_offer(offer_id)
        if offer:
            landings.record_offer_click(offer_id)
            url = landings.build_offer_url(offer_id, visitor_data)
            return RedirectResponse(url, status_code=302)
    
    elif result["action"] == "show_html":
        return HTMLResponse(result.get("html", ""))
    
    elif result["action"] == "block":
        return HTMLResponse("<html><body>Access Denied</body></html>", status_code=403)
    
    # По умолчанию - 404
    return HTMLResponse("<html><body>Not Found</body></html>", status_code=404)


@router.get("/lp_click/{click_id}")
async def track_lp_click(click_id: str, request: Request):
    """Трекинг клика на лендинге (LP Click)"""
    tds = get_tds_core()
    landings = get_tds_landings()
    
    # Получение клика
    click = tds.get_click(click_id)
    if not click:
        return HTMLResponse("<html><body>Click not found</body></html>", status_code=404)
    
    # Обновление LP Click
    tds.update_click(click_id, lp_click=True)
    
    # Получение оффера и редирект
    offer_id = request.query_params.get("offer_id", "")
    if offer_id:
        offer = landings.get_offer(offer_id)
        if offer:
            landings.record_offer_click(offer_id)
            visitor_data = {
                "click_id": click_id,
                "sub_id": click.get("sub_id", "")
            }
            url = landings.build_offer_url(offer_id, visitor_data)
            return RedirectResponse(url, status_code=302)
    
    return HTMLResponse("<html><body>Offer not found</body></html>", status_code=404)


@router.post("/postback")
async def postback(request: Request):
    """Обработка постбэка (конверсии)"""
    tds = get_tds_core()
    landings = get_tds_landings()
    
    # Получение параметров
    params = dict(request.query_params)
    
    click_id = params.get("click_id", params.get("clickid", ""))
    status = params.get("status", "lead")
    payout = float(params.get("payout", params.get("sum", 0)))
    
    if not click_id:
        return {"success": False, "error": "click_id required"}
    
    # Регистрация конверсии
    result = tds.track_conversion(click_id, status, payout)
    
    # Обновление статистики оффера
    click = tds.get_click(click_id)
    if click and click.get("offer_id"):
        landings.record_offer_conversion(click["offer_id"], payout)
    
    return result


@router.get("/clicks")
async def get_clicks(campaign_id: str = None, limit: int = 100):
    """Получение списка кликов"""
    tds = get_tds_core()
    return tds.get_clicks(campaign_id=campaign_id, limit=limit)


# ═══════════════════════════════════════════════════════════════
# ФИЛЬТРЫ
# ═══════════════════════════════════════════════════════════════

@router.get("/filters")
async def get_filters(filter_type: str = None):
    """Получение списка фильтров"""
    filters = get_tds_filters()
    return filters.get_filters(filter_type=filter_type)

@router.post("/filters")
async def create_filter(data: FilterCreate):
    """Создание фильтра"""
    filters = get_tds_filters()
    return filters.create_filter(
        name=data.name,
        filter_type=data.filter_type,
        mode=data.mode,
        values=data.values
    )

@router.get("/filters/{filter_id}")
async def get_filter(filter_id: str):
    """Получение фильтра"""
    filters = get_tds_filters()
    f = filters.get_filter(filter_id)
    if not f:
        raise HTTPException(status_code=404, detail="Фильтр не найден")
    return f

@router.delete("/filters/{filter_id}")
async def delete_filter(filter_id: str):
    """Удаление фильтра"""
    filters = get_tds_filters()
    return filters.delete_filter(filter_id)


# ═══════════════════════════════════════════════════════════════
# ПОТОКИ
# ═══════════════════════════════════════════════════════════════

@router.get("/flows")
async def get_flows(campaign_id: str = None):
    """Получение списка потоков"""
    flows = get_tds_flows()
    return flows.get_flows(campaign_id=campaign_id)

@router.post("/flows")
async def create_flow(data: FlowCreate):
    """Создание потока"""
    flows = get_tds_flows()
    return flows.create_flow(
        name=data.name,
        campaign_id=data.campaign_id,
        schema=data.schema
    )

@router.get("/flows/{flow_id}")
async def get_flow(flow_id: str):
    """Получение потока"""
    flows = get_tds_flows()
    flow = flows.get_flow(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Поток не найден")
    return flow

@router.delete("/flows/{flow_id}")
async def delete_flow(flow_id: str):
    """Удаление потока"""
    flows = get_tds_flows()
    return flows.delete_flow(flow_id)

@router.post("/flows/{flow_id}/paths")
async def add_flow_path(flow_id: str, data: FlowPathCreate):
    """Добавление пути в поток"""
    flows = get_tds_flows()
    return flows.add_path(
        flow_id=flow_id,
        name=data.name,
        action=data.action,
        redirect_url=data.redirect_url,
        redirect_type=data.redirect_type,
        landing_id=data.landing_id,
        offer_id=data.offer_id,
        weight=data.weight
    )

@router.get("/flows/{flow_id}/stats")
async def get_flow_stats(flow_id: str):
    """Получение статистики потока"""
    flows = get_tds_flows()
    return flows.get_flow_stats(flow_id)


# ═══════════════════════════════════════════════════════════════
# ЛЕНДИНГИ
# ═══════════════════════════════════════════════════════════════

@router.get("/landings")
async def get_landings(status: str = None):
    """Получение списка лендингов"""
    landings = get_tds_landings()
    return landings.get_landings(status=status)

@router.post("/landings")
async def create_landing(data: LandingCreate):
    """Создание лендинга"""
    landings = get_tds_landings()
    return landings.create_landing(
        name=data.name,
        url=data.url,
        landing_type=data.landing_type
    )

@router.get("/landings/{landing_id}")
async def get_landing(landing_id: str):
    """Получение лендинга"""
    landings = get_tds_landings()
    landing = landings.get_landing(landing_id)
    if not landing:
        raise HTTPException(status_code=404, detail="Лендинг не найден")
    return landing

@router.delete("/landings/{landing_id}")
async def delete_landing(landing_id: str):
    """Удаление лендинга"""
    landings = get_tds_landings()
    return landings.delete_landing(landing_id)

@router.get("/landings/stats/summary")
async def get_landings_stats():
    """Получение статистики лендингов"""
    landings = get_tds_landings()
    return landings.get_landings_stats()


# ═══════════════════════════════════════════════════════════════
# ОФФЕРЫ
# ═══════════════════════════════════════════════════════════════

@router.get("/offers")
async def get_offers(status: str = None):
    """Получение списка офферов"""
    landings = get_tds_landings()
    return landings.get_offers(status=status)

@router.post("/offers")
async def create_offer(data: OfferCreate):
    """Создание оффера"""
    landings = get_tds_landings()
    return landings.create_offer(
        name=data.name,
        url=data.url,
        payout=data.payout,
        payout_type=data.payout_type,
        countries=data.countries
    )

@router.get("/offers/{offer_id}")
async def get_offer(offer_id: str):
    """Получение оффера"""
    landings = get_tds_landings()
    offer = landings.get_offer(offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Оффер не найден")
    return offer

@router.delete("/offers/{offer_id}")
async def delete_offer(offer_id: str):
    """Удаление оффера"""
    landings = get_tds_landings()
    return landings.delete_offer(offer_id)

@router.get("/offers/stats/summary")
async def get_offers_stats():
    """Получение статистики офферов"""
    landings = get_tds_landings()
    return landings.get_offers_stats()


# ═══════════════════════════════════════════════════════════════
# ГРУППЫ ОФФЕРОВ
# ═══════════════════════════════════════════════════════════════

@router.get("/offer-groups")
async def get_offer_groups():
    """Получение списка групп офферов"""
    landings = get_tds_landings()
    return landings.get_offer_groups()

@router.post("/offer-groups")
async def create_offer_group(data: OfferGroupCreate):
    """Создание группы офферов"""
    landings = get_tds_landings()
    return landings.create_offer_group(
        name=data.name,
        offer_ids=data.offer_ids,
        rotation_mode=data.rotation_mode
    )


# ═══════════════════════════════════════════════════════════════
# АНТИФРОД
# ═══════════════════════════════════════════════════════════════

@router.get("/antifraud/settings")
async def get_antifraud_settings():
    """Получение настроек антифрода"""
    antifraud = get_tds_antifraud()
    return antifraud.get_settings()

@router.put("/antifraud/settings")
async def update_antifraud_settings(data: AntifraudSettings):
    """Обновление настроек антифрода"""
    antifraud = get_tds_antifraud()
    return antifraud.update_settings(**data.dict(exclude_none=True))

@router.get("/antifraud/blacklist")
async def get_blacklist(entry_type: str = None):
    """Получение чёрного списка"""
    antifraud = get_tds_antifraud()
    return antifraud.get_blacklist(entry_type=entry_type)

@router.post("/antifraud/blacklist")
async def add_to_blacklist(data: BlacklistEntry):
    """Добавление в чёрный список"""
    antifraud = get_tds_antifraud()
    return antifraud.add_to_blacklist(
        entry_type=data.entry_type,
        value=data.value,
        reason=data.reason,
        hours=data.hours
    )

@router.delete("/antifraud/blacklist/{entry_id}")
async def remove_from_blacklist(entry_id: str):
    """Удаление из чёрного списка"""
    antifraud = get_tds_antifraud()
    return antifraud.remove_from_blacklist(entry_id)

@router.get("/antifraud/stats")
async def get_antifraud_stats(hours: int = 24):
    """Получение статистики антифрода"""
    antifraud = get_tds_antifraud()
    return antifraud.get_fraud_stats(hours=hours)

@router.get("/antifraud/log")
async def get_fraud_log(limit: int = 100, action: str = None):
    """Получение лога фрода"""
    antifraud = get_tds_antifraud()
    return antifraud.get_fraud_log(limit=limit, action=action)


# ═══════════════════════════════════════════════════════════════
# ОБЩАЯ СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

@router.get("/stats/dashboard")
async def get_dashboard_stats():
    """Получение статистики для дашборда"""
    tds = get_tds_core()
    landings = get_tds_landings()
    antifraud = get_tds_antifraud()
    
    return {
        "campaigns": tds.get_stats(),
        "landings": landings.get_landings_stats(),
        "offers": landings.get_offers_stats(),
        "antifraud": antifraud.get_fraud_stats(hours=24)
    }


# ═══════════════════════════════════════════════════════════════
# РАСШИРЕННАЯ ДЕТЕКЦИЯ БОТОВ (Keitaro-style)
# ═══════════════════════════════════════════════════════════════

from services.tds_bot_detector import bot_detector, VisitorProfile
from services.tds_traffic_filter import traffic_filter
from services.tds_routing import traffic_router
from services.tds_statistics import traffic_statistics


class AdvancedVisitorCheck(BaseModel):
    ip: str
    user_agent: str = ""
    accept_language: str = ""
    referrer: str = ""
    screen_width: int = 0
    screen_height: int = 0
    has_webgl: bool = True
    has_canvas: bool = True
    time_on_page: float = 0.0
    mouse_movements: int = 0
    fingerprint: str = ""


@router.post("/bot-check")
async def advanced_bot_check(request: AdvancedVisitorCheck):
    """Расширенная проверка на бота"""
    visitor = VisitorProfile(
        ip=request.ip,
        user_agent=request.user_agent,
        accept_language=request.accept_language,
        referrer=request.referrer,
        screen_width=request.screen_width,
        screen_height=request.screen_height,
        has_webgl=request.has_webgl,
        has_canvas=request.has_canvas,
        time_on_page=request.time_on_page,
        mouse_movements=request.mouse_movements,
        fingerprint=request.fingerprint
    )
    
    result = bot_detector.analyze_visitor(visitor)
    
    return {
        "is_bot": result.is_bot,
        "score": result.total_score,
        "confidence": result.confidence,
        "category": result.category,
        "recommendation": result.recommendation,
        "reasons": result.reasons,
        "checks_passed": result.checks_passed,
        "checks_failed": result.checks_failed
    }


@router.get("/bot-detection/stats")
async def get_bot_detection_stats():
    """Статистика детекции ботов"""
    return bot_detector.get_stats()


@router.post("/bot-detection/mark-bot")
async def mark_visitor_as_bot(fingerprint: str, ip: str = ""):
    """Пометить посетителя как бота"""
    bot_detector.mark_as_bot(fingerprint, ip)
    return {"success": True}


@router.post("/bot-detection/mark-human")
async def mark_visitor_as_human(fingerprint: str):
    """Пометить посетителя как человека"""
    bot_detector.mark_as_human(fingerprint)
    return {"success": True}


@router.get("/bot-detection/js-challenge")
async def get_js_challenge_script():
    """Получить JS скрипт для проверки посетителя"""
    return {"script": bot_detector.generate_js_challenge()}


# ═══════════════════════════════════════════════════════════════
# РАСШИРЕННАЯ СТАТИСТИКА (Keitaro-style)
# ═══════════════════════════════════════════════════════════════

@router.get("/stats/overview")
async def get_stats_overview():
    """Общий обзор статистики"""
    return traffic_statistics.get_overview()


@router.get("/stats/realtime")
async def get_realtime_stats(minutes: int = 60):
    """Статистика в реальном времени"""
    return traffic_statistics.get_realtime_stats(minutes)


@router.get("/stats/period")
async def get_stats_by_period(start_date: str, end_date: str):
    """Статистика за период"""
    return traffic_statistics.get_stats_by_period(start_date, end_date)


@router.get("/stats/countries")
async def get_stats_by_country(start_date: str = "", end_date: str = ""):
    """Статистика по странам"""
    return {"countries": traffic_statistics.get_stats_by_country(start_date, end_date)}


@router.get("/stats/browsers")
async def get_stats_by_browser(start_date: str = "", end_date: str = ""):
    """Статистика по браузерам"""
    return {"browsers": traffic_statistics.get_stats_by_browser(start_date, end_date)}


@router.get("/stats/os")
async def get_stats_by_os(start_date: str = "", end_date: str = ""):
    """Статистика по ОС"""
    return {"os": traffic_statistics.get_stats_by_os(start_date, end_date)}


@router.get("/stats/devices")
async def get_stats_by_device(start_date: str = "", end_date: str = ""):
    """Статистика по устройствам"""
    return {"devices": traffic_statistics.get_stats_by_device(start_date, end_date)}


@router.get("/stats/referrers")
async def get_stats_by_referrer(start_date: str = "", end_date: str = ""):
    """Статистика по рефереррам"""
    return {"referrers": traffic_statistics.get_stats_by_referrer(start_date, end_date)}


@router.get("/stats/hourly")
async def get_hourly_stats(date: str = ""):
    """Почасовая статистика"""
    return {"hourly": traffic_statistics.get_hourly_stats(date)}


# ═══════════════════════════════════════════════════════════════
# РАСШИРЕННАЯ МАРШРУТИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

@router.get("/routing/landings")
async def get_routing_landings():
    """Получение лендингов маршрутизации"""
    return {"landings": traffic_router.get_landings()}


@router.get("/routing/offers")
async def get_routing_offers():
    """Получение офферов маршрутизации"""
    return {"offers": traffic_router.get_offers()}


@router.get("/routing/rules")
async def get_routing_rules():
    """Получение правил маршрутизации"""
    return {"rules": traffic_router.get_rules()}


@router.get("/routing/stats")
async def get_routing_stats():
    """Статистика маршрутизации"""
    return traffic_router.get_stats()


@router.post("/routing/route")
async def route_visitor(visitor_data: Dict):
    """Маршрутизация посетителя"""
    return traffic_router.route_visitor(visitor_data)


# ═══════════════════════════════════════════════════════════════
# РАСШИРЕННЫЕ ФИЛЬТРЫ
# ═══════════════════════════════════════════════════════════════

@router.get("/traffic-filters")
async def get_traffic_filters():
    """Получение фильтров трафика"""
    return {"filters": traffic_filter.get_filters()}


@router.get("/traffic-flows")
async def get_traffic_flows():
    """Получение потоков трафика"""
    return {"flows": traffic_filter.get_flows()}


@router.get("/traffic-campaigns")
async def get_traffic_campaigns():
    """Получение кампаний трафика"""
    return {"campaigns": traffic_filter.get_campaigns()}


@router.get("/traffic-filter/stats")
async def get_traffic_filter_stats():
    """Статистика фильтрации трафика"""
    return traffic_filter.get_stats()
