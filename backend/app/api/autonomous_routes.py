"""
SEO Monster - API роуты для автономного автопилота
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
from pathlib import Path

# Добавляем путь к сервисам
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from autonomous_autopilot import autonomous_autopilot
from autonomous_content_engine import autonomous_content_engine
from autonomous_site_analyzer import autonomous_site_analyzer

router = APIRouter(prefix="/api/autonomous", tags=["Autonomous"])


# Модели запросов
class SiteRequest(BaseModel):
    url: str
    name: Optional[str] = None
    language: Optional[str] = "en"


class GenerateRequest(BaseModel):
    topic: str
    keywords: Optional[List[str]] = None
    content_type: Optional[str] = "guide"
    language: Optional[str] = "en"
    word_count: Optional[int] = 1000
    autopublish: Optional[bool] = False  # Auto-publish to MANUS.space after generation


class RunNowRequest(BaseModel):
    url: str
    language: Optional[str] = "en"
    articles_count: Optional[int] = 3


class SettingsRequest(BaseModel):
    auto_analyze: Optional[bool] = None
    auto_generate: Optional[bool] = None
    articles_per_day: Optional[int] = None
    min_word_count: Optional[int] = None
    max_word_count: Optional[int] = None
    languages: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    external_ai_enabled: Optional[bool] = None


# === Автопилот ===

@router.get("/status")
async def get_autopilot_status():
    """Получить статус автопилота"""
    return autonomous_autopilot.get_status()


@router.post("/start")
async def start_autopilot():
    """Запустить автопилот"""
    return autonomous_autopilot.start()


@router.post("/stop")
async def stop_autopilot():
    """Остановить автопилот"""
    return autonomous_autopilot.stop()


@router.post("/pause")
async def pause_autopilot():
    """Приостановить автопилот"""
    return autonomous_autopilot.pause()


@router.post("/resume")
async def resume_autopilot():
    """Возобновить автопилот"""
    return autonomous_autopilot.resume()


@router.post("/run-now")
async def run_now(request: RunNowRequest):
    """Немедленно запустить генерацию для сайта"""
    return autonomous_autopilot.run_now(
        url=request.url,
        language=request.language,
        articles_count=request.articles_count
    )


@router.get("/logs")
async def get_logs(limit: int = 50):
    """Получить логи автопилота"""
    return {"logs": autonomous_autopilot.get_logs(limit)}


@router.put("/settings")
async def update_settings(request: SettingsRequest):
    """Обновить настройки автопилота"""
    settings = {k: v for k, v in request.dict().items() if v is not None}
    return autonomous_autopilot.update_settings(settings)


# === Сайты ===

@router.post("/sites")
async def add_site(request: SiteRequest):
    """Добавить сайт для мониторинга"""
    return autonomous_autopilot.add_site(
        url=request.url,
        name=request.name,
        language=request.language
    )


@router.delete("/sites")
async def remove_site(url: str):
    """Удалить сайт"""
    return autonomous_autopilot.remove_site(url)


@router.get("/sites")
async def get_sites():
    """Получить список сайтов"""
    return {"sites": autonomous_autopilot.settings.get("sites", [])}


# === Анализ сайтов ===

@router.post("/analyze")
async def analyze_site(request: SiteRequest):
    """Быстрый анализ сайта"""
    result = autonomous_site_analyzer.quick_analyze(request.url)
    return result


@router.get("/analysis-history")
async def get_analysis_history():
    """Получить историю анализов"""
    return {"history": autonomous_site_analyzer.get_analysis_history()}


# === Генерация контента ===

@router.post("/generate")
async def generate_content(request: GenerateRequest):
    """Сгенерировать статью с опциональной автопубликацией на MANUS.space"""
    result = autonomous_content_engine.generate_article(
        topic=request.topic,
        keywords=request.keywords,
        content_type=request.content_type,
        word_count=request.word_count,
        language=request.language
    )
    
    # Auto-publish if enabled
    if request.autopublish and result.get('id'):  # Check if article was generated (has id)
        try:
            from services.landing_generator import landing_generator
            import os
            import json
            from datetime import datetime
            
            # Generate landing page
            landing_result = landing_generator.generate_landing(
                title=result.get('title', request.topic),
                content=result.get('content', ''),
                language=request.language,
                style='glassmorphism_dark',
                keywords=request.keywords,
                author='SEO Monster'
            )
            
            # Save to landings directory for Manus to pick up
            landings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "landings")
            os.makedirs(landings_dir, exist_ok=True)
            
            slug = landing_result['slug']
            html_path = os.path.join(landings_dir, f"{slug}.html")
            meta_path = os.path.join(landings_dir, f"{slug}.json")
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(landing_result['html'])
            
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'id': f"autopublish_{slug[:20]}",
                    'slug': slug,
                    'title': landing_result['title'],
                    'meta_description': landing_result['meta_description'],
                    'keywords': landing_result.get('keywords', []),
                    'language': request.language,
                    'word_count': landing_result['word_count'],
                    'created_at': datetime.utcnow().isoformat(),
                    'autopublished': True
                }, f, ensure_ascii=False, indent=2)
            
            result['autopublish'] = {
                'success': True,
                'slug': slug,
                'preview_url': f'/api/publishing/preview/{slug}',
                'pending_url': f'https://{slug}.manus.space',
                'message': 'Article queued for auto-publishing to MANUS.space'
            }
        except Exception as e:
            result['autopublish'] = {
                'success': False,
                'error': str(e)
            }
    
    return result


@router.get("/articles")
async def get_articles():
    """Получить список сгенерированных статей"""
    return {"articles": autonomous_content_engine.get_generated_articles()}


@router.get("/articles/{article_id}")
async def get_article_by_id(article_id: str):
    """Получить статью по ID с полным контентом"""
    articles = autonomous_content_engine.get_generated_articles()
    for article in articles:
        if article.get('id') == article_id:
            return article
    raise HTTPException(status_code=404, detail="Article not found")


@router.post("/analyze-topic")
async def analyze_topic(topic: str):
    """Анализ темы для генерации контента"""
    return autonomous_content_engine.analyze_topic(topic)


# === Задачи ===

@router.post("/tasks/analyze")
async def add_analyze_task(request: SiteRequest):
    """Добавить задачу на анализ сайта"""
    return autonomous_autopilot.add_task("analyze_site", {"url": request.url})


@router.post("/tasks/generate")
async def add_generate_task(request: GenerateRequest):
    """Добавить задачу на генерацию контента"""
    return autonomous_autopilot.add_task("generate_content", request.dict())


@router.post("/tasks/pipeline")
async def add_pipeline_task(request: RunNowRequest):
    """Добавить задачу полного пайплайна"""
    return autonomous_autopilot.add_task("full_pipeline", request.dict())


@router.get("/tasks/queue")
async def get_task_queue():
    """Получить очередь задач"""
    return {
        "queue": [
            {
                "id": task.id,
                "type": task.type,
                "status": task.status,
                "created_at": task.created_at
            }
            for task in autonomous_autopilot.task_queue
        ],
        "current": {
            "id": autonomous_autopilot.current_task.id,
            "type": autonomous_autopilot.current_task.type,
            "status": autonomous_autopilot.current_task.status
        } if autonomous_autopilot.current_task else None
    }


@router.get("/tasks/completed")
async def get_completed_tasks(limit: int = 20):
    """Получить завершенные задачи"""
    return {
        "tasks": [
            {
                "id": task.id,
                "type": task.type,
                "status": task.status,
                "created_at": task.created_at,
                "completed_at": task.completed_at,
                "error": task.error
            }
            for task in autonomous_autopilot.completed_tasks[-limit:]
        ]
    }
