"""
SEO Monster - TDS Antifraud System
Система защиты от фрода, ботов и нежелательного трафика

Функции:
- Детекция ботов по User-Agent, поведению, fingerprint
- Блокировка IP/диапазонов
- Детекция прокси/VPN
- Проверка рефереров
- Honeypot ловушки
- Анализ поведения
"""

import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from collections import defaultdict

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
ANTIFRAUD_PATH = DATA_DIR / "antifraud.json"
BLACKLIST_PATH = DATA_DIR / "blacklist.json"
FRAUD_LOG_PATH = DATA_DIR / "fraud_log.json"


# Известные боты и краулеры
BOT_SIGNATURES = [
    # Поисковые боты
    "googlebot", "bingbot", "yandexbot", "baiduspider", "duckduckbot",
    "slurp", "msnbot", "teoma", "gigabot", "scrubby",
    # Социальные сети
    "facebookexternalhit", "twitterbot", "linkedinbot", "pinterest",
    "whatsapp", "telegrambot", "slackbot", "discordbot",
    # SEO инструменты
    "semrushbot", "ahrefsbot", "mj12bot", "dotbot", "rogerbot",
    "screaming frog", "seokicks", "sistrix", "blexbot",
    # Мониторинг
    "uptimerobot", "pingdom", "statuscake", "site24x7",
    # Общие боты
    "bot", "crawler", "spider", "scraper", "curl", "wget", "python",
    "java", "perl", "ruby", "go-http", "axios", "node-fetch",
    "headless", "phantom", "selenium", "puppeteer", "playwright"
]

# Подозрительные User-Agent паттерны
SUSPICIOUS_UA_PATTERNS = [
    r"^$",  # Пустой UA
    r"^-$",
    r"^Mozilla/[45]\.0$",  # Слишком короткий
    r"^Mozilla/[45]\.0 \(compatible\)$",
    r"MSIE [1-6]\.",  # Старые IE
    r"Windows NT [1-5]\.",  # Старые Windows
    r"Android [1-3]\.",  # Старые Android
]

# Известные диапазоны дата-центров (примеры)
DATACENTER_RANGES = [
    "104.16.",  # Cloudflare
    "172.64.",  # Cloudflare
    "141.101.",  # Cloudflare
    "45.33.",  # Linode
    "96.126.",  # Linode
    "139.162.",  # Linode
    "167.99.",  # DigitalOcean
    "206.189.",  # DigitalOcean
    "134.209.",  # DigitalOcean
    "35.192.",  # Google Cloud
    "35.193.",  # Google Cloud
    "34.68.",  # Google Cloud
    "52.0.",  # AWS
    "54.0.",  # AWS
    "18.0.",  # AWS
]


@dataclass
class AntifraudSettings:
    """Настройки антифрода"""
    # Включение/выключение
    enabled: bool = True
    
    # Детекция ботов
    block_bots: bool = True
    block_empty_ua: bool = True
    block_suspicious_ua: bool = True
    
    # Детекция дата-центров
    block_datacenters: bool = False
    
    # Лимиты
    max_clicks_per_ip: int = 100  # За час
    max_clicks_per_ip_daily: int = 500
    click_flood_threshold: int = 10  # Кликов за 10 секунд
    
    # Рефереры
    check_referrer: bool = True
    block_empty_referrer: bool = False
    allowed_referrers: List[str] = field(default_factory=list)
    blocked_referrers: List[str] = field(default_factory=list)
    
    # Honeypot
    honeypot_enabled: bool = False
    honeypot_field_name: str = "website"
    
    # Fingerprint
    check_fingerprint: bool = True
    block_duplicate_fingerprints: bool = False
    
    # Действия
    action_on_fraud: str = "block"  # block, redirect, log_only
    fraud_redirect_url: str = ""
    
    # Логирование
    log_all_checks: bool = False
    log_blocked_only: bool = True


@dataclass
class BlacklistEntry:
    """Запись в чёрном списке"""
    id: str
    entry_type: str  # ip, ip_range, ua, referrer, fingerprint
    value: str
    reason: str = ""
    expires_at: str = ""  # Пустая строка = навсегда
    created_at: str = ""
    hits: int = 0


