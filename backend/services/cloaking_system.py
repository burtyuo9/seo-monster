"""
Advanced Cloaking System
Расширенная система клоакинга для обхода модерации рекламных сетей
"""

import json
import hashlib
import re
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SAFE_PAGES_PATH = os.path.join(DATA_DIR, 'safe_pages.json')
WHITELIST_PATH = os.path.join(DATA_DIR, 'cloaking_whitelist.json')
BLACKLIST_PATH = os.path.join(DATA_DIR, 'cloaking_blacklist.json')


# Расширенные списки IP-диапазонов модераторов и ботов
MODERATOR_IP_RANGES = {
    "google": [
        "64.233.160.0/19", "66.102.0.0/20", "66.249.64.0/19",
        "72.14.192.0/18", "74.125.0.0/16", "108.177.0.0/17",
        "142.250.0.0/15", "172.217.0.0/16", "173.194.0.0/16",
        "207.126.144.0/20", "209.85.128.0/17", "216.239.32.0/19",
        "216.58.192.0/19", "35.190.0.0/17", "35.191.0.0/16"
    ],
    "facebook": [
        "31.13.24.0/21", "31.13.64.0/18", "66.220.144.0/20",
        "69.63.176.0/20", "69.171.224.0/19", "74.119.76.0/22",
        "102.132.96.0/20", "129.134.0.0/16", "157.240.0.0/16",
        "173.252.64.0/18", "179.60.192.0/22", "185.60.216.0/22",
        "204.15.20.0/22"
    ],
    "bing": [
        "40.77.167.0/24", "65.52.0.0/14", "131.253.21.0/24",
        "131.253.22.0/23", "131.253.24.0/21", "131.253.32.0/20",
        "157.55.0.0/16", "157.56.0.0/14", "207.46.0.0/16"
    ],
    "yandex": [
        "5.45.192.0/18", "5.255.192.0/18", "37.9.64.0/18",
        "37.140.128.0/18", "77.88.0.0/18", "84.201.128.0/18",
        "87.250.224.0/19", "93.158.128.0/18", "95.108.128.0/17",
        "100.43.64.0/19", "141.8.128.0/18", "178.154.128.0/17",
        "185.32.187.0/24", "213.180.192.0/19"
    ],
    "tiktok": [
        "161.117.0.0/16", "152.32.128.0/17", "144.48.0.0/16"
    ],
    "linkedin": [
        "108.174.0.0/16", "144.2.0.0/16", "216.52.0.0/16"
    ]
}

# Расширенные User-Agent паттерны
BOT_UA_PATTERNS = [
    # Google
    r"googlebot", r"adsbot-google", r"mediapartners-google",
    r"google-inspectiontool", r"google-adwords", r"feedfetcher-google",
    r"google-site-verification", r"googleweblight", r"google-read-aloud",
    
    # Facebook
    r"facebookexternalhit", r"facebookcatalog", r"facebot",
    r"meta-externalagent", r"meta-externalfetcher",
    
    # Bing
    r"bingbot", r"msnbot", r"bingpreview", r"adidxbot",
    
    # Yandex
    r"yandexbot", r"yandeximages", r"yandexdirect", r"yandexmetrika",
    
    # TikTok
    r"bytespider", r"bytedance", r"tiktok",
    
    # LinkedIn
    r"linkedinbot",
    
    # Общие боты
    r"crawler", r"spider", r"scraper", r"bot/", r"bot\s",
    r"headless", r"phantom", r"selenium", r"puppeteer",
    r"wget", r"curl", r"python-requests", r"httpx",
    r"ahrefs", r"semrush", r"majestic", r"moz\.com",
    r"screaming\s?frog", r"dotbot", r"petalbot"
]


@dataclass
class SafePage:
    """Безопасная страница для показа модераторам"""
    id: str
    name: str
    url: str
    html_content: str = ""
    page_type: str = "redirect"  # redirect, html, proxy
    enabled: bool = True
    views: int = 0
    created_at: str = ""


@dataclass
class CloakingDecision:
    """Результат решения клоакинга"""
    is_bot: bool
    is_moderator: bool
    action: str  # pass, safe_page, redirect, block
    reason: str
    moderator_type: Optional[str] = None
    confidence: float = 0.0
    checks_performed: List[str] = field(default_factory=list)
    redirect_url: Optional[str] = None


