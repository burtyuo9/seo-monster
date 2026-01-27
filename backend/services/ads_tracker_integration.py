"""
Ads-Tracker Integration Module
Интеграция трекера с рекламными кампаниями для обхода фрод-систем
"""

import json
import hashlib
import asyncio
import aiohttp
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import os

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INTEGRATION_PATH = os.path.join(DATA_DIR, 'ads_tracker_integration.json')
CLOAKING_PATH = os.path.join(DATA_DIR, 'cloaking_rules.json')
POSTBACKS_PATH = os.path.join(DATA_DIR, 'postbacks.json')


class CloakingMode(str, Enum):
    """Режимы клоакинга"""
    DISABLED = "disabled"
    SAFE_PAGE = "safe_page"  # Показ безопасной страницы модераторам
    REDIRECT = "redirect"    # Редирект модераторов
    BLOCK = "block"          # Блокировка модераторов
    GEO_FILTER = "geo_filter"  # Фильтрация по гео


class ModeratorType(str, Enum):
    """Типы модераторов рекламных сетей"""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    BING = "bing"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    YANDEX = "yandex"


@dataclass
class CloakingRule:
    """Правило клоакинга"""
    id: str
    name: str
    mode: CloakingMode = CloakingMode.SAFE_PAGE
    safe_page_url: str = ""
    redirect_url: str = ""
    enabled: bool = True
    target_platforms: List[str] = field(default_factory=list)
    blocked_ips: List[str] = field(default_factory=list)
    blocked_user_agents: List[str] = field(default_factory=list)
    blocked_referrers: List[str] = field(default_factory=list)
    allowed_countries: List[str] = field(default_factory=list)
    blocked_countries: List[str] = field(default_factory=list)
    hits: int = 0
    blocks: int = 0
    created_at: str = ""


@dataclass
class PostbackConfig:
    """Конфигурация постбэка"""
    id: str
    name: str
    platform: str  # google, facebook, bing, etc.
    event_type: str  # conversion, lead, purchase, etc.
    url_template: str
    method: str = "GET"  # GET or POST
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    sent_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    last_sent: str = ""


@dataclass
class TrackingLink:
    """Трекинговая ссылка для рекламной кампании"""
    id: str
    campaign_id: str
    name: str
    url: str
    tracking_params: Dict[str, str] = field(default_factory=dict)
    clicks: int = 0
    unique_clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    cost: float = 0.0
    created_at: str = ""


# Сигнатуры модераторов рекламных сетей
MODERATOR_SIGNATURES = {
    ModeratorType.GOOGLE: {
        "ips": [
            "66.249.", "66.102.", "64.233.", "72.14.", "74.125.",
            "209.85.", "216.239.", "173.194.", "207.126.", "108.177.",
            "172.217.", "142.250.", "35.190.", "35.191.", "34.64.",
            "34.65.", "34.80.", "34.96.", "34.104.", "34.124."
        ],
        "user_agents": [
            "googlebot", "adsbot-google", "mediapartners-google",
            "google-adwords", "google-inspectiontool", "google-read-aloud",
            "feedfetcher-google", "google-site-verification", "googleweblight"
        ],
        "referrers": [
            "google.com/ads", "ads.google.com", "adwords.google.com"
        ]
    },
    ModeratorType.FACEBOOK: {
        "ips": [
            "31.13.", "66.220.", "69.63.", "69.171.", "74.119.",
            "173.252.", "179.60.", "185.60.", "204.15.", "157.240.",
            "129.134.", "163.70.", "199.201."
        ],
        "user_agents": [
            "facebookexternalhit", "facebookcatalog", "facebook",
            "facebot", "meta-externalagent", "meta-externalfetcher"
        ],
        "referrers": [
            "facebook.com", "fb.com", "business.facebook.com"
        ]
    },
    ModeratorType.BING: {
        "ips": [
            "40.77.", "157.55.", "207.46.", "13.66.", "13.67.",
            "52.167.", "65.52.", "131.253.", "199.30."
        ],
        "user_agents": [
            "bingbot", "msnbot", "bingpreview", "adidxbot"
        ],
        "referrers": [
            "bing.com", "ads.microsoft.com"
        ]
    },
    ModeratorType.TIKTOK: {
        "ips": [
            "161.117.", "152.32.", "144.48.", "103.136."
        ],
        "user_agents": [
            "tiktok", "bytespider", "bytedance"
        ],
        "referrers": [
            "tiktok.com", "ads.tiktok.com"
        ]
    },
    ModeratorType.LINKEDIN: {
        "ips": [
            "144.2.", "108.174.", "216.52."
        ],
        "user_agents": [
            "linkedinbot", "linkedin"
        ],
        "referrers": [
            "linkedin.com", "business.linkedin.com"
        ]
    },
    ModeratorType.YANDEX: {
        "ips": [
            "5.45.", "5.255.", "37.9.", "37.140.", "77.88.",
            "84.201.", "87.250.", "93.158.", "95.108.", "100.43.",
            "130.193.", "141.8.", "178.154.", "185.32.", "213.180."
        ],
        "user_agents": [
            "yandexbot", "yandex", "yandeximages", "yandexdirect"
        ],
        "referrers": [
            "yandex.ru", "direct.yandex.ru", "yandex.com"
        ]
    }
}