@dataclass
class FraudLogEntry:
    """Запись в логе фрода"""
    timestamp: str
    ip: str
    user_agent: str
    referrer: str
    reason: str
    action_taken: str
    click_id: str = ""
    campaign_id: str = ""
    fingerprint: str = ""
    country: str = ""
    additional_data: Dict = field(default_factory=dict)


class TDSAntifraud:
    """
    Система антифрода TDS
    """
    
    def __init__(self):
        self.settings = AntifraudSettings()
        self.blacklist: Dict[str, BlacklistEntry] = {}
        self.fraud_log: List[FraudLogEntry] = []
        
        # Кэш для rate limiting
        self.ip_clicks: Dict[str, List[datetime]] = defaultdict(list)
        self.fingerprint_cache: Dict[str, List[datetime]] = defaultdict(list)
        
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных"""
        # Настройки
        if ANTIFRAUD_PATH.exists():
            try:
                with open(ANTIFRAUD_PATH, 'r') as f:
                    data = json.load(f)
                    settings_data = data.get("settings", {})
                    if isinstance(settings_data.get("allowed_referrers"), str):
                        settings_data["allowed_referrers"] = []
                    if isinstance(settings_data.get("blocked_referrers"), str):
                        settings_data["blocked_referrers"] = []
                    self.settings = AntifraudSettings(**settings_data)
            except Exception as e:
                print(f"Ошибка загрузки настроек антифрода: {e}")
        
        # Чёрный список
        if BLACKLIST_PATH.exists():
            try:
                with open(BLACKLIST_PATH, 'r') as f:
                    data = json.load(f)
                    for entry_data in data.get("entries", []):
                        entry = BlacklistEntry(**entry_data)
                        self.blacklist[entry.id] = entry
            except Exception as e:
                print(f"Ошибка загрузки чёрного списка: {e}")
        
        # Лог фрода (последние 1000 записей)
        if FRAUD_LOG_PATH.exists():
            try:
                with open(FRAUD_LOG_PATH, 'r') as f:
                    data = json.load(f)
                    for entry_data in data.get("entries", [])[-1000:]:
                        if isinstance(entry_data.get("additional_data"), str):
                            entry_data["additional_data"] = {}
                        self.fraud_log.append(FraudLogEntry(**entry_data))
            except Exception as e:
                print(f"Ошибка загрузки лога фрода: {e}")
    
    def _save_settings(self):
        """Сохранение настроек"""
        data = {"settings": asdict(self.settings)}
        with open(ANTIFRAUD_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_blacklist(self):
        """Сохранение чёрного списка"""
        data = {"entries": [asdict(e) for e in self.blacklist.values()]}
        with open(BLACKLIST_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_fraud_log(self):
        """Сохранение лога фрода"""
        # Храним только последние 10000 записей
        entries = self.fraud_log[-10000:]
        data = {"entries": [asdict(e) for e in entries]}
        with open(FRAUD_LOG_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # НАСТРОЙКИ
    # ═══════════════════════════════════════════════════════════════
    
    def get_settings(self) -> Dict:
        """Получение настроек"""
        return asdict(self.settings)
    
    def update_settings(self, **kwargs) -> Dict:
        """Обновление настроек"""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        self._save_settings()
        return {"success": True, "message": "Настройки обновлены"}
    
    # ═══════════════════════════════════════════════════════════════
    # ПРОВЕРКА ПОСЕТИТЕЛЯ
    # ═══════════════════════════════════════════════════════════════
    
    def check_visitor(self, visitor_data: Dict) -> Tuple[bool, str, str]:
        """
        Полная проверка посетителя
        
        Возвращает:
        - (True, "", "") - посетитель чист
        - (False, reason, action) - посетитель заблокирован
        """
        if not self.settings.enabled:
            return True, "", ""
        
        ip = visitor_data.get("ip", "")
        user_agent = visitor_data.get("user_agent", "")
        referrer = visitor_data.get("referrer", "")
        fingerprint = visitor_data.get("fingerprint", "")
        
        # 1. Проверка чёрного списка
        blocked, reason = self._check_blacklist(ip, user_agent, referrer, fingerprint)
        if blocked:
            self._log_fraud(visitor_data, reason, self.settings.action_on_fraud)
            return False, reason, self.settings.action_on_fraud
        
        # 2. Проверка User-Agent на ботов
        if self.settings.block_bots:
            is_bot, bot_reason = self._check_bot_ua(user_agent)
            if is_bot:
                self._log_fraud(visitor_data, bot_reason, self.settings.action_on_fraud)
                return False, bot_reason, self.settings.action_on_fraud
        
        # 3. Проверка пустого User-Agent
        if self.settings.block_empty_ua and not user_agent:
            reason = "Empty User-Agent"
            self._log_fraud(visitor_data, reason, self.settings.action_on_fraud)
            return False, reason, self.settings.action_on_fraud
        
        # 4. Проверка подозрительного User-Agent
        if self.settings.block_suspicious_ua:
            is_suspicious, sus_reason = self._check_suspicious_ua(user_agent)
            if is_suspicious:
                self._log_fraud(visitor_data, sus_reason, self.settings.action_on_fraud)
                return False, sus_reason, self.settings.action_on_fraud
        
        # 5. Проверка дата-центров
        if self.settings.block_datacenters:
            is_dc = self._check_datacenter(ip)
            if is_dc:
                reason = "Datacenter IP detected"
                self._log_fraud(visitor_data, reason, self.settings.action_on_fraud)
                return False, reason, self.settings.action_on_fraud
        
        # 6. Проверка рефереров
        if self.settings.check_referrer:
            ref_blocked, ref_reason = self._check_referrer(referrer)
            if ref_blocked:
                self._log_fraud(visitor_data, ref_reason, self.settings.action_on_fraud)
                return False, ref_reason, self.settings.action_on_fraud
        
        # 7. Rate limiting по IP
        rate_limited, rate_reason = self._check_rate_limit(ip)
        if rate_limited:
            self._log_fraud(visitor_data, rate_reason, self.settings.action_on_fraud)
            return False, rate_reason, self.settings.action_on_fraud
        
        # 8. Проверка click flood
        is_flood = self._check_click_flood(ip)
        if is_flood:
            reason = "Click flood detected"
            self._log_fraud(visitor_data, reason, self.settings.action_on_fraud)
            # Автоматическое добавление в чёрный список на 1 час
            self.add_to_blacklist("ip", ip, reason, hours=1)
            return False, reason, self.settings.action_on_fraud
        
        # Запись клика для rate limiting
        self._record_click(ip, fingerprint)
        
        # Логирование успешной проверки (если включено)
        if self.settings.log_all_checks:
            self._log_fraud(visitor_data, "Passed all checks", "allow")
        
        return True, "", ""
    
    def _check_blacklist(self, ip: str, user_agent: str, referrer: str, 
                        fingerprint: str) -> Tuple[bool, str]:
        """Проверка чёрного списка"""
        now = datetime.now()
        
        for entry in self.blacklist.values():
            # Проверка срока действия
            if entry.expires_at:
                try:
                    expires = datetime.fromisoformat(entry.expires_at)
                    if now > expires:
                        continue
                except:
                    pass
            
            if entry.entry_type == "ip" and ip == entry.value:
                entry.hits += 1
                self._save_blacklist()
                return True, f"IP blacklisted: {entry.reason}"
            
            elif entry.entry_type == "ip_range" and ip.startswith(entry.value):
                entry.hits += 1
                self._save_blacklist()
                return True, f"IP range blacklisted: {entry.reason}"
            
            elif entry.entry_type == "ua" and entry.value.lower() in user_agent.lower():
                entry.hits += 1
                self._save_blacklist()
                return True, f"User-Agent blacklisted: {entry.reason}"
            
            elif entry.entry_type == "referrer" and entry.value.lower() in referrer.lower():
                entry.hits += 1
                self._save_blacklist()
                return True, f"Referrer blacklisted: {entry.reason}"
            
            elif entry.entry_type == "fingerprint" and fingerprint == entry.value:
                entry.hits += 1
                self._save_blacklist()
                return True, f"Fingerprint blacklisted: {entry.reason}"
        
        return False, ""
    
    def _check_bot_ua(self, user_agent: str) -> Tuple[bool, str]:
        """Проверка User-Agent на ботов"""
        ua_lower = user_agent.lower()
        
        for bot_sig in BOT_SIGNATURES:
            if bot_sig in ua_lower:
                return True, f"Bot detected: {bot_sig}"
        
        return False, ""
    
    def _check_suspicious_ua(self, user_agent: str) -> Tuple[bool, str]:
        """Проверка подозрительного User-Agent"""
        for pattern in SUSPICIOUS_UA_PATTERNS:
            if re.match(pattern, user_agent, re.IGNORECASE):
                return True, f"Suspicious User-Agent pattern: {pattern}"
        
        return False, ""
    
    def _check_datacenter(self, ip: str) -> bool:
        """Проверка IP дата-центра"""
        for dc_range in DATACENTER_RANGES:
            if ip.startswith(dc_range):
                return True
        return False
    
    def _check_referrer(self, referrer: str) -> Tuple[bool, str]:
        """Проверка реферера"""
        # Блокировка пустого реферера
        if self.settings.block_empty_referrer and not referrer:
            return True, "Empty referrer blocked"
        
        # Проверка заблокированных рефереров
        ref_lower = referrer.lower()
        for blocked in self.settings.blocked_referrers:
            if blocked.lower() in ref_lower:
                return True, f"Blocked referrer: {blocked}"
        
        # Проверка разрешённых рефереров (если список не пуст)
        if self.settings.allowed_referrers and referrer:
            allowed = False
            for allowed_ref in self.settings.allowed_referrers:
                if allowed_ref.lower() in ref_lower:
                    allowed = True
                    break
            if not allowed:
                return True, "Referrer not in allowed list"
        
        return False, ""
    
    def _check_rate_limit(self, ip: str) -> Tuple[bool, str]:
        """Проверка rate limit по IP"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        # Очистка старых записей
        self.ip_clicks[ip] = [t for t in self.ip_clicks[ip] if t > day_ago]
        
        # Подсчёт кликов за час
        hourly_clicks = len([t for t in self.ip_clicks[ip] if t > hour_ago])
        if hourly_clicks >= self.settings.max_clicks_per_ip:
            return True, f"Rate limit exceeded: {hourly_clicks} clicks/hour"
        
        # Подсчёт кликов за день
        daily_clicks = len(self.ip_clicks[ip])
        if daily_clicks >= self.settings.max_clicks_per_ip_daily:
            return True, f"Daily rate limit exceeded: {daily_clicks} clicks/day"
        
        return False, ""
    
    def _check_click_flood(self, ip: str) -> bool:
        """Проверка click flood (много кликов за короткое время)"""
        now = datetime.now()
        ten_seconds_ago = now - timedelta(seconds=10)
        
        recent_clicks = len([t for t in self.ip_clicks[ip] if t > ten_seconds_ago])
        return recent_clicks >= self.settings.click_flood_threshold
    
    def _record_click(self, ip: str, fingerprint: str = ""):
        """Запись клика для rate limiting"""
        now = datetime.now()
        self.ip_clicks[ip].append(now)
        
        if fingerprint:
            self.fingerprint_cache[fingerprint].append(now)
    
    def _log_fraud(self, visitor_data: Dict, reason: str, action: str):
        """Логирование фрода"""
        if not self.settings.log_blocked_only or action != "allow":
            entry = FraudLogEntry(
                timestamp=datetime.now().isoformat(),
                ip=visitor_data.get("ip", ""),
                user_agent=visitor_data.get("user_agent", ""),
                referrer=visitor_data.get("referrer", ""),
                reason=reason,
                action_taken=action,
                click_id=visitor_data.get("click_id", ""),
                campaign_id=visitor_data.get("campaign_id", ""),
                fingerprint=visitor_data.get("fingerprint", ""),
                country=visitor_data.get("country", "")
            )
            self.fraud_log.append(entry)
            
            # Периодическое сохранение
            if len(self.fraud_log) % 100 == 0:
                self._save_fraud_log()
    
    # ═══════════════════════════════════════════════════════════════
    # ЧЁРНЫЙ СПИСОК
    # ═══════════════════════════════════════════════════════════════
    
    def add_to_blacklist(self, entry_type: str, value: str, 
                        reason: str = "", hours: int = 0) -> Dict:
        """Добавление в чёрный список"""
        entry_id = hashlib.md5(f"{entry_type}_{value}".encode()).hexdigest()[:12]
        
        expires_at = ""
        if hours > 0:
            expires_at = (datetime.now() + timedelta(hours=hours)).isoformat()
        
        entry = BlacklistEntry(
            id=entry_id,
            entry_type=entry_type,
            value=value,
            reason=reason,
            expires_at=expires_at,
            created_at=datetime.now().isoformat()
        )
        
        self.blacklist[entry_id] = entry
        self._save_blacklist()
        
        return {
            "success": True,
            "entry_id": entry_id,
            "message": f"Добавлено в чёрный список: {entry_type}={value}"
        }
    
    def remove_from_blacklist(self, entry_id: str) -> Dict:
        """Удаление из чёрного списка"""
        if entry_id not in self.blacklist:
            return {"success": False, "error": "Запись не найдена"}
        
        del self.blacklist[entry_id]
        self._save_blacklist()
        
        return {"success": True, "message": "Удалено из чёрного списка"}
    
    def get_blacklist(self, entry_type: str = None) -> List[Dict]:
        """Получение чёрного списка"""
        result = []
        for entry in self.blacklist.values():
            if entry_type and entry.entry_type != entry_type:
                continue
            result.append(asdict(entry))
        return result
    
    def import_blacklist(self, entries: List[Dict]) -> Dict:
        """Импорт чёрного списка"""
        imported = 0
        for entry_data in entries:
            entry_type = entry_data.get("type", "ip")
            value = entry_data.get("value", "")
            reason = entry_data.get("reason", "Imported")
            
            if value:
                self.add_to_blacklist(entry_type, value, reason)
                imported += 1
        
        return {"success": True, "imported": imported}
    
    def clear_expired_blacklist(self) -> Dict:
        """Очистка истёкших записей"""
        now = datetime.now()
        removed = 0
        
        to_remove = []
        for entry_id, entry in self.blacklist.items():
            if entry.expires_at:
                try:
                    expires = datetime.fromisoformat(entry.expires_at)
                    if now > expires:
                        to_remove.append(entry_id)
                except:
                    pass
        
        for entry_id in to_remove:
            del self.blacklist[entry_id]
            removed += 1
        
        if removed > 0:
            self._save_blacklist()
        
        return {"success": True, "removed": removed}
    
    # ═══════════════════════════════════════════════════════════════
    # HONEYPOT
    # ═══════════════════════════════════════════════════════════════
    
    def check_honeypot(self, form_data: Dict) -> Tuple[bool, str]:
        """Проверка honeypot поля"""
        if not self.settings.honeypot_enabled:
            return False, ""
        
        honeypot_value = form_data.get(self.settings.honeypot_field_name, "")
        
        if honeypot_value:
            return True, f"Honeypot triggered: {self.settings.honeypot_field_name}"
        
        return False, ""
    
    def generate_honeypot_html(self) -> str:
        """Генерация HTML для honeypot поля"""
        field_name = self.settings.honeypot_field_name
        return f'''
        <div style="position: absolute; left: -9999px; opacity: 0; height: 0; overflow: hidden;">
            <input type="text" name="{field_name}" id="{field_name}" 
                   tabindex="-1" autocomplete="off" value="">
        </div>
        '''
    
    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА И ЛОГИ
    # ═══════════════════════════════════════════════════════════════
    
    def get_fraud_stats(self, hours: int = 24) -> Dict:
        """Получение статистики фрода"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_logs = []
        for entry in self.fraud_log:
            try:
                entry_time = datetime.fromisoformat(entry.timestamp)
                if entry_time > cutoff:
                    recent_logs.append(entry)
            except:
                pass
        
        # Подсчёт по причинам
        reasons = defaultdict(int)
        for entry in recent_logs:
            reasons[entry.reason] += 1
        
        # Топ заблокированных IP
        blocked_ips = defaultdict(int)
        for entry in recent_logs:
            if entry.action_taken == "block":
                blocked_ips[entry.ip] += 1
        
        top_blocked_ips = sorted(blocked_ips.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "period_hours": hours,
            "total_checks": len(recent_logs),
            "blocked": len([e for e in recent_logs if e.action_taken == "block"]),
            "allowed": len([e for e in recent_logs if e.action_taken == "allow"]),
            "reasons": dict(reasons),
            "top_blocked_ips": top_blocked_ips,
            "blacklist_size": len(self.blacklist)
        }
    
    def get_fraud_log(self, limit: int = 100, action: str = None) -> List[Dict]:
        """Получение лога фрода"""
        result = []
        
        for entry in reversed(self.fraud_log[-limit:]):
            if action and entry.action_taken != action:
                continue
            result.append(asdict(entry))
        
        return result
    
    def clear_fraud_log(self, older_than_days: int = 30) -> Dict:
        """Очистка старых записей лога"""
        cutoff = datetime.now() - timedelta(days=older_than_days)
        
        new_log = []
        for entry in self.fraud_log:
            try:
                entry_time = datetime.fromisoformat(entry.timestamp)
                if entry_time > cutoff:
                    new_log.append(entry)
            except:
                new_log.append(entry)
        
        removed = len(self.fraud_log) - len(new_log)
        self.fraud_log = new_log
        self._save_fraud_log()
        
        return {"success": True, "removed": removed}
    
    # ═══════════════════════════════════════════════════════════════
    # АНАЛИЗ ПОВЕДЕНИЯ
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_visitor_behavior(self, click_history: List[Dict]) -> Dict:
        """
        Анализ поведения посетителя по истории кликов
        
        Возвращает оценку подозрительности (0-100)
        """
        if not click_history:
            return {"score": 0, "reasons": []}
        
        score = 0
        reasons = []
        
        # 1. Слишком быстрые клики
        timestamps = []
        for click in click_history:
            try:
                ts = datetime.fromisoformat(click.get("timestamp", ""))
                timestamps.append(ts)
            except:
                pass
        
        if len(timestamps) >= 2:
            timestamps.sort()
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(interval)
            
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval < 1:
                score += 40
                reasons.append("Very fast clicks (< 1 sec avg)")
            elif avg_interval < 3:
                score += 20
                reasons.append("Fast clicks (< 3 sec avg)")
        
        # 2. Одинаковые User-Agent
        user_agents = set(c.get("user_agent", "") for c in click_history)
        if len(user_agents) == 1 and len(click_history) > 10:
            score += 10
            reasons.append("Same User-Agent for all clicks")
        
        # 3. Много кликов без конверсий
        conversions = sum(1 for c in click_history if c.get("converted"))
        if len(click_history) > 50 and conversions == 0:
            score += 20
            reasons.append("Many clicks without conversions")
        
        # 4. Клики только по одной кампании
        campaigns = set(c.get("campaign_id", "") for c in click_history)
        if len(campaigns) == 1 and len(click_history) > 20:
            score += 10
            reasons.append("All clicks on single campaign")
        
        return {
            "score": min(score, 100),
            "reasons": reasons,
            "recommendation": "block" if score >= 60 else "monitor" if score >= 30 else "allow"
        }


# Singleton
_tds_antifraud = None

def get_tds_antifraud() -> TDSAntifraud:
    """Получение экземпляра TDS Antifraud"""
    global _tds_antifraud
    if _tds_antifraud is None:
        _tds_antifraud = TDSAntifraud()
    return _tds_antifraud