class AdvancedCloakingSystem:
    """Расширенная система клоакинга"""
    
    def __init__(self):
        self.safe_pages: Dict[str, SafePage] = {}
        self.whitelist_ips: List[str] = []
        self.blacklist_ips: List[str] = []
        self.whitelist_uas: List[str] = []
        self.blacklist_uas: List[str] = []
        self.decision_log: List[Dict] = []
        self._load_data()
        self._compile_patterns()
    
    def _load_data(self):
        """Загрузка данных"""
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Загрузка безопасных страниц
        if os.path.exists(SAFE_PAGES_PATH):
            try:
                with open(SAFE_PAGES_PATH, 'r') as f:
                    data = json.load(f)
                    for page_data in data.get('pages', []):
                        page = SafePage(**page_data)
                        self.safe_pages[page.id] = page
            except Exception as e:
                print(f"Error loading safe pages: {e}")
        
        # Загрузка whitelist
        if os.path.exists(WHITELIST_PATH):
            try:
                with open(WHITELIST_PATH, 'r') as f:
                    data = json.load(f)
                    self.whitelist_ips = data.get('ips', [])
                    self.whitelist_uas = data.get('user_agents', [])
            except Exception as e:
                print(f"Error loading whitelist: {e}")
        
        # Загрузка blacklist
        if os.path.exists(BLACKLIST_PATH):
            try:
                with open(BLACKLIST_PATH, 'r') as f:
                    data = json.load(f)
                    self.blacklist_ips = data.get('ips', [])
                    self.blacklist_uas = data.get('user_agents', [])
            except Exception as e:
                print(f"Error loading blacklist: {e}")
    
    def _compile_patterns(self):
        """Компиляция регулярных выражений"""
        self.bot_ua_compiled = [re.compile(p, re.IGNORECASE) for p in BOT_UA_PATTERNS]
    
    def _save_safe_pages(self):
        """Сохранение безопасных страниц"""
        data = {"pages": [asdict(p) for p in self.safe_pages.values()]}
        with open(SAFE_PAGES_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_whitelist(self):
        """Сохранение whitelist"""
        data = {"ips": self.whitelist_ips, "user_agents": self.whitelist_uas}
        with open(WHITELIST_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_blacklist(self):
        """Сохранение blacklist"""
        data = {"ips": self.blacklist_ips, "user_agents": self.blacklist_uas}
        with open(BLACKLIST_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # ПРОВЕРКИ
    # ═══════════════════════════════════════════════════════════════
    
    def _check_ip_in_ranges(self, ip: str, ranges: List[str]) -> bool:
        """Проверка IP в диапазонах"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            for range_str in ranges:
                try:
                    network = ipaddress.ip_network(range_str, strict=False)
                    if ip_obj in network:
                        return True
                except ValueError:
                    # Проверка как префикс
                    if ip.startswith(range_str.rstrip('.0/').rstrip('/')):
                        return True
        except ValueError:
            pass
        return False
    
    def _check_moderator_ip(self, ip: str) -> Tuple[bool, Optional[str]]:
        """Проверка IP модератора"""
        for platform, ranges in MODERATOR_IP_RANGES.items():
            if self._check_ip_in_ranges(ip, ranges):
                return True, platform
        return False, None
    
    def _check_bot_ua(self, user_agent: str) -> Tuple[bool, Optional[str]]:
        """Проверка User-Agent на бота"""
        for pattern in self.bot_ua_compiled:
            if pattern.search(user_agent):
                return True, pattern.pattern
        return False, None
    
    def _check_whitelist(self, ip: str, user_agent: str) -> bool:
        """Проверка в whitelist"""
        # Проверка IP
        for wl_ip in self.whitelist_ips:
            if ip.startswith(wl_ip) or ip == wl_ip:
                return True
        
        # Проверка UA
        ua_lower = user_agent.lower()
        for wl_ua in self.whitelist_uas:
            if wl_ua.lower() in ua_lower:
                return True
        
        return False
    
    def _check_blacklist(self, ip: str, user_agent: str) -> Tuple[bool, str]:
        """Проверка в blacklist"""
        # Проверка IP
        for bl_ip in self.blacklist_ips:
            if ip.startswith(bl_ip) or ip == bl_ip:
                return True, "blacklisted_ip"
        
        # Проверка UA
        ua_lower = user_agent.lower()
        for bl_ua in self.blacklist_uas:
            if bl_ua.lower() in ua_lower:
                return True, "blacklisted_ua"
        
        return False, ""
    
    def _check_suspicious_headers(self, headers: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Проверка подозрительных заголовков"""
        suspicious = []
        
        # Нормализуем ключи заголовков (могут быть в разном регистре)
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        # Отсутствие Accept-Language
        if not normalized_headers.get('accept-language'):
            suspicious.append("missing_accept_language")
        
        # Отсутствие Accept-Encoding
        if not normalized_headers.get('accept-encoding'):
            suspicious.append("missing_accept_encoding")
        
        # Подозрительный Accept
        accept = normalized_headers.get('accept', '')
        if accept == '*/*' or not accept:
            suspicious.append("generic_accept")
        
        # Проверка на headless браузеры
        ua = headers.get('user-agent', '').lower()
        if 'headless' in ua or 'phantom' in ua:
            suspicious.append("headless_browser")
        
        return len(suspicious) > 0, suspicious
    
    # ═══════════════════════════════════════════════════════════════
    # ОСНОВНАЯ ЛОГИКА КЛОАКИНГА
    # ═══════════════════════════════════════════════════════════════
    
    def make_decision(self, visitor_data: Dict) -> CloakingDecision:
        """Принятие решения о клоакинге"""
        ip = visitor_data.get('ip', '')
        user_agent = visitor_data.get('user_agent', '')
        headers = visitor_data.get('headers', {})
        referrer = visitor_data.get('referrer', '')
        
        checks_performed = []
        confidence = 0.0
        
        # 1. Проверка whitelist (пропускаем сразу)
        if self._check_whitelist(ip, user_agent):
            return CloakingDecision(
                is_bot=False,
                is_moderator=False,
                action="pass",
                reason="whitelisted",
                confidence=1.0,
                checks_performed=["whitelist"]
            )
        checks_performed.append("whitelist")
        
        # 2. Проверка blacklist (блокируем сразу)
        is_blacklisted, bl_reason = self._check_blacklist(ip, user_agent)
        if is_blacklisted:
            return CloakingDecision(
                is_bot=True,
                is_moderator=False,
                action="block",
                reason=bl_reason,
                confidence=1.0,
                checks_performed=["blacklist"]
            )
        checks_performed.append("blacklist")
        
        # 3. Проверка IP модератора
        is_mod_ip, mod_platform = self._check_moderator_ip(ip)
        if is_mod_ip:
            confidence += 0.6
            checks_performed.append(f"moderator_ip_{mod_platform}")
        
        # 4. Проверка User-Agent на бота
        is_bot_ua, bot_pattern = self._check_bot_ua(user_agent)
        if is_bot_ua:
            confidence += 0.4
            checks_performed.append("bot_user_agent")
        
        # 5. Проверка подозрительных заголовков
        is_suspicious, suspicious_reasons = self._check_suspicious_headers(headers)
        if is_suspicious:
            confidence += 0.1 * len(suspicious_reasons)
            checks_performed.extend(suspicious_reasons)
        
        # Определение результата
        is_moderator = is_mod_ip or is_bot_ua
        is_bot = confidence >= 0.3
        
        if is_moderator:
            # Показываем безопасную страницу модераторам
            safe_page = self._get_default_safe_page()
            return CloakingDecision(
                is_bot=True,
                is_moderator=True,
                action="safe_page",
                reason="moderator_detected",
                moderator_type=mod_platform,
                confidence=confidence,
                checks_performed=checks_performed,
                redirect_url=safe_page.url if safe_page else None
            )
        elif is_bot:
            return CloakingDecision(
                is_bot=True,
                is_moderator=False,
                action="block",
                reason="bot_detected",
                confidence=confidence,
                checks_performed=checks_performed
            )
        else:
            return CloakingDecision(
                is_bot=False,
                is_moderator=False,
                action="pass",
                reason="human_visitor",
                confidence=1.0 - confidence,
                checks_performed=checks_performed
            )
    
    def _get_default_safe_page(self) -> Optional[SafePage]:
        """Получение дефолтной безопасной страницы"""
        for page in self.safe_pages.values():
            if page.enabled:
                return page
        return None
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ БЕЗОПАСНЫМИ СТРАНИЦАМИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_safe_page(self, name: str, url: str, **kwargs) -> SafePage:
        """Создание безопасной страницы"""
        page_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        page = SafePage(
            id=page_id,
            name=name,
            url=url,
            html_content=kwargs.get('html_content', ''),
            page_type=kwargs.get('page_type', 'redirect'),
            enabled=kwargs.get('enabled', True),
            created_at=datetime.now().isoformat()
        )
        
        self.safe_pages[page_id] = page
        self._save_safe_pages()
        return page
    
    def get_safe_pages(self) -> List[Dict]:
        """Получение списка безопасных страниц"""
        return [asdict(p) for p in self.safe_pages.values()]
    
    def update_safe_page(self, page_id: str, **kwargs) -> Optional[SafePage]:
        """Обновление безопасной страницы"""
        if page_id not in self.safe_pages:
            return None
        
        page = self.safe_pages[page_id]
        for key, value in kwargs.items():
            if hasattr(page, key):
                setattr(page, key, value)
        
        self._save_safe_pages()
        return page
    
    def delete_safe_page(self, page_id: str) -> bool:
        """Удаление безопасной страницы"""
        if page_id in self.safe_pages:
            del self.safe_pages[page_id]
            self._save_safe_pages()
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ СПИСКАМИ
    # ═══════════════════════════════════════════════════════════════
    
    def add_to_whitelist(self, ip: str = None, user_agent: str = None):
        """Добавление в whitelist"""
        if ip and ip not in self.whitelist_ips:
            self.whitelist_ips.append(ip)
        if user_agent and user_agent not in self.whitelist_uas:
            self.whitelist_uas.append(user_agent)
        self._save_whitelist()
    
    def add_to_blacklist(self, ip: str = None, user_agent: str = None):
        """Добавление в blacklist"""
        if ip and ip not in self.blacklist_ips:
            self.blacklist_ips.append(ip)
        if user_agent and user_agent not in self.blacklist_uas:
            self.blacklist_uas.append(user_agent)
        self._save_blacklist()
    
    def remove_from_whitelist(self, ip: str = None, user_agent: str = None):
        """Удаление из whitelist"""
        if ip and ip in self.whitelist_ips:
            self.whitelist_ips.remove(ip)
        if user_agent and user_agent in self.whitelist_uas:
            self.whitelist_uas.remove(user_agent)
        self._save_whitelist()
    
    def remove_from_blacklist(self, ip: str = None, user_agent: str = None):
        """Удаление из blacklist"""
        if ip and ip in self.blacklist_ips:
            self.blacklist_ips.remove(ip)
        if user_agent and user_agent in self.blacklist_uas:
            self.blacklist_uas.remove(user_agent)
        self._save_blacklist()
    
    def get_lists(self) -> Dict:
        """Получение всех списков"""
        return {
            "whitelist": {
                "ips": self.whitelist_ips,
                "user_agents": self.whitelist_uas
            },
            "blacklist": {
                "ips": self.blacklist_ips,
                "user_agents": self.blacklist_uas
            }
        }
    
    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    def get_stats(self) -> Dict:
        """Получение статистики клоакинга"""
        return {
            "safe_pages": {
                "total": len(self.safe_pages),
                "active": sum(1 for p in self.safe_pages.values() if p.enabled),
                "total_views": sum(p.views for p in self.safe_pages.values())
            },
            "whitelist": {
                "ips": len(self.whitelist_ips),
                "user_agents": len(self.whitelist_uas)
            },
            "blacklist": {
                "ips": len(self.blacklist_ips),
                "user_agents": len(self.blacklist_uas)
            },
            "moderator_ip_ranges": {
                platform: len(ranges) for platform, ranges in MODERATOR_IP_RANGES.items()
            },
            "bot_ua_patterns": len(BOT_UA_PATTERNS)
        }


# Глобальный экземпляр
cloaking_system = AdvancedCloakingSystem()


# Алиас для совместимости с диагностикой
CloakingSystem = AdvancedCloakingSystem
