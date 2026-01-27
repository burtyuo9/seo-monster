"""
SEO Monster - TDS Core (Traffic Distribution System)
Ядро системы распределения трафика по типу Keitaro

Возможности:
- Трекинг всех кликов с детальной информацией
- Определение гео, устройства, ОС, браузера
- Уникальные и повторные посетители
- Конверсии и постбэки
- Статистика в реальном времени
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
import sqlite3
import re
from urllib.parse import urlparse, parse_qs
import ipaddress

# Пути
DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "tds.db"
GEOIP_PATH = DATA_DIR / "geoip.json"


@dataclass
class Click:
    """Клик/посещение"""
    id: str
    campaign_id: str
    flow_id: Optional[str]
    landing_id: Optional[str]
    offer_id: Optional[str]
    
    # Информация о посетителе
    ip: str
    country: str
    city: str
    region: str
    isp: str
    
    # Устройство
    device_type: str  # desktop, mobile, tablet
    os: str
    os_version: str
    browser: str
    browser_version: str
    
    # User Agent
    user_agent: str
    
    # Источник
    referrer: str
    referrer_domain: str
    
    # URL параметры
    sub_id: str  # subid для постбэков
    sub_id_1: str
    sub_id_2: str
    sub_id_3: str
    sub_id_4: str
    sub_id_5: str
    
    # Результат
    destination_url: str
    is_unique: bool
    is_bot: bool
    is_blocked: bool
    block_reason: str
    
    # Конверсия
    converted: bool
    conversion_time: Optional[str]
    revenue: float
    cost: float
    
    # Время
    timestamp: str
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Campaign:
    """Кампания TDS"""
    id: str
    name: str
    domain: str  # Домен для трекинга
    
    # Настройки
    default_flow_id: Optional[str]
    cost_type: str  # cpc, cpm, cpa, revshare
    cost_value: float
    
    # Статус
    status: str  # active, paused, archived
    
    # Статистика
    clicks: int
    unique_clicks: int
    conversions: int
    revenue: float
    cost: float
    
    # Время
    created_at: str
    updated_at: str
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class TDSCore:
    """
    Ядро Traffic Distribution System
    """
    
    def __init__(self):
        self.db_path = DB_PATH
        self._init_database()
        self._load_geoip_data()
        
        # Кэш для определения уникальных посетителей
        self.visitor_cache: Dict[str, datetime] = {}
        
        # User Agent парсинг паттерны
        self.ua_patterns = self._init_ua_patterns()
        
        # Список известных ботов
        self.bot_patterns = self._init_bot_patterns()
    
    def _init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица кампаний
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                domain TEXT,
                default_flow_id TEXT,
                cost_type TEXT DEFAULT 'cpc',
                cost_value REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                clicks INTEGER DEFAULT 0,
                unique_clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0,
                cost REAL DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Таблица кликов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id TEXT PRIMARY KEY,
                campaign_id TEXT,
                flow_id TEXT,
                landing_id TEXT,
                offer_id TEXT,
                ip TEXT,
                country TEXT,
                city TEXT,
                region TEXT,
                isp TEXT,
                device_type TEXT,
                os TEXT,
                os_version TEXT,
                browser TEXT,
                browser_version TEXT,
                user_agent TEXT,
                referrer TEXT,
                referrer_domain TEXT,
                sub_id TEXT,
                sub_id_1 TEXT,
                sub_id_2 TEXT,
                sub_id_3 TEXT,
                sub_id_4 TEXT,
                sub_id_5 TEXT,
                destination_url TEXT,
                is_unique INTEGER,
                is_bot INTEGER,
                is_blocked INTEGER,
                block_reason TEXT,
                converted INTEGER DEFAULT 0,
                conversion_time TEXT,
                revenue REAL DEFAULT 0,
                cost REAL DEFAULT 0,
                timestamp TEXT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')
        
        # Индексы для быстрого поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clicks_campaign ON clicks(campaign_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clicks_timestamp ON clicks(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clicks_country ON clicks(country)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clicks_ip ON clicks(ip)')
        
        # Таблица конверсий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                id TEXT PRIMARY KEY,
                click_id TEXT,
                campaign_id TEXT,
                offer_id TEXT,
                sub_id TEXT,
                revenue REAL,
                status TEXT,
                timestamp TEXT,
                FOREIGN KEY (click_id) REFERENCES clicks(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_geoip_data(self):
        """Загрузка GeoIP данных"""
        # Базовая таблица IP диапазонов по странам
        # В реальном проекте использовать MaxMind GeoIP2
        self.geoip_data = {}
        
        if GEOIP_PATH.exists():
            try:
                with open(GEOIP_PATH, 'r') as f:
                    self.geoip_data = json.load(f)
            except:
                pass
        
        # Базовые данные для демо
        if not self.geoip_data:
            self.geoip_data = {
                "country_codes": {
                    "RU": "Russia",
                    "US": "United States",
                    "DE": "Germany",
                    "FR": "France",
                    "GB": "United Kingdom",
                    "UA": "Ukraine",
                    "KZ": "Kazakhstan",
                    "BY": "Belarus",
                    "PL": "Poland",
                    "IT": "Italy",
                    "ES": "Spain",
                    "BR": "Brazil",
                    "IN": "India",
                    "CN": "China",
                    "JP": "Japan"
                }
            }
    
    def _init_ua_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Инициализация паттернов User Agent"""
        return {
            "os": [
                (r"Windows NT 10\.0", "Windows 10"),
                (r"Windows NT 6\.3", "Windows 8.1"),
                (r"Windows NT 6\.2", "Windows 8"),
                (r"Windows NT 6\.1", "Windows 7"),
                (r"Mac OS X (\d+[._]\d+)", "macOS"),
                (r"Android (\d+\.?\d*)", "Android"),
                (r"iPhone OS (\d+[._]\d+)", "iOS"),
                (r"iPad.*OS (\d+[._]\d+)", "iPadOS"),
                (r"Linux", "Linux"),
                (r"Ubuntu", "Ubuntu"),
                (r"CrOS", "Chrome OS"),
            ],
            "browser": [
                (r"Chrome/(\d+)", "Chrome"),
                (r"Firefox/(\d+)", "Firefox"),
                (r"Safari/(\d+)", "Safari"),
                (r"Edge/(\d+)", "Edge"),
                (r"Edg/(\d+)", "Edge"),
                (r"OPR/(\d+)", "Opera"),
                (r"Opera/(\d+)", "Opera"),
                (r"MSIE (\d+)", "Internet Explorer"),
                (r"Trident.*rv:(\d+)", "Internet Explorer"),
                (r"YaBrowser/(\d+)", "Yandex Browser"),
                (r"SamsungBrowser/(\d+)", "Samsung Browser"),
            ],
            "device": [
                (r"Mobile|Android.*Mobile|iPhone|iPod", "mobile"),
                (r"iPad|Android(?!.*Mobile)|Tablet", "tablet"),
                (r".*", "desktop"),
            ]
        }
    
    def _init_bot_patterns(self) -> List[str]:
        """Список паттернов для определения ботов"""
        return [
            r"bot", r"crawler", r"spider", r"slurp", r"googlebot",
            r"bingbot", r"yandex", r"baidu", r"duckduck", r"facebookexternalhit",
            r"twitterbot", r"linkedinbot", r"pinterest", r"whatsapp",
            r"telegrambot", r"applebot", r"semrush", r"ahrefs",
            r"mj12bot", r"dotbot", r"petalbot", r"bytespider",
            r"headless", r"phantom", r"selenium", r"puppeteer",
            r"curl", r"wget", r"python-requests", r"httpx", r"axios"
        ]
    
    # ═══════════════════════════════════════════════════════════════
    # ПАРСИНГ ИНФОРМАЦИИ О ПОСЕТИТЕЛЕ
    # ═══════════════════════════════════════════════════════════════
    
    def parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """Парсинг User Agent"""
        result = {
            "device_type": "desktop",
            "os": "Unknown",
            "os_version": "",
            "browser": "Unknown",
            "browser_version": ""
        }
        
        if not user_agent:
            return result
        
        ua_lower = user_agent.lower()
        
        # Определение устройства
        for pattern, device in self.ua_patterns["device"]:
            if re.search(pattern, user_agent, re.IGNORECASE):
                result["device_type"] = device
                break
        
        # Определение ОС
        for pattern, os_name in self.ua_patterns["os"]:
            match = re.search(pattern, user_agent, re.IGNORECASE)
            if match:
                result["os"] = os_name
                if match.groups():
                    result["os_version"] = match.group(1).replace("_", ".")
                break
        
        # Определение браузера
        for pattern, browser_name in self.ua_patterns["browser"]:
            match = re.search(pattern, user_agent, re.IGNORECASE)
            if match:
                result["browser"] = browser_name
                if match.groups():
                    result["browser_version"] = match.group(1)
                break
        
        return result
    
    def detect_bot(self, user_agent: str, ip: str = "") -> Tuple[bool, str]:
        """Определение бота"""
        if not user_agent:
            return True, "Empty User Agent"
        
        ua_lower = user_agent.lower()
        
        for pattern in self.bot_patterns:
            if re.search(pattern, ua_lower):
                return True, f"Bot pattern: {pattern}"
        
        # Проверка подозрительных признаков
        if len(user_agent) < 20:
            return True, "User Agent too short"
        
        if "mozilla" not in ua_lower and "opera" not in ua_lower:
            return True, "Missing Mozilla/Opera"
        
        return False, ""
    
    def get_geo_info(self, ip: str) -> Dict[str, str]:
        """Получение гео-информации по IP"""
        # В реальном проекте использовать MaxMind GeoIP2 или ip-api.com
        # Для демо возвращаем заглушку
        result = {
            "country": "XX",
            "country_name": "Unknown",
            "city": "Unknown",
            "region": "Unknown",
            "isp": "Unknown"
        }
        
        # Простая логика для демо
        if ip.startswith("192.168") or ip.startswith("10.") or ip.startswith("127."):
            result["country"] = "LOCAL"
            result["country_name"] = "Local Network"
        
        return result
    
    def parse_referrer(self, referrer: str) -> str:
        """Извлечение домена из реферера"""
        if not referrer:
            return ""
        
        try:
            parsed = urlparse(referrer)
            return parsed.netloc or ""
        except:
            return ""
    
    def generate_click_id(self) -> str:
        """Генерация уникального ID клика"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_part = hashlib.md5(f"{timestamp}{os.urandom(8).hex()}".encode()).hexdigest()[:8]
        return f"clk_{timestamp}_{random_part}"
    
    def generate_visitor_hash(self, ip: str, user_agent: str) -> str:
        """Генерация хэша посетителя для определения уникальности"""
        data = f"{ip}:{user_agent}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def is_unique_visitor(self, campaign_id: str, visitor_hash: str, 
                         unique_period_hours: int = 24) -> bool:
        """Проверка уникальности посетителя"""
        cache_key = f"{campaign_id}:{visitor_hash}"
        now = datetime.now()
        
        if cache_key in self.visitor_cache:
            last_visit = self.visitor_cache[cache_key]
            if now - last_visit < timedelta(hours=unique_period_hours):
                return False
        
        self.visitor_cache[cache_key] = now
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ КАМПАНИЯМИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_campaign(self, name: str, domain: str = "",
                       cost_type: str = "cpc", cost_value: float = 0) -> Dict:
        """Создание кампании"""
        campaign_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaigns (id, name, domain, cost_type, cost_value, 
                                  status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
        ''', (campaign_id, name, domain, cost_type, cost_value, now, now))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "message": f"Кампания '{name}' создана"
        }
    
    def get_campaigns(self, status: Optional[str] = None) -> List[Dict]:
        """Получение списка кампаний"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM campaigns WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM campaigns ORDER BY created_at DESC')
        
        campaigns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return campaigns
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        """Получение кампании по ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_campaign(self, campaign_id: str, **kwargs) -> Dict:
        """Обновление кампании"""
        allowed_fields = ['name', 'domain', 'default_flow_id', 'cost_type', 
                         'cost_value', 'status']
        
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            return {"success": False, "error": "Нет полей для обновления"}
        
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(campaign_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            UPDATE campaigns SET {", ".join(updates)} WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Кампания обновлена"}
    
    def delete_campaign(self, campaign_id: str) -> Dict:
        """Удаление кампании"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM clicks WHERE campaign_id = ?', (campaign_id,))
        cursor.execute('DELETE FROM campaigns WHERE id = ?', (campaign_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Кампания удалена"}
    
    # ═══════════════════════════════════════════════════════════════
    # ТРЕКИНГ КЛИКОВ
    # ═══════════════════════════════════════════════════════════════
    
    def track_click(self, campaign_id: str, ip: str, user_agent: str,
                   referrer: str = "", url_params: Dict = None,
                   destination_url: str = "", flow_id: str = "",
                   landing_id: str = "", offer_id: str = "") -> Dict:
        """
        Трекинг клика
        """
        url_params = url_params or {}
        
        # Генерация ID клика
        click_id = self.generate_click_id()
        
        # Парсинг User Agent
        ua_info = self.parse_user_agent(user_agent)
        
        # Определение бота
        is_bot, bot_reason = self.detect_bot(user_agent, ip)
        
        # Гео-информация
        geo_info = self.get_geo_info(ip)
        
        # Проверка уникальности
        visitor_hash = self.generate_visitor_hash(ip, user_agent)
        is_unique = self.is_unique_visitor(campaign_id, visitor_hash)
        
        # Парсинг реферера
        referrer_domain = self.parse_referrer(referrer)
        
        # Извлечение sub_id из параметров
        sub_id = url_params.get("subid", url_params.get("sub_id", url_params.get("clickid", "")))
        sub_id_1 = url_params.get("sub1", url_params.get("sub_id_1", ""))
        sub_id_2 = url_params.get("sub2", url_params.get("sub_id_2", ""))
        sub_id_3 = url_params.get("sub3", url_params.get("sub_id_3", ""))
        sub_id_4 = url_params.get("sub4", url_params.get("sub_id_4", ""))
        sub_id_5 = url_params.get("sub5", url_params.get("sub_id_5", ""))
        
        # Если sub_id не передан, генерируем
        if not sub_id:
            sub_id = click_id
        
        # Сохранение клика
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clicks (
                id, campaign_id, flow_id, landing_id, offer_id,
                ip, country, city, region, isp,
                device_type, os, os_version, browser, browser_version,
                user_agent, referrer, referrer_domain,
                sub_id, sub_id_1, sub_id_2, sub_id_3, sub_id_4, sub_id_5,
                destination_url, is_unique, is_bot, is_blocked, block_reason,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            click_id, campaign_id, flow_id, landing_id, offer_id,
            ip, geo_info["country"], geo_info["city"], geo_info["region"], geo_info["isp"],
            ua_info["device_type"], ua_info["os"], ua_info["os_version"],
            ua_info["browser"], ua_info["browser_version"],
            user_agent, referrer, referrer_domain,
            sub_id, sub_id_1, sub_id_2, sub_id_3, sub_id_4, sub_id_5,
            destination_url, int(is_unique), int(is_bot), 0, "",
            datetime.now().isoformat()
        ))
        
        # Обновление статистики кампании
        if is_unique:
            cursor.execute('''
                UPDATE campaigns SET clicks = clicks + 1, unique_clicks = unique_clicks + 1,
                updated_at = ? WHERE id = ?
            ''', (datetime.now().isoformat(), campaign_id))
        else:
            cursor.execute('''
                UPDATE campaigns SET clicks = clicks + 1, updated_at = ? WHERE id = ?
            ''', (datetime.now().isoformat(), campaign_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "click_id": click_id,
            "sub_id": sub_id,
            "is_unique": is_unique,
            "is_bot": is_bot,
            "country": geo_info["country"],
            "device": ua_info["device_type"],
            "os": ua_info["os"],
            "browser": ua_info["browser"]
        }
    
    def record_conversion(self, click_id: str = "", sub_id: str = "",
                         revenue: float = 0, status: str = "approved") -> Dict:
        """
        Запись конверсии (постбэк)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Поиск клика
        if click_id:
            cursor.execute('SELECT * FROM clicks WHERE id = ?', (click_id,))
        elif sub_id:
            cursor.execute('SELECT * FROM clicks WHERE sub_id = ?', (sub_id,))
        else:
            conn.close()
            return {"success": False, "error": "Не указан click_id или sub_id"}
        
        click = cursor.fetchone()
        if not click:
            conn.close()
            return {"success": False, "error": "Клик не найден"}
        
        click = dict(click)
        
        # Генерация ID конверсии
        conv_id = hashlib.md5(f"{click['id']}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Запись конверсии
        cursor.execute('''
            INSERT INTO conversions (id, click_id, campaign_id, offer_id, sub_id, revenue, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (conv_id, click['id'], click['campaign_id'], click['offer_id'],
              click['sub_id'], revenue, status, datetime.now().isoformat()))
        
        # Обновление клика
        cursor.execute('''
            UPDATE clicks SET converted = 1, conversion_time = ?, revenue = ? WHERE id = ?
        ''', (datetime.now().isoformat(), revenue, click['id']))
        
        # Обновление статистики кампании
        cursor.execute('''
            UPDATE campaigns SET conversions = conversions + 1, revenue = revenue + ?,
            updated_at = ? WHERE id = ?
        ''', (revenue, datetime.now().isoformat(), click['campaign_id']))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "conversion_id": conv_id,
            "click_id": click['id'],
            "revenue": revenue
        }
    
    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    def get_campaign_stats(self, campaign_id: str, 
                          start_date: str = "", end_date: str = "",
                          group_by: str = "day") -> Dict:
        """Получение статистики кампании"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Базовый запрос
        query = '''
            SELECT 
                COUNT(*) as clicks,
                SUM(is_unique) as unique_clicks,
                SUM(converted) as conversions,
                SUM(revenue) as revenue,
                SUM(cost) as cost
            FROM clicks
            WHERE campaign_id = ?
        '''
        params = [campaign_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        totals = dict(cursor.fetchone())
        
        # Статистика по дням
        if group_by == "day":
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as clicks,
                    SUM(is_unique) as unique_clicks,
                    SUM(converted) as conversions,
                    SUM(revenue) as revenue
                FROM clicks
                WHERE campaign_id = ?
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            ''', (campaign_id,))
        elif group_by == "country":
            cursor.execute('''
                SELECT 
                    country,
                    COUNT(*) as clicks,
                    SUM(is_unique) as unique_clicks,
                    SUM(converted) as conversions,
                    SUM(revenue) as revenue
                FROM clicks
                WHERE campaign_id = ?
                GROUP BY country
                ORDER BY clicks DESC
            ''', (campaign_id,))
        elif group_by == "device":
            cursor.execute('''
                SELECT 
                    device_type,
                    COUNT(*) as clicks,
                    SUM(is_unique) as unique_clicks,
                    SUM(converted) as conversions
                FROM clicks
                WHERE campaign_id = ?
                GROUP BY device_type
                ORDER BY clicks DESC
            ''', (campaign_id,))
        elif group_by == "os":
            cursor.execute('''
                SELECT 
                    os,
                    COUNT(*) as clicks,
                    SUM(is_unique) as unique_clicks,
                    SUM(converted) as conversions
                FROM clicks
                WHERE campaign_id = ?
                GROUP BY os
                ORDER BY clicks DESC
            ''', (campaign_id,))
        elif group_by == "browser":
            cursor.execute('''
                SELECT 
                    browser,
                    COUNT(*) as clicks,
                    SUM(is_unique) as unique_clicks,
                    SUM(converted) as conversions
                FROM clicks
                WHERE campaign_id = ?
                GROUP BY browser
                ORDER BY clicks DESC
            ''', (campaign_id,))
        
        breakdown = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Расчёт метрик
        cr = 0
        if totals["unique_clicks"] and totals["unique_clicks"] > 0:
            cr = (totals["conversions"] or 0) / totals["unique_clicks"] * 100
        
        epc = 0
        if totals["clicks"] and totals["clicks"] > 0:
            epc = (totals["revenue"] or 0) / totals["clicks"]
        
        roi = 0
        if totals["cost"] and totals["cost"] > 0:
            roi = ((totals["revenue"] or 0) - totals["cost"]) / totals["cost"] * 100
        
        return {
            "totals": totals,
            "breakdown": breakdown,
            "metrics": {
                "cr": round(cr, 2),  # Conversion Rate
                "epc": round(epc, 4),  # Earnings Per Click
                "roi": round(roi, 2)  # Return on Investment
            }
        }
    
    def get_clicks(self, campaign_id: str = "", limit: int = 100,
                  offset: int = 0, filters: Dict = None) -> List[Dict]:
        """Получение списка кликов"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM clicks WHERE 1=1"
        params = []
        
        if campaign_id:
            query += " AND campaign_id = ?"
            params.append(campaign_id)
        
        if filters:
            if filters.get("country"):
                query += " AND country = ?"
                params.append(filters["country"])
            
            if filters.get("device_type"):
                query += " AND device_type = ?"
                params.append(filters["device_type"])
            
            if filters.get("is_unique") is not None:
                query += " AND is_unique = ?"
                params.append(int(filters["is_unique"]))
            
            if filters.get("converted") is not None:
                query += " AND converted = ?"
                params.append(int(filters["converted"]))
            
            if filters.get("is_bot") is not None:
                query += " AND is_bot = ?"
                params.append(int(filters["is_bot"]))
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        clicks = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return clicks
    
    def get_overall_stats(self) -> Dict:
        """Общая статистика по всем кампаниям"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Общие показатели
        cursor.execute('''
            SELECT 
                COUNT(*) as total_campaigns,
                SUM(clicks) as total_clicks,
                SUM(unique_clicks) as total_unique,
                SUM(conversions) as total_conversions,
                SUM(revenue) as total_revenue,
                SUM(cost) as total_cost
            FROM campaigns
        ''')
        totals = dict(cursor.fetchone())
        
        # Статистика за сегодня
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT 
                COUNT(*) as clicks,
                SUM(is_unique) as unique_clicks,
                SUM(converted) as conversions,
                SUM(revenue) as revenue
            FROM clicks
            WHERE DATE(timestamp) = ?
        ''', (today,))
        today_stats = dict(cursor.fetchone())
        
        # Топ кампании
        cursor.execute('''
            SELECT id, name, clicks, unique_clicks, conversions, revenue
            FROM campaigns
            ORDER BY clicks DESC
            LIMIT 5
        ''')
        top_campaigns = [dict(row) for row in cursor.fetchall()]
        
        # Топ страны
        cursor.execute('''
            SELECT country, COUNT(*) as clicks, SUM(converted) as conversions
            FROM clicks
            GROUP BY country
            ORDER BY clicks DESC
            LIMIT 10
        ''')
        top_countries = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "totals": totals,
            "today": today_stats,
            "top_campaigns": top_campaigns,
            "top_countries": top_countries
        }


# Singleton
_tds_core = None

def get_tds_core() -> TDSCore:
    """Получение экземпляра TDS Core"""
    global _tds_core
    if _tds_core is None:
        _tds_core = TDSCore()
    return _tds_core
