"""
SEO Monster - Traffic Statistics System (Keitaro-style)
Детальная система статистики трафика
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import hashlib

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
STATS_PATH = DATA_DIR / "statistics.json"
CLICKS_PATH = DATA_DIR / "clicks.json"


@dataclass
class Click:
    """Клик"""
    id: str
    timestamp: str
    ip: str
    country: str = ""
    city: str = ""
    region: str = ""
    isp: str = ""
    browser: str = ""
    browser_version: str = ""
    os: str = ""
    os_version: str = ""
    device: str = ""
    language: str = ""
    referrer: str = ""
    referrer_domain: str = ""
    landing_id: str = ""

    offer_id: str = ""
    campaign_id: str = ""
    flow_id: str = ""
    sub_id: str = ""
    sub_id_2: str = ""
    sub_id_3: str = ""
    sub_id_4: str = ""
    sub_id_5: str = ""
    is_unique: bool = True
    is_bot: bool = False
    is_proxy: bool = False
    cost: float = 0.0
    revenue: float = 0.0
    profit: float = 0.0
    converted: bool = False
    conversion_time: str = ""


@dataclass
class DailyStats:
    """Дневная статистика"""
    date: str
    clicks: int = 0
    unique_clicks: int = 0
    bots: int = 0
    conversions: int = 0
    revenue: float = 0.0
    cost: float = 0.0
    profit: float = 0.0
    cr: float = 0.0  # Conversion Rate
    epc: float = 0.0  # Earnings Per Click
    roi: float = 0.0  # Return On Investment


class TrafficStatistics:
    """Система статистики трафика как в Keitaro"""
    
    def __init__(self):
        self.clicks: List[Click] = []
        self.daily_stats: Dict[str, DailyStats] = {}
        self.unique_ips: Dict[str, set] = defaultdict(set)  # По дням
        self._load_data()
    
    def _load_data(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if CLICKS_PATH.exists():
            try:
                with open(CLICKS_PATH, 'r') as f:
                    data = json.load(f)
                    for c_data in data.get("clicks", [])[-50000:]:
                        click = Click(**c_data)
                        self.clicks.append(click)
            except Exception as e:
                print(f"Error loading clicks: {e}")
        
        if STATS_PATH.exists():
            try:
                with open(STATS_PATH, 'r') as f:
                    data = json.load(f)
                    for s_data in data.get("daily_stats", []):
                        stats = DailyStats(**s_data)
                        self.daily_stats[stats.date] = stats
            except Exception as e:
                print(f"Error loading stats: {e}")
    
    def _save_clicks(self):
        # Сохраняем только последние 50000 кликов
        data = {"clicks": [asdict(c) for c in self.clicks[-50000:]]}
        with open(CLICKS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_stats(self):
        data = {"daily_stats": [asdict(s) for s in self.daily_stats.values()]}
        with open(STATS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def record_click(self, click_data: Dict) -> Click:
        """Запись клика"""
        click_id = hashlib.md5(
            f"{click_data.get('ip', '')}_{datetime.now().isoformat()}_{len(self.clicks)}".encode()
        ).hexdigest()[:16]
        
        today = datetime.now().strftime("%Y-%m-%d")
        ip = click_data.get("ip", "")
        
        # Проверка уникальности
        is_unique = ip not in self.unique_ips[today]
        if is_unique:
            self.unique_ips[today].add(ip)
        
        click = Click(
            id=click_id,
            timestamp=datetime.now().isoformat(),
            ip=ip,
            country=click_data.get("country", ""),
            city=click_data.get("city", ""),
            region=click_data.get("region", ""),
            isp=click_data.get("isp", ""),
            browser=click_data.get("browser", ""),
            browser_version=click_data.get("browser_version", ""),
            os=click_data.get("os", ""),
            os_version=click_data.get("os_version", ""),
            device=click_data.get("device", ""),
            language=click_data.get("language", ""),
            referrer=click_data.get("referrer", ""),
            referrer_domain=click_data.get("referrer_domain", ""),
            landing_id=click_data.get("landing_id", ""),
            offer_id=click_data.get("offer_id", ""),
            campaign_id=click_data.get("campaign_id", ""),
            flow_id=click_data.get("flow_id", ""),
            sub_id=click_data.get("sub_id", ""),
            sub_id_2=click_data.get("sub_id_2", ""),
            sub_id_3=click_data.get("sub_id_3", ""),
            sub_id_4=click_data.get("sub_id_4", ""),
            sub_id_5=click_data.get("sub_id_5", ""),
            is_unique=is_unique,
            is_bot=click_data.get("is_bot", False),
            is_proxy=click_data.get("is_proxy", False),
            cost=click_data.get("cost", 0.0)
        )
        
        self.clicks.append(click)
        self._update_daily_stats(click)
        
        # Периодическое сохранение
        if len(self.clicks) % 100 == 0:
            self._save_clicks()
            self._save_stats()
        
        return click
    
    def _update_daily_stats(self, click: Click):
        """Обновление дневной статистики"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.daily_stats:
            self.daily_stats[today] = DailyStats(date=today)
        
        stats = self.daily_stats[today]
        stats.clicks += 1
        
        if click.is_unique:
            stats.unique_clicks += 1
        
        if click.is_bot:
            stats.bots += 1
        
        stats.cost += click.cost
        
        self._recalculate_stats(stats)
    
    def record_conversion(self, click_id: str, revenue: float = 0.0) -> bool:
        """Запись конверсии"""
        for click in reversed(self.clicks):
            if click.id == click_id and not click.converted:
                click.converted = True
                click.conversion_time = datetime.now().isoformat()
                click.revenue = revenue
                click.profit = revenue - click.cost
                
                # Обновляем дневную статистику
                click_date = click.timestamp[:10]
                if click_date in self.daily_stats:
                    stats = self.daily_stats[click_date]
                    stats.conversions += 1
                    stats.revenue += revenue
                    stats.profit += click.profit
                    self._recalculate_stats(stats)
                
                self._save_clicks()
                self._save_stats()
                return True
        return False
    
    def _recalculate_stats(self, stats: DailyStats):
        """Пересчёт показателей"""
        if stats.clicks > 0:
            stats.cr = (stats.conversions / stats.clicks) * 100
            stats.epc = stats.revenue / stats.clicks
        
        if stats.cost > 0:
            stats.roi = ((stats.revenue - stats.cost) / stats.cost) * 100
    
    def get_stats_by_period(self, start_date: str, end_date: str) -> Dict:
        """Получение статистики за период"""
        result = {
            "period": {"start": start_date, "end": end_date},
            "totals": {
                "clicks": 0,
                "unique_clicks": 0,
                "bots": 0,
                "conversions": 0,
                "revenue": 0.0,
                "cost": 0.0,
                "profit": 0.0,
                "cr": 0.0,
                "epc": 0.0,
                "roi": 0.0
            },
            "daily": []
        }
        
        for date, stats in sorted(self.daily_stats.items()):
            if start_date <= date <= end_date:
                result["daily"].append(asdict(stats))
                result["totals"]["clicks"] += stats.clicks
                result["totals"]["unique_clicks"] += stats.unique_clicks
                result["totals"]["bots"] += stats.bots
                result["totals"]["conversions"] += stats.conversions
                result["totals"]["revenue"] += stats.revenue
                result["totals"]["cost"] += stats.cost
                result["totals"]["profit"] += stats.profit
        
        # Пересчёт итоговых показателей
        totals = result["totals"]
        if totals["clicks"] > 0:
            totals["cr"] = (totals["conversions"] / totals["clicks"]) * 100
            totals["epc"] = totals["revenue"] / totals["clicks"]
        if totals["cost"] > 0:
            totals["roi"] = ((totals["revenue"] - totals["cost"]) / totals["cost"]) * 100
        
        return result
    
    def get_stats_by_country(self, start_date: str = "", end_date: str = "") -> List[Dict]:
        """Статистика по странам"""
        country_stats = defaultdict(lambda: {
            "clicks": 0, "unique": 0, "conversions": 0, "revenue": 0.0
        })
        
        for click in self.clicks:
            click_date = click.timestamp[:10]
            if start_date and click_date < start_date:
                continue
            if end_date and click_date > end_date:
                continue
            
            country = click.country or "Unknown"
            country_stats[country]["clicks"] += 1
            if click.is_unique:
                country_stats[country]["unique"] += 1
            if click.converted:
                country_stats[country]["conversions"] += 1
                country_stats[country]["revenue"] += click.revenue
        
        result = []
        for country, stats in sorted(country_stats.items(), key=lambda x: x[1]["clicks"], reverse=True):
            cr = (stats["conversions"] / stats["clicks"] * 100) if stats["clicks"] > 0 else 0
            result.append({
                "country": country,
                "clicks": stats["clicks"],
                "unique": stats["unique"],
                "conversions": stats["conversions"],
                "revenue": stats["revenue"],
                "cr": round(cr, 2)
            })
        
        return result
    
    def get_stats_by_browser(self, start_date: str = "", end_date: str = "") -> List[Dict]:
        """Статистика по браузерам"""
        browser_stats = defaultdict(lambda: {"clicks": 0, "conversions": 0})
        
        for click in self.clicks:
            click_date = click.timestamp[:10]
            if start_date and click_date < start_date:
                continue
            if end_date and click_date > end_date:
                continue
            
            browser = click.browser or "Unknown"
            browser_stats[browser]["clicks"] += 1
            if click.converted:
                browser_stats[browser]["conversions"] += 1
        
        result = []
        for browser, stats in sorted(browser_stats.items(), key=lambda x: x[1]["clicks"], reverse=True):
            cr = (stats["conversions"] / stats["clicks"] * 100) if stats["clicks"] > 0 else 0
            result.append({
                "browser": browser,
                "clicks": stats["clicks"],
                "conversions": stats["conversions"],
                "cr": round(cr, 2)
            })
        
        return result
    
    def get_stats_by_os(self, start_date: str = "", end_date: str = "") -> List[Dict]:
        """Статистика по ОС"""
        os_stats = defaultdict(lambda: {"clicks": 0, "conversions": 0})
        
        for click in self.clicks:
            click_date = click.timestamp[:10]
            if start_date and click_date < start_date:
                continue
            if end_date and click_date > end_date:
                continue
            
            os_name = click.os or "Unknown"
            os_stats[os_name]["clicks"] += 1
            if click.converted:
                os_stats[os_name]["conversions"] += 1
        
        result = []
        for os_name, stats in sorted(os_stats.items(), key=lambda x: x[1]["clicks"], reverse=True):
            cr = (stats["conversions"] / stats["clicks"] * 100) if stats["clicks"] > 0 else 0
            result.append({
                "os": os_name,
                "clicks": stats["clicks"],
                "conversions": stats["conversions"],
                "cr": round(cr, 2)
            })
        
        return result
    
    def get_stats_by_device(self, start_date: str = "", end_date: str = "") -> List[Dict]:
        """Статистика по устройствам"""
        device_stats = defaultdict(lambda: {"clicks": 0, "conversions": 0})
        
        for click in self.clicks:
            click_date = click.timestamp[:10]
            if start_date and click_date < start_date:
                continue
            if end_date and click_date > end_date:
                continue
            
            device = click.device or "Unknown"
            device_stats[device]["clicks"] += 1
            if click.converted:
                device_stats[device]["conversions"] += 1
        
        result = []
        for device, stats in sorted(device_stats.items(), key=lambda x: x[1]["clicks"], reverse=True):
            cr = (stats["conversions"] / stats["clicks"] * 100) if stats["clicks"] > 0 else 0
            result.append({
                "device": device,
                "clicks": stats["clicks"],
                "conversions": stats["conversions"],
                "cr": round(cr, 2)
            })
        
        return result
    
    def get_stats_by_referrer(self, start_date: str = "", end_date: str = "") -> List[Dict]:
        """Статистика по рефереррам"""
        ref_stats = defaultdict(lambda: {"clicks": 0, "conversions": 0, "revenue": 0.0})
        
        for click in self.clicks:
            click_date = click.timestamp[:10]
            if start_date and click_date < start_date:
                continue
            if end_date and click_date > end_date:
                continue
            
            referrer = click.referrer_domain or "Direct"
            ref_stats[referrer]["clicks"] += 1
            if click.converted:
                ref_stats[referrer]["conversions"] += 1
                ref_stats[referrer]["revenue"] += click.revenue
        
        result = []
        for referrer, stats in sorted(ref_stats.items(), key=lambda x: x[1]["clicks"], reverse=True):
            cr = (stats["conversions"] / stats["clicks"] * 100) if stats["clicks"] > 0 else 0
            result.append({
                "referrer": referrer,
                "clicks": stats["clicks"],
                "conversions": stats["conversions"],
                "revenue": stats["revenue"],
                "cr": round(cr, 2)
            })
        
        return result
    
    def get_hourly_stats(self, date: str = "") -> List[Dict]:
        """Почасовая статистика"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        hourly = {i: {"clicks": 0, "conversions": 0} for i in range(24)}
        
        for click in self.clicks:
            if click.timestamp[:10] == date:
                hour = int(click.timestamp[11:13])
                hourly[hour]["clicks"] += 1
                if click.converted:
                    hourly[hour]["conversions"] += 1
        
        return [{"hour": h, **stats} for h, stats in hourly.items()]
    
    def get_realtime_stats(self, minutes: int = 60) -> Dict:
        """Статистика в реальном времени"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        cutoff_str = cutoff.isoformat()
        
        stats = {
            "period_minutes": minutes,
            "clicks": 0,
            "unique_clicks": 0,
            "bots": 0,
            "conversions": 0,
            "revenue": 0.0,
            "countries": defaultdict(int),
            "browsers": defaultdict(int),
            "devices": defaultdict(int)
        }
        
        seen_ips = set()
        
        for click in reversed(self.clicks):
            if click.timestamp < cutoff_str:
                break
            
            stats["clicks"] += 1
            if click.ip not in seen_ips:
                stats["unique_clicks"] += 1
                seen_ips.add(click.ip)
            if click.is_bot:
                stats["bots"] += 1
            if click.converted:
                stats["conversions"] += 1
                stats["revenue"] += click.revenue
            
            stats["countries"][click.country or "Unknown"] += 1
            stats["browsers"][click.browser or "Unknown"] += 1
            stats["devices"][click.device or "Unknown"] += 1
        
        stats["countries"] = dict(stats["countries"])
        stats["browsers"] = dict(stats["browsers"])
        stats["devices"] = dict(stats["devices"])
        
        return stats
    
    def get_overview(self) -> Dict:
        """Общий обзор статистики"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        today_stats = self.daily_stats.get(today, DailyStats(date=today))
        yesterday_stats = self.daily_stats.get(yesterday, DailyStats(date=yesterday))
        
        # Статистика за неделю
        week_stats = self.get_stats_by_period(week_ago, today)
        
        return {
            "today": asdict(today_stats),
            "yesterday": asdict(yesterday_stats),
            "week": week_stats["totals"],
            "total_clicks_all_time": len(self.clicks),
            "bot_rate": (sum(1 for c in self.clicks if c.is_bot) / len(self.clicks) * 100) if self.clicks else 0
        }


# Глобальный экземпляр
traffic_statistics = TrafficStatistics()
