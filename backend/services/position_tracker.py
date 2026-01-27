"""
SEO Monster - Position Tracker Service
Сервис отслеживания позиций сайта в поисковых системах
"""

import os
import json
import asyncio
import aiohttp
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from urllib.parse import quote_plus, urlparse

# Путь к данным
DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/positions")
DATA_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS_FILE = DATA_DIR / "keywords.json"
HISTORY_FILE = DATA_DIR / "position_history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# User-Agent для запросов
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


class PositionTracker:
    """Трекер позиций в поисковых системах"""
    
    def __init__(self):
        self.keywords = self._load_keywords()
        self.history = self._load_history()
        self.settings = self._load_settings()
    
    def _load_keywords(self) -> List[Dict]:
        """Загрузка ключевых слов для отслеживания"""
        if KEYWORDS_FILE.exists():
            try:
                with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_keywords(self):
        """Сохранение ключевых слов"""
        with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.keywords, f, indent=2, ensure_ascii=False)
    
    def _load_history(self) -> List[Dict]:
        """Загрузка истории позиций"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_history(self):
        """Сохранение истории позиций"""
        # Храним историю за последние 90 дней
        cutoff = datetime.now() - timedelta(days=90)
        self.history = [
            h for h in self.history 
            if datetime.fromisoformat(h.get("timestamp", "2000-01-01")) > cutoff
        ]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def _load_settings(self) -> Dict:
        """Загрузка настроек"""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "check_depth": 100,  # Проверять до 100 позиции
            "delay_between_requests": 3,  # Задержка между запросами (секунды)
            "google_region": "ru",  # Регион Google
            "bing_region": "ru-RU"  # Регион Bing
        }
    
    def _save_settings(self):
        """Сохранение настроек"""
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)
    
    def add_keyword(self, domain: str, keyword: str, target_url: Optional[str] = None) -> Dict:
        """Добавление ключевого слова для отслеживания"""
        # Проверяем, не существует ли уже
        for kw in self.keywords:
            if kw["domain"] == domain and kw["keyword"] == keyword:
                return {"status": "exists", "keyword": keyword}
        
        keyword_data = {
            "id": len(self.keywords) + 1,
            "domain": domain,
            "keyword": keyword,
            "target_url": target_url,
            "added_at": datetime.now().isoformat(),
            "last_check": None,
            "google_position": None,
            "bing_position": None
        }
        
        self.keywords.append(keyword_data)
        self._save_keywords()
        
        return {"status": "added", "keyword": keyword_data}
    
    def remove_keyword(self, keyword_id: int) -> Dict:
        """Удаление ключевого слова"""
        self.keywords = [kw for kw in self.keywords if kw.get("id") != keyword_id]
        self._save_keywords()
        return {"status": "removed", "id": keyword_id}
    
    def get_keywords(self, domain: Optional[str] = None) -> List[Dict]:
        """Получение списка ключевых слов"""
        if domain:
            return [kw for kw in self.keywords if kw.get("domain") == domain]
        return self.keywords
    
    def import_keywords(self, data: str, domain: str) -> Dict:
        """
        Импорт ключевых слов из текста
        Формат: одно ключевое слово на строку
        """
        lines = data.strip().split('\n')
        added = 0
        skipped = 0
        
        for line in lines:
            keyword = line.strip()
            if keyword:
                result = self.add_keyword(domain, keyword)
                if result["status"] == "added":
                    added += 1
                else:
                    skipped += 1
        
        return {"added": added, "skipped": skipped}
    
    async def check_google_position(self, domain: str, keyword: str) -> Optional[int]:
        """
        Проверка позиции в Google
        Использует парсинг поисковой выдачи
        """
        try:
            query = quote_plus(keyword)
            url = f"https://www.google.com/search?q={query}&num=100&hl={self.settings['google_region']}"
            
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    
                    # Парсим результаты
                    position = self._parse_google_results(html, domain)
                    return position
                    
        except Exception as e:
            print(f"Google check error: {e}")
            return None
    
    def _parse_google_results(self, html: str, domain: str) -> Optional[int]:
        """Парсинг результатов Google"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Ищем все ссылки в результатах
            position = 0
            for result in soup.find_all('div', class_='g'):
                position += 1
                
                # Ищем ссылку
                link = result.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    if domain in href:
                        return position
                
                if position >= self.settings["check_depth"]:
                    break
            
            return None  # Не найден в топ-N
            
        except Exception as e:
            print(f"Parse error: {e}")
            return None
    
    async def check_bing_position(self, domain: str, keyword: str) -> Optional[int]:
        """
        Проверка позиции в Bing
        """
        try:
            query = quote_plus(keyword)
            url = f"https://www.bing.com/search?q={query}&count=50&setlang={self.settings['bing_region']}"
            
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    position = self._parse_bing_results(html, domain)
                    return position
                    
        except Exception as e:
            print(f"Bing check error: {e}")
            return None
    
    def _parse_bing_results(self, html: str, domain: str) -> Optional[int]:
        """Парсинг результатов Bing"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            position = 0
            for result in soup.find_all('li', class_='b_algo'):
                position += 1
                
                link = result.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    if domain in href:
                        return position
                
                if position >= self.settings["check_depth"]:
                    break
            
            return None
            
        except Exception as e:
            print(f"Parse error: {e}")
            return None
    
    async def check_all_positions(self, domain: Optional[str] = None) -> List[Dict]:
        """Проверка позиций для всех ключевых слов"""
        keywords_to_check = self.get_keywords(domain)
        results = []
        
        for kw in keywords_to_check:
            kw_domain = kw["domain"]
            keyword = kw["keyword"]
            
            print(f"Checking: {keyword} for {kw_domain}")
            
            # Проверяем Google
            google_pos = await self.check_google_position(kw_domain, keyword)
            await asyncio.sleep(self.settings["delay_between_requests"])
            
            # Проверяем Bing
            bing_pos = await self.check_bing_position(kw_domain, keyword)
            await asyncio.sleep(self.settings["delay_between_requests"])
            
            # Получаем предыдущие позиции
            prev_google = kw.get("google_position")
            prev_bing = kw.get("bing_position")
            
            # Вычисляем изменения
            google_change = None
            bing_change = None
            
            if prev_google is not None and google_pos is not None:
                google_change = prev_google - google_pos  # Положительное = рост
            if prev_bing is not None and bing_pos is not None:
                bing_change = prev_bing - bing_pos
            
            # Обновляем данные
            kw["google_position"] = google_pos
            kw["bing_position"] = bing_pos
            kw["last_check"] = datetime.now().isoformat()
            
            result = {
                "keyword_id": kw["id"],
                "domain": kw_domain,
                "keyword": keyword,
                "google_position": google_pos,
                "google_change": google_change,
                "bing_position": bing_pos,
                "bing_change": bing_change,
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(result)
            
            # Сохраняем в историю
            self.history.append(result)
        
        # Сохраняем обновления
        self._save_keywords()
        self._save_history()
        
        return results
    
    def get_latest_positions(self, domain: Optional[str] = None) -> List[Dict]:
        """Получение последних позиций"""
        keywords = self.get_keywords(domain)
        return [{
            "keyword": kw["keyword"],
            "domain": kw["domain"],
            "google_position": kw.get("google_position"),
            "bing_position": kw.get("bing_position"),
            "last_check": kw.get("last_check")
        } for kw in keywords]
    
    def get_position_history(self, keyword_id: int, days: int = 30) -> List[Dict]:
        """Получение истории позиций для ключевого слова"""
        cutoff = datetime.now() - timedelta(days=days)
        
        return [
            h for h in self.history
            if h.get("keyword_id") == keyword_id 
            and datetime.fromisoformat(h.get("timestamp", "2000-01-01")) > cutoff
        ]
    
    def get_position_summary(self, domain: Optional[str] = None) -> Dict:
        """Получение сводки по позициям"""
        keywords = self.get_keywords(domain)
        
        summary = {
            "total_keywords": len(keywords),
            "google": {
                "top_3": 0,
                "top_10": 0,
                "top_30": 0,
                "top_100": 0,
                "not_found": 0
            },
            "bing": {
                "top_3": 0,
                "top_10": 0,
                "top_30": 0,
                "top_100": 0,
                "not_found": 0
            },
            "improved": 0,
            "declined": 0,
            "stable": 0
        }
        
        for kw in keywords:
            # Google
            g_pos = kw.get("google_position")
            if g_pos is None:
                summary["google"]["not_found"] += 1
            elif g_pos <= 3:
                summary["google"]["top_3"] += 1
            elif g_pos <= 10:
                summary["google"]["top_10"] += 1
            elif g_pos <= 30:
                summary["google"]["top_30"] += 1
            elif g_pos <= 100:
                summary["google"]["top_100"] += 1
            else:
                summary["google"]["not_found"] += 1
            
            # Bing
            b_pos = kw.get("bing_position")
            if b_pos is None:
                summary["bing"]["not_found"] += 1
            elif b_pos <= 3:
                summary["bing"]["top_3"] += 1
            elif b_pos <= 10:
                summary["bing"]["top_10"] += 1
            elif b_pos <= 30:
                summary["bing"]["top_30"] += 1
            elif b_pos <= 100:
                summary["bing"]["top_100"] += 1
            else:
                summary["bing"]["not_found"] += 1
        
        return summary
    
    def generate_report_section(self) -> str:
        """Генерация секции отчёта по позициям для Telegram"""
        keywords = self.keywords
        
        if not keywords:
            return """
