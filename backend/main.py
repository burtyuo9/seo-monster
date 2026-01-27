"""
SEO Monster - Автономный ИИ-агент для SEO-продвижения.
Главный файл приложения.
"""

import os
import sys

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.routes import (
    sites_router,
    platforms_router,
    content_router,
    tasks_router,
    system_router,
    learning_router,
    backup_router
)
from app.api.agent_routes import (
    agent_router,
    finder_router,
    browser_router
)
from app.api.session_routes import router as session_router
from app.api.indexing_routes import router as indexing_router
from app.api.autopilot_routes import router as autopilot_router
from app.api.account_routes import router as account_router
from app.api.chat_routes import router as chat_router
from app.api.telegram_routes import router as telegram_router
from app.api.position_routes import router as position_router
from app.api.ai_routes import router as ai_router
from app.api.hosting_routes import router as hosting_router
from app.api.tds_routes import router as tds_router
from app.api.github_routes import router as github_router
from app.api.image_routes import router as image_router, priority_router
from app.api.smart_image_routes import router as smart_image_router
from app.api.diagnostics_routes import router as diagnostics_router
from app.api.ad_campaigns_routes import router as ad_campaigns_router
from app.api.ads_tracker_routes import router as ads_tracker_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    print(f"🚀 Запуск {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    print("✅ База данных инициализирована")
    
    yield
    
    # Shutdown
    await close_db()
    print("👋 Приложение остановлено")


# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## SEO Monster - Автономный ИИ-агент для SEO-продвижения

### Возможности:
- 🔍 **Анализ сайтов** - автоматическое извлечение ключевых слов и определение ниши
- ✍️ **Генерация контента** - создание уникальных статей на разных языках
- 📤 **Автопостинг** - публикация контента на площадках
- 📊 **Аналитика** - отслеживание результатов и самообучение
- 💾 **Бэкапы** - сохранение состояния системы

### Поддерживаемые языки:
🇷🇺 Русский | 🇺🇸 English | 🇩🇪 Deutsch | 🇫🇷 Français | 🇪🇸 Español | 🇮🇹 Italiano | 🇵🇹 Português | 🇨🇳 中文 | 🇯🇵 日本語 | 🇰🇷 한국어 | 🇸🇦 العربية | 🇹🇷 Türkçe
    """,
    lifespan=lifespan
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров API
app.include_router(sites_router, prefix="/api")
app.include_router(platforms_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(learning_router, prefix="/api")
app.include_router(backup_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(finder_router, prefix="/api")
app.include_router(browser_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.include_router(indexing_router)
app.include_router(autopilot_router)
app.include_router(account_router)
app.include_router(chat_router)
app.include_router(telegram_router)
app.include_router(position_router)
app.include_router(ai_router)
app.include_router(hosting_router)
app.include_router(tds_router)
app.include_router(github_router)
app.include_router(image_router)
app.include_router(priority_router)
app.include_router(smart_image_router)
app.include_router(diagnostics_router)
app.include_router(ad_campaigns_router)
app.include_router(ads_tracker_router)


# Корневой эндпоинт
@app.get("/")
async def root():
    """Информация о приложении."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": "/api"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения."""
    return {
        "status": "healthy",
        "ai_configured": bool(settings.OPENAI_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

# System stats endpoint
@app.get("/api/system/stats")
async def get_system_stats():
    """Get system statistics"""
    return {
        "total_sites": 0,
        "total_platforms": 0,
        "total_content": 0,
        "published_content": 0,
        "pending_tasks": 0,
        "running_tasks": 0,
        "success_rate": 0.0
    }
