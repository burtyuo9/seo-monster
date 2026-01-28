"""
SEO Monster - Autonomous AI Agent for SEO Promotion.
Main application file.
"""

import os
import sys

# Add application path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

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
from app.api.ses_routes import router as ses_router
from app.api.localization_routes import router as localization_router
from app.api.features_routes import router as features_router
from app.api.autonomous_routes import router as autonomous_router
from app.api.publishing_routes import router as publishing_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    print(f"[START] Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    print("[OK] Database initialized")
    
    yield
    
    # Shutdown
    await close_db()
    print("[STOP] Application stopped")


# Create application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## SEO Monster - Autonomous AI Agent for SEO Promotion

### Features:
- Site Analysis - automatic keyword extraction and niche detection
- Content Generation - creating unique articles in different languages
- Auto-posting - publishing content on platforms
- Analytics - tracking results and self-learning
- Backups - saving system state

### Supported Languages:
Russian | English | German | French | Spanish | Italian | Portuguese | Chinese | Japanese | Korean | Arabic | Turkish
    """,
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect API routers
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
app.include_router(ses_router)
app.include_router(localization_router)
app.include_router(features_router)
app.include_router(autonomous_router)
app.include_router(publishing_router)


# Root endpoint - redirect to Frontend
@app.get("/")
async def root():
    """Redirect to Frontend UI."""
    return RedirectResponse(url="http://localhost:5200", status_code=302)


@app.get("/api/info")
async def api_info():
    """Application information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": "/api",
        "frontend": "http://localhost:5200"
    }


@app.get("/health")
async def health_check():
    """Application health check."""
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
