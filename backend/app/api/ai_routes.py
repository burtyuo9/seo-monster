"""
SEO Monster - AI System API Routes
API для управления AI-агентом, обучением и эволюцией
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio

import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.ai_agent_core import get_ai_agent
from services.ai_learning_engine import get_learning_engine
from services.ai_code_generator import get_code_generator
from services.ai_evolution_system import get_evolution_system

router = APIRouter(prefix="/api/ai", tags=["AI System"])


# ═══════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = None

class CreateModuleRequest(BaseModel):
    name: str
    description: str
    features: Optional[List[str]] = None

class UpdateCodeRequest(BaseModel):
    file_path: str
    instruction: str

class FixErrorRequest(BaseModel):
    file_path: str
    error_message: str
    traceback: Optional[str] = None

class RefactorRequest(BaseModel):
    file_path: str
    refactor_type: str = "optimize"  # optimize, clean, document, modernize

class AddGoalRequest(BaseModel):
    description: str
    priority: int = 5
    deadline: Optional[str] = None

class DevelopCapabilityRequest(BaseModel):
    description: str

class AnalyzeCampaignRequest(BaseModel):
    campaign_data: Dict

class ContentAnalysisRequest(BaseModel):
    content_list: List[Dict]


# ═══════════════════════════════════════════════════════════════
# AI AGENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/chat")
async def chat_with_ai(request: ChatMessage):
    """
    Общение с AI-агентом
    Агент понимает естественный язык и выполняет команды
    """
    agent = get_ai_agent()
    result = await agent.process_message(request.message, request.context)
    return result


@router.get("/status")
async def get_ai_status():
    """Получение статуса AI-агента"""
    agent = get_ai_agent()
    return {
        "status": "active",
        "model": agent.model,
        "capabilities": agent.capabilities,
        "memory_items": len(agent.memory)
    }


@router.get("/memory")
async def get_ai_memory():
    """Получение памяти AI-агента"""
    agent = get_ai_agent()
    return {"memory": agent.memory[-50:]}


@router.delete("/memory")
async def clear_ai_memory():
    """Очистка памяти AI-агента"""
    agent = get_ai_agent()
    agent.memory = []
    return {"status": "memory_cleared"}


# ═══════════════════════════════════════════════════════════════
# CODE GENERATOR ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/code/generate-module")
async def generate_module(request: CreateModuleRequest):
    """
    Генерация нового модуля
    AI создаёт сервис и API роуты по описанию
    """
    generator = get_code_generator()
    result = generator.generate_module(
        name=request.name,
        description=request.description,
        features=request.features
    )
    return result


@router.post("/code/update")
async def update_code(request: UpdateCodeRequest):
    """
    Обновление существующего кода
    AI модифицирует код по инструкции
    """
    generator = get_code_generator()
    result = generator.update_code(
        file_path=request.file_path,
        instruction=request.instruction
    )
    return result


@router.post("/code/fix-error")
async def fix_error(request: FixErrorRequest):
    """
    Автоматическое исправление ошибки
    AI анализирует и исправляет ошибку в коде
    """
    generator = get_code_generator()
    result = generator.fix_error(
        file_path=request.file_path,
        error_message=request.error_message,
        error_traceback=request.traceback
    )
    return result


@router.post("/code/refactor")
async def refactor_code(request: RefactorRequest):
    """
    Рефакторинг кода
    Типы: optimize, clean, document, modernize
    """
    generator = get_code_generator()
    result = generator.refactor_code(
        file_path=request.file_path,
        refactor_type=request.refactor_type
    )
    return result


@router.get("/code/stats")
async def get_code_generation_stats():
    """Статистика генерации кода"""
    generator = get_code_generator()
    return generator.get_generation_stats()


# ═══════════════════════════════════════════════════════════════
# LEARNING ENGINE ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/learning/analyze-campaign")
async def analyze_campaign(request: AnalyzeCampaignRequest):
    """
    Анализ результатов SEO-кампании
    AI учится на результатах
    """
    engine = get_learning_engine()
    result = engine.analyze_campaign_results(request.campaign_data)
    return result


@router.post("/learning/analyze-content")
async def analyze_content(request: ContentAnalysisRequest):
    """
    Анализ эффективности контента
    Выявляет успешные паттерны
    """
    engine = get_learning_engine()
    result = engine.analyze_content_performance(request.content_list)
    return result


@router.get("/learning/content-recommendations")
async def get_content_recommendations(topic: str, platform: Optional[str] = None):
    """
    Получение рекомендаций для создания контента
    На основе обученных паттернов
    """
    engine = get_learning_engine()
    return engine.get_content_recommendations(topic, platform)


@router.get("/learning/predict-ranking")
async def predict_ranking(keyword: str, domain: str, current_position: Optional[int] = None):
    """
    Предсказание потенциала ранжирования
    """
    engine = get_learning_engine()
    return engine.predict_ranking_potential(keyword, domain, current_position)


@router.get("/learning/stats")
async def get_learning_stats():
    """Статистика обучения"""
    engine = get_learning_engine()
    return engine.get_learning_stats()


# ═══════════════════════════════════════════════════════════════
# EVOLUTION SYSTEM ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/evolution/health")
async def check_system_health():
    """
    Проверка здоровья системы
    AI анализирует все компоненты
    """
    evolution = get_evolution_system()
    return await evolution.check_system_health()


@router.post("/evolution/improve")
async def auto_improve(background_tasks: BackgroundTasks):
    """
    Автоматическое улучшение системы
    AI анализирует и применяет улучшения
    """
    evolution = get_evolution_system()
    
    # Запускаем в фоне для длительных операций
    async def run_improvement():
        return await evolution.auto_improve()
    
    result = await evolution.auto_improve()
    return result


@router.post("/evolution/goals")
async def add_goal(request: AddGoalRequest):
    """
    Добавление новой цели для AI
    """
    evolution = get_evolution_system()
    return evolution.add_goal(
        description=request.description,
        priority=request.priority,
        deadline=request.deadline
    )


@router.get("/evolution/goals")
async def get_goals():
    """Получение списка целей"""
    evolution = get_evolution_system()
    return evolution.goals


@router.post("/evolution/work-on-goals")
async def work_on_goals():
    """
    Работа над активными целями
    AI продвигается к достижению целей
    """
    evolution = get_evolution_system()
    return await evolution.work_on_goals()


@router.post("/evolution/develop-capability")
async def develop_capability(request: DevelopCapabilityRequest):
    """
    Разработка новой возможности
    AI создаёт новую функциональность
    """
    evolution = get_evolution_system()
    return await evolution.develop_new_capability(request.description)


@router.get("/evolution/capabilities")
async def get_capabilities():
    """Получение списка возможностей AI"""
    evolution = get_evolution_system()
    return {"capabilities": evolution.get_capabilities()}


@router.get("/evolution/stats")
async def get_evolution_stats():
    """Статистика эволюции AI"""
    evolution = get_evolution_system()
    return evolution.get_evolution_stats()


# ═══════════════════════════════════════════════════════════════
# COMBINED STATS
# ═══════════════════════════════════════════════════════════════

@router.get("/stats")
async def get_all_ai_stats():
    """
    Полная статистика AI системы
    Объединяет данные из всех модулей
    """
    agent = get_ai_agent()
    learning = get_learning_engine()
    generator = get_code_generator()
    evolution = get_evolution_system()
    
    return {
        "agent": {
            "status": "active",
            "memory_items": len(agent.memory.get("conversations", [])),
            "capabilities": agent.capabilities
        },
        "learning": learning.get_learning_stats(),
        "code_generator": generator.get_generation_stats(),
        "evolution": evolution.get_evolution_stats()
    }
