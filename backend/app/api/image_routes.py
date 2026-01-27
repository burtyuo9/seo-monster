"""
SEO Monster - Image API Routes
API endpoints для управления изображениями и системой приоритетов
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os

# Добавляем путь к services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services'))

from services.image_providers import (
    image_provider_manager,
    ImageProvider,
    ImageCategory
)
from services.priority_system import (
    priority_manager,
    PriorityLevel,
    TaskType,
    ResourceType,
    PriorityTask,
    AgentPriority,
    ResourcePriority
)
from services.image_content_integration import (
    article_image_enricher
)


router = APIRouter(prefix="/api/images", tags=["Images"])
priority_router = APIRouter(prefix="/api/priority", tags=["Priority"])


# ==================== IMAGE ENDPOINTS ====================

class ImageSearchRequest(BaseModel):
    query: str
    category: str = "inline"
    count: int = 5
    min_width: int = 800
    orientation: str = "landscape"


class ProviderPriorityRequest(BaseModel):
    provider: str
    priority: int


class ProviderToggleRequest(BaseModel):
    provider: str
    enabled: bool


class ArticleEnrichRequest(BaseModel):
    title: str
    content: str
    keywords: List[str]
    meta_description: Optional[str] = ""


class PerformanceDataRequest(BaseModel):
    article_id: str
    image_performance: List[Dict[str, Any]]


@router.post("/search")
async def search_images(request: ImageSearchRequest):
    """Поиск изображений по запросу"""
    try:
        category = ImageCategory(request.category)
    except ValueError:
        category = ImageCategory.INLINE
    
    results = await image_provider_manager.search_images(
        query=request.query,
        category=category,
        count=request.count,
        min_width=request.min_width,
        orientation=request.orientation
    )
    
    return {
        "success": True,
        "count": len(results),
        "images": [
            {
                "id": img.id,
                "url": img.url,
                "thumbnail_url": img.thumbnail_url,
                "width": img.width,
                "height": img.height,
                "provider": img.provider.value,
                "photographer": img.photographer,
                "alt_text": img.alt_text,
                "tags": img.tags,
                "license": img.license,
                "relevance_score": img.relevance_score
            }
            for img in results
        ]
    }


@router.get("/providers")
async def get_providers():
    """Получение списка провайдеров изображений"""
    return {
        "success": True,
        "providers": image_provider_manager.get_providers_status()
    }


@router.post("/providers/priority")
async def set_provider_priority(request: ProviderPriorityRequest):
    """Установка приоритета провайдера"""
    try:
        provider = ImageProvider(request.provider)
        image_provider_manager.set_provider_priority(provider, request.priority)
        return {"success": True, "message": f"Priority set to {request.priority}"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid provider")


@router.post("/providers/toggle")
async def toggle_provider(request: ProviderToggleRequest):
    """Включение/выключение провайдера"""
    try:
        provider = ImageProvider(request.provider)
        image_provider_manager.enable_provider(provider, request.enabled)
        return {"success": True, "enabled": request.enabled}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid provider")


@router.get("/stats")
async def get_image_stats():
    """Получение статистики использования изображений"""
    return {
        "success": True,
        "stats": image_provider_manager.get_stats()
    }


@router.post("/enrich-article")
async def enrich_article_with_images(request: ArticleEnrichRequest):
    """Обогащение статьи изображениями"""
    article = {
        "title": request.title,
        "content": request.content,
        "keywords": request.keywords,
        "meta_description": request.meta_description
    }
    
    enriched = await article_image_enricher.enrich_article(article)
    
    return {
        "success": True,
        "images": enriched.get("images", {}),
        "hero_html": enriched.get("hero_html", ""),
        "inline_images_html": enriched.get("inline_images_html", []),
        "og_tags": enriched.get("og_tags", {})
    }


@router.post("/record-performance")
async def record_image_performance(request: PerformanceDataRequest):
    """Запись данных о производительности изображений"""
    article_image_enricher.record_article_performance(
        article_id=request.article_id,
        performance_data={"image_performance": request.image_performance}
    )
    
    return {"success": True, "message": "Performance data recorded"}


@router.get("/learning-report")
async def get_learning_report():
    """Получение отчёта об обучении системы изображений"""
    return {
        "success": True,
        "report": article_image_enricher.get_stats()
    }


@router.get("/categories")
async def get_image_categories():
    """Получение списка категорий изображений"""
    return {
        "success": True,
        "categories": [
            {"value": c.value, "name": c.name}
            for c in ImageCategory
        ]
    }


# ==================== PRIORITY ENDPOINTS ====================

class CreateTaskRequest(BaseModel):
    task_type: str
    data: Dict[str, Any]
    priority: Optional[str] = None
    deadline: Optional[str] = None
    dependencies: Optional[List[str]] = None


class AgentRegistrationRequest(BaseModel):
    agent_id: str
    name: str
    specialization: List[str]
    priority: int = 5
    max_load: int = 5


class ResourceRegistrationRequest(BaseModel):
    resource_id: str
    resource_type: str
    name: str
    priority: int = 5
    rate_limit: int = 100
    cost_per_request: float = 0.0


class UpdateAgentStatsRequest(BaseModel):
    agent_id: str
    success: bool
    response_time: float


class SetPriorityRequest(BaseModel):
    entity_id: str
    priority: int


@priority_router.post("/tasks/create")
async def create_priority_task(request: CreateTaskRequest):
    """Создание задачи с приоритетом"""
    try:
        task_type = TaskType(request.task_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task type")
    
    priority = None
    if request.priority:
        try:
            priority = PriorityLevel[request.priority.upper()]
        except KeyError:
            pass
    
    task = priority_manager.create_task(
        task_type=task_type,
        data=request.data,
        priority=priority,
        dependencies=request.dependencies
    )
    
    return {
        "success": True,
        "task_id": task.id,
        "priority": task.priority.name
    }


@priority_router.get("/tasks/next")
async def get_next_task():
    """Получение следующей задачи для выполнения"""
    task = priority_manager.get_next_task()
    
    if task is None:
        return {"success": True, "task": None}
    
    return {
        "success": True,
        "task": {
            "id": task.id,
            "type": task.type.value,
            "priority": task.priority.name,
            "data": task.data,
            "created_at": task.created_at.isoformat()
        }
    }


@priority_router.get("/tasks/pending")
async def get_pending_tasks():
    """Получение списка ожидающих задач"""
    tasks = priority_manager.task_queue.get_pending()
    
    return {
        "success": True,
        "count": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "type": t.type.value,
                "priority": t.priority.name,
                "status": t.status,
                "created_at": t.created_at.isoformat()
            }
            for t in sorted(tasks, key=lambda x: (x.priority.value, x.created_at))
        ]
    }


@priority_router.get("/tasks/distribution")
async def get_task_distribution():
    """Получение распределения задач по приоритетам"""
    return {
        "success": True,
        "distribution": priority_manager.get_task_distribution()
    }


@priority_router.post("/agents/register")
async def register_agent(request: AgentRegistrationRequest):
    """Регистрация агента в системе приоритетов"""
    try:
        specialization = [TaskType(s) for s in request.specialization]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid specialization")
    
    agent = AgentPriority(
        agent_id=request.agent_id,
        name=request.name,
        specialization=specialization,
        priority=request.priority,
        max_load=request.max_load
    )
    
    priority_manager.register_agent(agent)
    
    return {"success": True, "message": f"Agent {request.name} registered"}


@priority_router.get("/agents/best/{task_type}")
async def get_best_agent(task_type: str):
    """Получение лучшего агента для типа задачи"""
    try:
        tt = TaskType(task_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task type")
    
    agent = priority_manager.get_best_agent(tt)
    
    if agent is None:
        return {"success": True, "agent": None}
    
    return {
        "success": True,
        "agent": {
            "id": agent.agent_id,
            "name": agent.name,
            "priority": agent.priority,
            "performance_score": agent.performance_score,
            "current_load": agent.current_load,
            "max_load": agent.max_load
        }
    }


@priority_router.post("/agents/update-stats")
async def update_agent_stats(request: UpdateAgentStatsRequest):
    """Обновление статистики агента"""
    priority_manager.update_agent_stats(
        agent_id=request.agent_id,
        success=request.success,
        response_time=request.response_time
    )
    
    return {"success": True, "message": "Stats updated"}


@priority_router.post("/agents/priority")
async def set_agent_priority(request: SetPriorityRequest):
    """Установка приоритета агента"""
    priority_manager.set_agent_priority(request.entity_id, request.priority)
    return {"success": True, "message": f"Priority set to {request.priority}"}


@priority_router.get("/agents")
async def get_all_agents():
    """Получение списка всех агентов"""
    return {
        "success": True,
        "agents": [
            {
                "id": a.agent_id,
                "name": a.name,
                "priority": a.priority,
                "performance_score": a.performance_score,
                "success_rate": a.success_rate,
                "current_load": a.current_load,
                "max_load": a.max_load,
                "enabled": a.enabled,
                "specialization": [s.value for s in a.specialization]
            }
            for a in priority_manager.agents.values()
        ]
    }


@priority_router.post("/resources/register")
async def register_resource(request: ResourceRegistrationRequest):
    """Регистрация ресурса в системе приоритетов"""
    try:
        resource_type = ResourceType(request.resource_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resource type")
    
    resource = ResourcePriority(
        resource_id=request.resource_id,
        type=resource_type,
        name=request.name,
        priority=request.priority,
        rate_limit=request.rate_limit,
        cost_per_request=request.cost_per_request
    )
    
    priority_manager.register_resource(resource)
    
    return {"success": True, "message": f"Resource {request.name} registered"}


@priority_router.get("/resources/best/{resource_type}")
async def get_best_resource(resource_type: str):
    """Получение лучшего ресурса по типу"""
    try:
        rt = ResourceType(resource_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resource type")
    
    resource = priority_manager.get_best_resource(rt)
    
    if resource is None:
        return {"success": True, "resource": None}
    
    return {
        "success": True,
        "resource": {
            "id": resource.resource_id,
            "name": resource.name,
            "type": resource.type.value,
            "priority": resource.priority,
            "rate_limit": resource.rate_limit,
            "current_usage": resource.current_usage
        }
    }


@priority_router.get("/resources")
async def get_all_resources():
    """Получение списка всех ресурсов"""
    return {
        "success": True,
        "resources": [
            {
                "id": r.resource_id,
                "name": r.name,
                "type": r.type.value,
                "priority": r.priority,
                "rate_limit": r.rate_limit,
                "current_usage": r.current_usage,
                "reliability_score": r.reliability_score,
                "enabled": r.enabled
            }
            for r in priority_manager.resources.values()
        ]
    }


@priority_router.get("/stats")
async def get_priority_stats():
    """Получение статистики системы приоритетов"""
    return {
        "success": True,
        "stats": priority_manager.get_stats()
    }


@priority_router.get("/config/export")
async def export_priority_config():
    """Экспорт конфигурации приоритетов"""
    return {
        "success": True,
        "config": priority_manager.export_config()
    }


@priority_router.post("/config/import")
async def import_priority_config(config: Dict[str, Any]):
    """Импорт конфигурации приоритетов"""
    priority_manager.import_config(config)
    return {"success": True, "message": "Config imported"}


@priority_router.post("/optimize")
async def optimize_priorities():
    """Запуск оптимизации приоритетов"""
    priority_manager.optimize_priorities()
    return {"success": True, "message": "Optimization completed"}


@priority_router.get("/task-types")
async def get_task_types():
    """Получение списка типов задач"""
    return {
        "success": True,
        "task_types": [
            {"value": t.value, "name": t.name}
            for t in TaskType
        ]
    }


@priority_router.get("/priority-levels")
async def get_priority_levels():
    """Получение списка уровней приоритета"""
    return {
        "success": True,
        "levels": [
            {"value": p.value, "name": p.name}
            for p in PriorityLevel
        ]
    }
