"""
SEO Monster - Indexing Service
Модуль для индексации сайтов в поисковых системах
"""

import asyncio
import aiohttp
import json
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndexingStatus(str, Enum):
    PENDING = "pending"
    INDEXED = "indexed"
    NOT_INDEXED = "not_indexed"
    ERROR = "error"
    SUBMITTED = "submitted"


@dataclass
class IndexingResult:
    url: str
    status: IndexingStatus
    message: str
    timestamp: str
    source: str  # google, bing, yandex, ping


@dataclass
class SitemapEntry:
    loc: str
    lastmod: Optional[str] = None
    changefreq: Optional[str] = None
    priority: Optional[float] = None


class IndexingService:
    """Сервис индексации сайтов"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "data/indexing")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы данных
        self.history_file = self.data_dir / "indexing_history.json"
        self.queue_file = self.data_dir / "indexing_queue.json"
        
        # Ping-сервисы для уведомления поисковиков
        self.ping_services = [
            "http://www.google.com/ping?sitemap={sitemap_url}",
            "http://www.bing.com/ping?sitemap={sitemap_url}",
            "http://ping.blogs.yandex.ru/RPC2",
            "http://rpc.pingomatic.com/",
            "http://blogsearch.google.com/ping/RPC2",
            "http://api.moreover.com/RPC2",
            "http://www.blogdigger.com/RPC2",
            "http://www.blogshares.com/rpc.php",
            "http://www.blogsnow.com/ping",
            "http://www.blogstreet.com/xrbin/xmlrpc.cgi",
        ]
        
        # Google Indexing API endpoints
        self.google_indexing_api = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        
        # Загружаем историю
        self.history: List[Dict] = self._load_json(self.history_file, [])
        self.queue: List[Dict] = self._load_json(self.queue_file, [])
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Загрузка JSON файла"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, path: Path, data: Any):
        """Сохранение JSON файла"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    async def submit_to_google(self, url: str, api_key: str = None) -> IndexingResult:
        """
        Отправка URL в Google Indexing API
        
        Args:
            url: URL для индексации
            api_key: Google API ключ (опционально)
        
        Returns:
            IndexingResult
        """
        timestamp = datetime.now().isoformat()
        
        # Если нет API ключа, используем ping
        if not api_key:
            return await self.ping_google(url)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "url": url,
                "type": "URL_UPDATED"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.google_indexing_api,
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = IndexingResult(
                            url=url,
                            status=IndexingStatus.SUBMITTED,
                            message="URL успешно отправлен в Google Indexing API",
                            timestamp=timestamp,
                            source="google_api"
                        )
                    else:
                        error_text = await response.text()
                        result = IndexingResult(
                            url=url,
                            status=IndexingStatus.ERROR,
                            message=f"Ошибка Google API: {error_text}",
                            timestamp=timestamp,
                            source="google_api"
                        )
        except Exception as e:
            result = IndexingResult(
                url=url,
                status=IndexingStatus.ERROR,
                message=f"Ошибка: {str(e)}",
                timestamp=timestamp,
                source="google_api"
            )
        
        self._add_to_history(result)
        return result
    
    async def ping_google(self, url: str) -> IndexingResult:
        """Ping Google о новом контенте"""
        timestamp = datetime.now().isoformat()
        
        try:
            ping_url = f"http://www.google.com/ping?sitemap={url}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(ping_url, timeout=30) as response:
                    if response.status == 200:
                        result = IndexingResult(
                            url=url,
                            status=IndexingStatus.SUBMITTED,
                            message="Ping отправлен в Google",
                            timestamp=timestamp,
                            source="google_ping"
                        )
                    else:
                        result = IndexingResult(
                            url=url,
                            status=IndexingStatus.ERROR,
                            message=f"Google ping вернул статус {response.status}",
                            timestamp=timestamp,
                            source="google_ping"
                        )
        except Exception as e:
            result = IndexingResult(
                url=url,
                status=IndexingStatus.ERROR,
                message=f"Ошибка ping: {str(e)}",
                timestamp=timestamp,
                source="google_ping"
            )
        
        self._add_to_history(result)
        return result
    
    async def ping_all_services(self, sitemap_url: str) -> List[IndexingResult]:
        """
        Отправка ping во все сервисы
        
        Args:
            sitemap_url: URL sitemap.xml
        
        Returns:
            Список результатов
        """
        results = []
        timestamp = datetime.now().isoformat()
        
        # Простые HTTP ping сервисы
        simple_ping_services = [
            ("Google", f"http://www.google.com/ping?sitemap={sitemap_url}"),
            ("Bing", f"http://www.bing.com/ping?sitemap={sitemap_url}"),
            ("Yandex", f"http://blogs.yandex.ru/pings/?status=success&url={sitemap_url}"),
        ]
        
        async with aiohttp.ClientSession() as session:
            for name, ping_url in simple_ping_services:
                try:
                    async with session.get(ping_url, timeout=30) as response:
                        if response.status in [200, 204]:
                            result = IndexingResult(
                                url=sitemap_url,
                                status=IndexingStatus.SUBMITTED,
                                message=f"Ping успешно отправлен в {name}",
                                timestamp=timestamp,
                                source=name.lower()
                            )
                        else:
                            result = IndexingResult(
                                url=sitemap_url,
                                status=IndexingStatus.ERROR,
                                message=f"{name} вернул статус {response.status}",
                                timestamp=timestamp,
                                source=name.lower()
                            )
                except Exception as e:
                    result = IndexingResult(
                        url=sitemap_url,
                        status=IndexingStatus.ERROR,
                        message=f"Ошибка {name}: {str(e)}",
                        timestamp=timestamp,
                        source=name.lower()
                    )
                
                results.append(result)
                self._add_to_history(result)
        
        return results
    
    async def check_indexing_status(self, url: str) -> IndexingResult:
        """
        Проверка статуса индексации URL в Google
        
        Args:
            url: URL для проверки
        
        Returns:
            IndexingResult
        """
        timestamp = datetime.now().isoformat()
        
        try:
            # Используем Google Search для проверки
            search_url = f"https://www.google.com/search?q=site:{url}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        text = await response.text()
                        
                        # Проверяем наличие результатов
                        if "did not match any documents" in text or "ничего не найдено" in text.lower():
                            result = IndexingResult(
                                url=url,
                                status=IndexingStatus.NOT_INDEXED,
                                message="URL не найден в индексе Google",
                                timestamp=timestamp,
                                source="google_check"
                            )
                        else:
                            result = IndexingResult(
                                url=url,
                                status=IndexingStatus.INDEXED,
                                message="URL найден в индексе Google",
                                timestamp=timestamp,
                                source="google_check"
                            )
                    else:
                        result = IndexingResult(
                            url=url,
                            status=IndexingStatus.ERROR,
                            message=f"Ошибка проверки: статус {response.status}",
                            timestamp=timestamp,
                            source="google_check"
                        )
        except Exception as e:
            result = IndexingResult(
                url=url,
                status=IndexingStatus.ERROR,
                message=f"Ошибка проверки: {str(e)}",
                timestamp=timestamp,
                source="google_check"
            )
        
        self._add_to_history(result)
        return result
    
    def generate_sitemap(
        self, 
        urls: List[str], 
        base_url: str,
        output_path: str = None
    ) -> str:
        """
        Генерация sitemap.xml
        
        Args:
            urls: Список URL для включения
            base_url: Базовый URL сайта
            output_path: Путь для сохранения (опционально)
        
        Returns:
            XML строка sitemap
        """
        # Создаем корневой элемент
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        # Текущая дата
        today = datetime.now().strftime("%Y-%m-%d")
        
        for url in urls:
            # Нормализуем URL
            if not url.startswith("http"):
                url = urljoin(base_url, url)
            
            url_element = ET.SubElement(urlset, "url")
            
            loc = ET.SubElement(url_element, "loc")
            loc.text = url
            
            lastmod = ET.SubElement(url_element, "lastmod")
            lastmod.text = today
            
            changefreq = ET.SubElement(url_element, "changefreq")
            changefreq.text = "weekly"
            
            priority = ET.SubElement(url_element, "priority")
            # Главная страница имеет высший приоритет
            if url.rstrip("/") == base_url.rstrip("/"):
                priority.text = "1.0"
            else:
                priority.text = "0.8"
        
        # Генерируем XML
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content = ET.tostring(urlset, encoding="unicode")
        
        sitemap_xml = xml_declaration + xml_content
        
        # Сохраняем если указан путь
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(sitemap_xml)
        
        return sitemap_xml
    
    async def crawl_site_urls(self, base_url: str, max_pages: int = 100) -> List[str]:
        """
        Сканирование сайта для получения списка URL
        
        Args:
            base_url: Базовый URL сайта
            max_pages: Максимальное количество страниц
        
        Returns:
            Список найденных URL
        """
        visited = set()
        to_visit = [base_url]
        found_urls = []
        
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        async with aiohttp.ClientSession() as session:
            while to_visit and len(found_urls) < max_pages:
                url = to_visit.pop(0)
                
                if url in visited:
                    continue
                
                visited.add(url)
                
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status != 200:
                            continue
                        
                        content_type = response.headers.get("Content-Type", "")
                        if "text/html" not in content_type:
                            continue
                        
                        html = await response.text()
                        found_urls.append(url)
                        
                        # Извлекаем ссылки
                        links = re.findall(r'href=["\']([^"\']+)["\']', html)
                        
                        for link in links:
                            # Нормализуем ссылку
                            if link.startswith("/"):
                                link = urljoin(base_url, link)
                            elif not link.startswith("http"):
                                continue
                            
                            # Проверяем что ссылка на тот же домен
                            parsed_link = urlparse(link)
                            if parsed_link.netloc == base_domain:
                                # Убираем якоря и параметры
                                clean_link = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
                                if clean_link not in visited and clean_link not in to_visit:
                                    to_visit.append(clean_link)
                
                except Exception as e:
                    logger.warning(f"Ошибка при сканировании {url}: {e}")
                    continue
        
        return found_urls
    
    def add_to_queue(self, urls: List[str]) -> int:
        """
        Добавление URL в очередь индексации
        
        Args:
            urls: Список URL
        
        Returns:
            Количество добавленных URL
        """
        added = 0
        existing_urls = {item["url"] for item in self.queue}
        
        for url in urls:
            if url not in existing_urls:
                self.queue.append({
                    "url": url,
                    "added_at": datetime.now().isoformat(),
                    "status": "pending"
                })
                added += 1
        
        self._save_json(self.queue_file, self.queue)
        return added
    
    async def process_queue(self, batch_size: int = 10) -> List[IndexingResult]:
        """
        Обработка очереди индексации
        
        Args:
            batch_size: Размер пакета
        
        Returns:
            Результаты обработки
        """
        results = []
        pending = [item for item in self.queue if item.get("status", "pending") == "pending"][:batch_size]
        
        for item in pending:
            # Отправляем ping
            result = await self.ping_google(item["url"])
            results.append(result)
            
            # Обновляем статус в очереди
            for q_item in self.queue:
                if q_item["url"] == item["url"]:
                    q_item["status"] = result.status.value
                    q_item["processed_at"] = datetime.now().isoformat()
                    break
            
            # Небольшая задержка между запросами
            await asyncio.sleep(1)
        
        self._save_json(self.queue_file, self.queue)
        return results
    
    def _add_to_history(self, result: IndexingResult):
        """Добавление результата в историю"""
        self.history.append(asdict(result))
        
        # Ограничиваем размер истории
        if len(self.history) > 10000:
            self.history = self.history[-5000:]
        
        self._save_json(self.history_file, self.history)
    
    def get_history(
        self, 
        limit: int = 100, 
        url_filter: str = None,
        status_filter: str = None
    ) -> List[Dict]:
        """
        Получение истории индексации
        
        Args:
            limit: Максимальное количество записей
            url_filter: Фильтр по URL
            status_filter: Фильтр по статусу
        
        Returns:
            Список записей истории
        """
        filtered = self.history
        
        if url_filter:
            filtered = [h for h in filtered if url_filter.lower() in h["url"].lower()]
        
        if status_filter:
            filtered = [h for h in filtered if h["status"] == status_filter]
        
        return filtered[-limit:][::-1]  # Последние записи первыми
    
    def get_queue(self, status: str = None) -> List[Dict]:
        """Получение очереди индексации"""
        if status:
            return [item for item in self.queue if item.get("status", "pending") == status]
        return self.queue
    
    def get_stats(self) -> Dict:
        """Получение статистики индексации"""
        total = len(self.history)
        
        stats = {
            "total_requests": total,
            "submitted": len([h for h in self.history if h["status"] == "submitted"]),
            "indexed": len([h for h in self.history if h["status"] == "indexed"]),
            "not_indexed": len([h for h in self.history if h["status"] == "not_indexed"]),
            "errors": len([h for h in self.history if h["status"] == "error"]),
            "queue_pending": len([q for q in self.queue if q.get("status", "pending") == "pending"]),
            "queue_total": len(self.queue),
        }
        
        # Уникальные домены
        domains = set()
        for h in self.history:
            try:
                parsed = urlparse(h["url"])
                domains.add(parsed.netloc)
            except:
                pass
        stats["unique_domains"] = len(domains)
        
        return stats


# Глобальный экземпляр сервиса
_indexing_service = None

def get_indexing_service() -> IndexingService:
    """Получение глобального экземпляра сервиса"""
    global _indexing_service
    if _indexing_service is None:
        _indexing_service = IndexingService()
    return _indexing_service
