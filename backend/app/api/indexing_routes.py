"""
SEO Monster - Indexing API Routes
API эндпоинты для модуля индексации
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import asyncio

import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.indexing_service import get_indexing_service, IndexingResult

router = APIRouter(prefix="/api/indexing", tags=["indexing"])


# Pydantic модели
class SubmitUrlRequest(BaseModel):
    url: str
    use_api: bool = False
    api_key: Optional[str] = None


class SubmitBulkRequest(BaseModel):
    urls: List[str]


class PingSitemapRequest(BaseModel):
    sitemap_url: str


class GenerateSitemapRequest(BaseModel):
    base_url: str
    urls: List[str]


class CrawlSiteRequest(BaseModel):
    base_url: str
    max_pages: int = 100


class CheckIndexingRequest(BaseModel):
    url: str


# API Endpoints

@router.get("/stats")
async def get_indexing_stats():
    """Получение статистики индексации"""
    service = get_indexing_service()
    return service.get_stats()


@router.get("/history")
async def get_indexing_history(
    limit: int = 100,
    url_filter: Optional[str] = None,
    status_filter: Optional[str] = None
):
    """Получение истории индексации"""
    service = get_indexing_service()
    return service.get_history(limit, url_filter, status_filter)


@router.get("/queue")
async def get_indexing_queue(status: Optional[str] = None):
    """Получение очереди индексации"""
    service = get_indexing_service()
    return service.get_queue(status)


@router.post("/submit")
async def submit_url_for_indexing(request: SubmitUrlRequest):
    """
    Отправка URL на индексацию
    
    - Если use_api=True и указан api_key, используется Google Indexing API
    - Иначе используется ping-метод
    """
    service = get_indexing_service()
    
    if request.use_api and request.api_key:
        result = await service.submit_to_google(request.url, request.api_key)
    else:
        result = await service.ping_google(request.url)
    
    return {
        "url": result.url,
        "status": result.status.value,
        "message": result.message,
        "timestamp": result.timestamp,
        "source": result.source
    }


@router.post("/submit-bulk")
async def submit_bulk_urls(request: SubmitBulkRequest, background_tasks: BackgroundTasks):
    """
    Массовая отправка URL на индексацию
    
    URL добавляются в очередь и обрабатываются в фоне
    """
    service = get_indexing_service()
    added = service.add_to_queue(request.urls)
    
    # Запускаем обработку в фоне
    background_tasks.add_task(service.process_queue, 10)
    
    return {
        "added": added,
        "total_in_queue": len(service.get_queue()),
        "message": f"Добавлено {added} URL в очередь индексации"
    }


@router.post("/ping-sitemap")
async def ping_sitemap(request: PingSitemapRequest):
    """
    Отправка ping всем поисковым системам о sitemap
    
    Уведомляет Google, Bing, Yandex о новом/обновленном sitemap
    """
    service = get_indexing_service()
    results = await service.ping_all_services(request.sitemap_url)
    
    return {
        "sitemap_url": request.sitemap_url,
        "results": [
            {
                "source": r.source,
                "status": r.status.value,
                "message": r.message
            }
            for r in results
        ],
        "success_count": len([r for r in results if r.status.value == "submitted"]),
        "error_count": len([r for r in results if r.status.value == "error"])
    }


@router.post("/check")
async def check_url_indexing(request: CheckIndexingRequest):
    """
    Проверка статуса индексации URL в Google
    """
    service = get_indexing_service()
    result = await service.check_indexing_status(request.url)
    
    return {
        "url": result.url,
        "status": result.status.value,
        "message": result.message,
        "timestamp": result.timestamp
    }


@router.post("/check-bulk")
async def check_bulk_indexing(request: SubmitBulkRequest):
    """
    Массовая проверка статуса индексации
    """
    service = get_indexing_service()
    results = []
    
    for url in request.urls[:20]:  # Ограничиваем до 20 URL
        result = await service.check_indexing_status(url)
        results.append({
            "url": result.url,
            "status": result.status.value,
            "message": result.message
        })
        await asyncio.sleep(1)  # Задержка между запросами
    
    indexed_count = len([r for r in results if r["status"] == "indexed"])
    
    return {
        "total": len(results),
        "indexed": indexed_count,
        "not_indexed": len(results) - indexed_count,
        "results": results
    }


@router.post("/generate-sitemap")
async def generate_sitemap(request: GenerateSitemapRequest):
    """
    Генерация sitemap.xml для списка URL
    """
    service = get_indexing_service()
    
    sitemap_xml = service.generate_sitemap(
        urls=request.urls,
        base_url=request.base_url
    )
    
    return {
        "base_url": request.base_url,
        "urls_count": len(request.urls),
        "sitemap_xml": sitemap_xml
    }


@router.post("/crawl-site")
async def crawl_site_for_urls(request: CrawlSiteRequest):
    """
    Сканирование сайта для получения списка URL
    
    Полезно для автоматического создания sitemap
    """
    service = get_indexing_service()
    
    try:
        urls = await service.crawl_site_urls(
            base_url=request.base_url,
            max_pages=min(request.max_pages, 500)  # Ограничение
        )
        
        return {
            "base_url": request.base_url,
            "urls_found": len(urls),
            "urls": urls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сканирования: {str(e)}")


@router.post("/process-queue")
async def process_indexing_queue(batch_size: int = 10):
    """
    Ручной запуск обработки очереди индексации
    """
    service = get_indexing_service()
    results = await service.process_queue(batch_size)
    
    return {
        "processed": len(results),
        "results": [
            {
                "url": r.url,
                "status": r.status.value,
                "message": r.message
            }
            for r in results
        ]
    }


@router.delete("/queue/clear")
async def clear_indexing_queue():
    """Очистка очереди индексации"""
    service = get_indexing_service()
    count = len(service.queue)
    service.queue = []
    service._save_json(service.queue_file, service.queue)
    
    return {"cleared": count, "message": f"Очищено {count} записей из очереди"}


@router.delete("/history/clear")
async def clear_indexing_history():
    """Очистка истории индексации"""
    service = get_indexing_service()
    count = len(service.history)
    service.history = []
    service._save_json(service.history_file, service.history)
    
    return {"cleared": count, "message": f"Очищено {count} записей из истории"}