🎯 <b>Позиции в поисковиках</b>

<i>Ключевые слова не настроены.</i>
<i>Добавьте ключевые слова в разделе "Позиции"</i>
"""
        
        summary = self.get_position_summary()
        
        report = """
🎯 <b>Позиции в поисковиках</b>

"""
        
        # Сводка по Google
        report += f"""<b>Google:</b>
  🥇 Топ-3: {summary['google']['top_3']}
  🥈 Топ-10: {summary['google']['top_10']}
  🥉 Топ-30: {summary['google']['top_30']}
  📍 Топ-100: {summary['google']['top_100']}
  ❓ Не найдено: {summary['google']['not_found']}

"""
        
        # Сводка по Bing
        report += f"""<b>Bing:</b>
  🥇 Топ-3: {summary['bing']['top_3']}
  🥈 Топ-10: {summary['bing']['top_10']}
  🥉 Топ-30: {summary['bing']['top_30']}
  📍 Топ-100: {summary['bing']['top_100']}
  ❓ Не найдено: {summary['bing']['not_found']}

"""
        
        # Детали по ключевым словам (топ-10 по позиции)
        sorted_keywords = sorted(
            keywords,
            key=lambda x: (x.get("google_position") or 999, x.get("bing_position") or 999)
        )[:10]
        
        if sorted_keywords:
            report += "<b>Топ ключевые слова:</b>\n"
            
            for kw in sorted_keywords:
                keyword = kw["keyword"][:25]
                g_pos = kw.get("google_position")
                b_pos = kw.get("bing_position")
                
                g_str = str(g_pos) if g_pos else "—"
                b_str = str(b_pos) if b_pos else "—"
                
                # Определяем тренд (если есть история)
                trend = ""
                for h in reversed(self.history[-100:]):
                    if h.get("keyword_id") == kw.get("id"):
                        g_change = h.get("google_change")
                        if g_change is not None:
                            if g_change > 0:
                                trend = "📈"
                            elif g_change < 0:
                                trend = "📉"
                            else:
                                trend = "➡️"
                        break
                
                report += f"  • {keyword}: G:{g_str} B:{b_str} {trend}\n"
        
        return report


# Singleton instance
_position_tracker = None

def get_position_tracker() -> PositionTracker:
    """Получение экземпляра трекера позиций"""
    global _position_tracker
    if _position_tracker is None:
        _position_tracker = PositionTracker()
    return _position_tracker
