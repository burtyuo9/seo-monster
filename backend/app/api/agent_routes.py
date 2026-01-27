"""
SEO Monster - Agent API Routes
"""

from fastapi import APIRouter

# Agent router
agent_router = APIRouter(prefix="/agent", tags=["agent"])

@agent_router.get("/status")
async def get_agent_status():
    return {"status": "active", "tasks_completed": 0}


# Finder router
finder_router = APIRouter(prefix="/finder", tags=["finder"])

@finder_router.post("/search")
async def search_platforms(query: str = None):
    return {"results": []}


# Browser router
browser_router = APIRouter(prefix="/browser", tags=["browser"])

@browser_router.get("/sessions")
async def get_browser_sessions():
    return {"sessions": []}