class AdsTrackerIntegration:
    """Интеграция трекера с рекламными кампаниями"""
    
    def __init__(self):
        self.cloaking_rules: Dict[str, CloakingRule] = {}
        self.postbacks: Dict[str, PostbackConfig] = {}
        self.tracking_links: Dict[str, TrackingLink] = {}
        self.click_log: List[Dict] = []
        self.conversion_log: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных из файлов"""
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Загрузка правил клоакинга
        if os.path.exists(CLOAKING_PATH):
            try:
                with open(CLOAKING_PATH, 'r') as f:
                    data = json.load(f)
                    for rule_data in data.get('rules', []):
                        rule = CloakingRule(**rule_data)
                        self.cloaking_rules[rule.id] = rule
            except Exception as e:
                print(f"Error loading cloaking rules: {e}")
        
        # Загрузка постбэков
        if os.path.exists(POSTBACKS_PATH):
            try:
                with open(POSTBACKS_PATH, 'r') as f:
                    data = json.load(f)
                    for pb_data in data.get('postbacks', []):
                        pb = PostbackConfig(**pb_data)
                        self.postbacks[pb.id] = pb
            except Exception as e:
                print(f"Error loading postbacks: {e}")
    
    def _save_cloaking_rules(self):
        """Сохранение правил клоакинга"""
        data = {"rules": [asdict(r) for r in self.cloaking_rules.values()]}
        with open(CLOAKING_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_postbacks(self):
        """Сохранение постбэков"""
        data = {"postbacks": [asdict(p) for p in self.postbacks.values()]}
        with open(POSTBACKS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # ДЕТЕКЦИЯ МОДЕРАТОРОВ
    # ═══════════════════════════════════════════════════════════════
    
    def detect_moderator(self, ip: str, user_agent: str, referrer: str = "") -> Optional[ModeratorType]:
        """Определение модератора рекламной сети"""
        ua_lower = user_agent.lower()
        ref_lower = referrer.lower()
        
        for mod_type, signatures in MODERATOR_SIGNATURES.items():
            # Проверка IP
            for ip_prefix in signatures.get("ips", []):
                if ip.startswith(ip_prefix):
                    return mod_type
            
            # Проверка User-Agent
            for ua_sig in signatures.get("user_agents", []):
                if ua_sig in ua_lower:
                    return mod_type
            
            # Проверка Referrer
            for ref_sig in signatures.get("referrers", []):
                if ref_sig in ref_lower:
                    return mod_type
        
        return None
    
    def is_moderator(self, ip: str, user_agent: str, referrer: str = "") -> bool:
        """Проверка, является ли посетитель модератором"""
        return self.detect_moderator(ip, user_agent, referrer) is not None
    
    # ═══════════════════════════════════════════════════════════════
    # КЛОАКИНГ
    # ═══════════════════════════════════════════════════════════════
    
    def create_cloaking_rule(self, name: str, **kwargs) -> CloakingRule:
        """Создание правила клоакинга"""
        rule_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        rule = CloakingRule(
            id=rule_id,
            name=name,
            mode=CloakingMode(kwargs.get("mode", CloakingMode.SAFE_PAGE)),
            safe_page_url=kwargs.get("safe_page_url", ""),
            redirect_url=kwargs.get("redirect_url", ""),
            enabled=kwargs.get("enabled", True),
            target_platforms=kwargs.get("target_platforms", []),
            blocked_ips=kwargs.get("blocked_ips", []),
            blocked_user_agents=kwargs.get("blocked_user_agents", []),
            blocked_referrers=kwargs.get("blocked_referrers", []),
            allowed_countries=kwargs.get("allowed_countries", []),
            blocked_countries=kwargs.get("blocked_countries", []),
            created_at=datetime.now().isoformat()
        )
        
        self.cloaking_rules[rule_id] = rule
        self._save_cloaking_rules()
        return rule
    
    def apply_cloaking(self, rule_id: str, visitor_data: Dict) -> Dict:
        """Применение клоакинга к посетителю"""
        if rule_id not in self.cloaking_rules:
            return {"action": "pass", "reason": "rule_not_found"}
        
        rule = self.cloaking_rules[rule_id]
        if not rule.enabled:
            return {"action": "pass", "reason": "rule_disabled"}
        
        ip = visitor_data.get("ip", "")
        user_agent = visitor_data.get("user_agent", "")
        referrer = visitor_data.get("referrer", "")
        country = visitor_data.get("country", "")
        
        rule.hits += 1
        
        # Проверка на модератора
        moderator = self.detect_moderator(ip, user_agent, referrer)
        if moderator:
            rule.blocks += 1
            self._save_cloaking_rules()
            
            if rule.mode == CloakingMode.SAFE_PAGE:
                return {
                    "action": "safe_page",
                    "url": rule.safe_page_url,
                    "reason": f"moderator_detected_{moderator.value}"
                }
            elif rule.mode == CloakingMode.REDIRECT:
                return {
                    "action": "redirect",
                    "url": rule.redirect_url,
                    "reason": f"moderator_detected_{moderator.value}"
                }
            elif rule.mode == CloakingMode.BLOCK:
                return {
                    "action": "block",
                    "reason": f"moderator_detected_{moderator.value}"
                }
        
        # Проверка заблокированных IP
        for blocked_ip in rule.blocked_ips:
            if ip.startswith(blocked_ip):
                rule.blocks += 1
                self._save_cloaking_rules()
                return {"action": "block", "reason": "blocked_ip"}
        
        # Проверка User-Agent
        ua_lower = user_agent.lower()
        for blocked_ua in rule.blocked_user_agents:
            if blocked_ua.lower() in ua_lower:
                rule.blocks += 1
                self._save_cloaking_rules()
                return {"action": "block", "reason": "blocked_user_agent"}
        
        # Проверка гео
        if rule.mode == CloakingMode.GEO_FILTER:
            if rule.allowed_countries and country not in rule.allowed_countries:
                rule.blocks += 1
                self._save_cloaking_rules()
                return {"action": "block", "reason": "country_not_allowed"}
            if country in rule.blocked_countries:
                rule.blocks += 1
                self._save_cloaking_rules()
                return {"action": "block", "reason": "country_blocked"}
        
        self._save_cloaking_rules()
        return {"action": "pass", "reason": "visitor_allowed"}
    
    # ═══════════════════════════════════════════════════════════════
    # ПОСТБЭКИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_postback(self, name: str, platform: str, event_type: str, 
                        url_template: str, **kwargs) -> PostbackConfig:
        """Создание конфигурации постбэка"""
        pb_id = hashlib.md5(f"{name}_{platform}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        postback = PostbackConfig(
            id=pb_id,
            name=name,
            platform=platform,
            event_type=event_type,
            url_template=url_template,
            method=kwargs.get("method", "GET"),
            headers=kwargs.get("headers", {}),
            params=kwargs.get("params", {}),
            enabled=kwargs.get("enabled", True)
        )
        
        self.postbacks[pb_id] = postback
        self._save_postbacks()
        return postback
    
    async def send_postback(self, postback_id: str, data: Dict) -> Dict:
        """Отправка постбэка"""
        if postback_id not in self.postbacks:
            return {"success": False, "error": "postback_not_found"}
        
        pb = self.postbacks[postback_id]
        if not pb.enabled:
            return {"success": False, "error": "postback_disabled"}
        
        # Подстановка переменных в URL
        url = pb.url_template
        for key, value in data.items():
            url = url.replace(f"{{{key}}}", str(value))
        
        # Подстановка в параметры
        params = {}
        for key, template in pb.params.items():
            value = template
            for data_key, data_value in data.items():
                value = value.replace(f"{{{data_key}}}", str(data_value))
            params[key] = value
        
        try:
            async with aiohttp.ClientSession() as session:
                if pb.method == "GET":
                    async with session.get(url, params=params, headers=pb.headers) as resp:
                        pb.sent_count += 1
                        if resp.status == 200:
                            pb.success_count += 1
                            pb.last_sent = datetime.now().isoformat()
                            self._save_postbacks()
                            return {"success": True, "status": resp.status}
                        else:
                            pb.fail_count += 1
                            self._save_postbacks()
                            return {"success": False, "status": resp.status}
                else:
                    async with session.post(url, json=params, headers=pb.headers) as resp:
                        pb.sent_count += 1
                        if resp.status == 200:
                            pb.success_count += 1
                            pb.last_sent = datetime.now().isoformat()
                            self._save_postbacks()
                            return {"success": True, "status": resp.status}
                        else:
                            pb.fail_count += 1
                            self._save_postbacks()
                            return {"success": False, "status": resp.status}
        except Exception as e:
            pb.fail_count += 1
            self._save_postbacks()
            return {"success": False, "error": str(e)}
    
    async def send_conversion(self, platform: str, conversion_data: Dict) -> List[Dict]:
        """Отправка конверсии во все активные постбэки платформы"""
        results = []
        for pb in self.postbacks.values():
            if pb.platform == platform and pb.enabled and pb.event_type == "conversion":
                result = await self.send_postback(pb.id, conversion_data)
                results.append({"postback_id": pb.id, "name": pb.name, **result})
        
        # Логирование конверсии
        self.conversion_log.append({
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "data": conversion_data,
            "results": results
        })
        
        return results
    
    # ═══════════════════════════════════════════════════════════════
    # ТРЕКИНГОВЫЕ ССЫЛКИ
    # ═══════════════════════════════════════════════════════════════
    
    def generate_tracking_link(self, campaign_id: str, base_url: str, 
                               name: str = "", **kwargs) -> TrackingLink:
        """Генерация трекинговой ссылки"""
        link_id = hashlib.md5(f"{campaign_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Стандартные параметры трекинга
        tracking_params = {
            "click_id": "{click_id}",
            "campaign_id": campaign_id,
            "source": kwargs.get("source", ""),
            "sub1": kwargs.get("sub1", ""),
            "sub2": kwargs.get("sub2", ""),
            "sub3": kwargs.get("sub3", ""),
            "sub4": kwargs.get("sub4", ""),
            "sub5": kwargs.get("sub5", ""),
        }
        tracking_params.update(kwargs.get("custom_params", {}))
        
        # Формирование URL
        params_str = "&".join([f"{k}={v}" for k, v in tracking_params.items() if v])
        separator = "&" if "?" in base_url else "?"
        full_url = f"{base_url}{separator}{params_str}"
        
        link = TrackingLink(
            id=link_id,
            campaign_id=campaign_id,
            name=name or f"Link_{link_id}",
            url=full_url,
            tracking_params=tracking_params,
            created_at=datetime.now().isoformat()
        )
        
        self.tracking_links[link_id] = link
        return link
    
    def track_click(self, link_id: str, visitor_data: Dict) -> Dict:
        """Трекинг клика"""
        if link_id not in self.tracking_links:
            return {"success": False, "error": "link_not_found"}
        
        link = self.tracking_links[link_id]
        
        # Генерация уникального click_id
        click_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        
        # Обновление статистики
        link.clicks += 1
        
        # Проверка уникальности (по IP + UA)
        visitor_hash = hashlib.md5(
            f"{visitor_data.get('ip', '')}_{visitor_data.get('user_agent', '')}".encode()
        ).hexdigest()
        
        # Логирование клика
        click_data = {
            "click_id": click_id,
            "link_id": link_id,
            "campaign_id": link.campaign_id,
            "visitor_hash": visitor_hash,
            "timestamp": datetime.now().isoformat(),
            **visitor_data
        }
        self.click_log.append(click_data)
        
        # Формирование финального URL с подставленным click_id
        final_url = link.url.replace("{click_id}", click_id)
        
        return {
            "success": True,
            "click_id": click_id,
            "redirect_url": final_url,
            "campaign_id": link.campaign_id
        }
    
    # ═══════════════════════════════════════════════════════════════
    # ПРЕДУСТАНОВЛЕННЫЕ ПОСТБЭКИ ДЛЯ ПОПУЛЯРНЫХ ПЛАТФОРМ
    # ═══════════════════════════════════════════════════════════════
    
    def get_postback_templates(self) -> Dict[str, Dict]:
        """Получение шаблонов постбэков для популярных платформ"""
        return {
            "google_ads": {
                "name": "Google Ads Conversion",
                "platform": "google",
                "event_type": "conversion",
                "url_template": "https://www.googleadservices.com/pagead/conversion/{conversion_id}/",
                "params": {
                    "gclid": "{gclid}",
                    "value": "{value}",
                    "currency": "{currency}",
                    "transaction_id": "{click_id}"
                }
            },
            "facebook_capi": {
                "name": "Facebook Conversions API",
                "platform": "facebook",
                "event_type": "conversion",
                "url_template": "https://graph.facebook.com/v18.0/{pixel_id}/events",
                "method": "POST",
                "params": {
                    "access_token": "{access_token}",
                    "data": "{event_data}"
                }
            },
            "bing_uet": {
                "name": "Bing UET Conversion",
                "platform": "bing",
                "event_type": "conversion",
                "url_template": "https://bat.bing.com/action/0",
                "params": {
                    "ti": "{tag_id}",
                    "evt": "custom",
                    "ec": "conversion",
                    "ea": "{action}",
                    "ev": "{value}"
                }
            },
            "tiktok_events": {
                "name": "TikTok Events API",
                "platform": "tiktok",
                "event_type": "conversion",
                "url_template": "https://business-api.tiktok.com/open_api/v1.3/pixel/track/",
                "method": "POST",
                "params": {
                    "pixel_code": "{pixel_code}",
                    "event": "CompletePayment",
                    "event_id": "{click_id}"
                }
            }
        }
    
    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    def get_integration_stats(self) -> Dict:
        """Получение статистики интеграции"""
        total_clicks = sum(link.clicks for link in self.tracking_links.values())
        total_conversions = sum(link.conversions for link in self.tracking_links.values())
        total_revenue = sum(link.revenue for link in self.tracking_links.values())
        
        postback_stats = {
            "total": len(self.postbacks),
            "active": sum(1 for pb in self.postbacks.values() if pb.enabled),
            "total_sent": sum(pb.sent_count for pb in self.postbacks.values()),
            "total_success": sum(pb.success_count for pb in self.postbacks.values()),
            "total_failed": sum(pb.fail_count for pb in self.postbacks.values())
        }
        
        cloaking_stats = {
            "total_rules": len(self.cloaking_rules),
            "active_rules": sum(1 for r in self.cloaking_rules.values() if r.enabled),
            "total_hits": sum(r.hits for r in self.cloaking_rules.values()),
            "total_blocks": sum(r.blocks for r in self.cloaking_rules.values()),
            "block_rate": 0
        }
        
        if cloaking_stats["total_hits"] > 0:
            cloaking_stats["block_rate"] = round(
                cloaking_stats["total_blocks"] / cloaking_stats["total_hits"] * 100, 2
            )
        
        return {
            "tracking_links": len(self.tracking_links),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_revenue": total_revenue,
            "conversion_rate": round(total_conversions / total_clicks * 100, 2) if total_clicks > 0 else 0,
            "postbacks": postback_stats,
            "cloaking": cloaking_stats
        }
    
    def get_cloaking_rules(self) -> List[Dict]:
        """Получение списка правил клоакинга"""
        return [asdict(r) for r in self.cloaking_rules.values()]
    
    def get_postbacks(self) -> List[Dict]:
        """Получение списка постбэков"""
        return [asdict(p) for p in self.postbacks.values()]


# Глобальный экземпляр
ads_tracker_integration = AdsTrackerIntegration()
