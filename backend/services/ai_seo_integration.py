"""
SEO Monster - AI SEO Integration Module
Интеграция AI-агентов в процесс SEO-продвижения
Агенты работают параллельно, самообучаются и автоматически обновляются
"""

import os
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import random
from concurrent.futures import ThreadPoolExecutor
import hashlib

from .ai_providers import AIProviderManager, ai_manager
from .ai_communication import (
    AIAgentNetwork, AICollaborationManager, ExternalAIConnector,
    AIAgent, AIAgentRole, AIMessage,
    ai_network, ai_collaboration, external_connector
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOTaskType(Enum):
    """Типы SEO-задач"""
    KEYWORD_RESEARCH = "keyword_research"
    CONTENT_GENERATION = "content_generation"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TECHNICAL_AUDIT = "technical_audit"
    LINK_BUILDING = "link_building"
    INDEXING = "indexing"
    CONTENT_OPTIMIZATION = "content_optimization"
    META_TAGS = "meta_tags"
    SCHEMA_MARKUP = "schema_markup"
    SITE_ANALYSIS = "site_analysis"
    TRANSLATION = "translation"
    FACT_CHECKING = "fact_checking"
    REPORTING = "reporting"


@dataclass
class SEOTask:
    """SEO-задача для выполнения"""
    id: str
    type: SEOTaskType
    priority: int  # 1-10, где 10 - наивысший
    data: Dict[str, Any]
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_agents: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class AgentPerformance:
    """Статистика производительности агента"""
    agent_name: str
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    avg_response_time: float = 0.0
    last_active: Optional[datetime] = None
    specializations: Dict[str, float] = field(default_factory=dict)  # task_type -> success_rate


class AIAgentOrchestrator:
    """
    Оркестратор AI-агентов для SEO-задач
    Управляет распределением задач, параллельным выполнением и самообучением
    """
    
    def __init__(self):
        self.network = ai_network
        self.collaboration = ai_collaboration
        self.provider_manager = ai_manager
        self.external = external_connector
        
        self.task_queue: List[SEOTask] = []
        self.active_tasks: Dict[str, SEOTask] = {}
        self.completed_tasks: List[SEOTask] = []
        self.agent_performance: Dict[str, AgentPerformance] = {}
        
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.is_running = False
        self.auto_update_interval = 3600  # 1 час
        self.last_auto_update = datetime.now()
        
        # Маппинг задач на роли агентов
        self.task_role_mapping = {
            SEOTaskType.KEYWORD_RESEARCH: [AIAgentRole.KEYWORD_RESEARCHER, AIAgentRole.DATA_ANALYST],
            SEOTaskType.CONTENT_GENERATION: [AIAgentRole.CONTENT_WRITER, AIAgentRole.EDITOR],
            SEOTaskType.COMPETITOR_ANALYSIS: [AIAgentRole.COMPETITOR_ANALYST, AIAgentRole.DATA_ANALYST],
            SEOTaskType.TECHNICAL_AUDIT: [AIAgentRole.SEO_ANALYST],
            SEOTaskType.LINK_BUILDING: [AIAgentRole.SEO_ANALYST, AIAgentRole.COMPETITOR_ANALYST],
            SEOTaskType.INDEXING: [AIAgentRole.SEO_ANALYST],
            SEOTaskType.CONTENT_OPTIMIZATION: [AIAgentRole.EDITOR, AIAgentRole.CONTENT_WRITER],
            SEOTaskType.META_TAGS: [AIAgentRole.CONTENT_WRITER, AIAgentRole.SEO_ANALYST],
            SEOTaskType.SCHEMA_MARKUP: [AIAgentRole.SEO_ANALYST, AIAgentRole.CODE_ASSISTANT],
            SEOTaskType.SITE_ANALYSIS: [AIAgentRole.SEO_ANALYST, AIAgentRole.DATA_ANALYST],
            SEOTaskType.TRANSLATION: [AIAgentRole.TRANSLATOR],
            SEOTaskType.FACT_CHECKING: [AIAgentRole.FACT_CHECKER],
            SEOTaskType.REPORTING: [AIAgentRole.DATA_ANALYST],
        }
        
        self._initialize_performance_tracking()
    
    def _initialize_performance_tracking(self):
        """Инициализация отслеживания производительности агентов"""
        for agent in self.network.agents.values():
            self.agent_performance[agent.name] = AgentPerformance(
                agent_name=agent.name,
                specializations={task_type.value: 0.5 for task_type in SEOTaskType}
            )
    
    async def add_task(self, task_type: SEOTaskType, data: Dict[str, Any], 
                       priority: int = 5) -> str:
        """Добавление новой SEO-задачи в очередь"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        task = SEOTask(
            id=task_id,
            type=task_type,
            priority=priority,
            data=data
        )
        
        # Автоматический подбор агентов для задачи
        task.assigned_agents = await self._select_best_agents(task)
        
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        
        logger.info(f"Added SEO task: {task_id} ({task_type.value}) with agents: {task.assigned_agents}")
        return task_id
    
    async def _select_best_agents(self, task: SEOTask) -> List[str]:
        """Выбор лучших агентов для задачи на основе их производительности"""
        required_roles = self.task_role_mapping.get(task.type, [])
        selected_agents = []
        
        for role in required_roles:
            agents = self.network.get_agents_by_role(role)
            if agents:
                # Выбираем агента с лучшей специализацией для данного типа задачи
                best_agent = max(
                    agents,
                    key=lambda a: self.agent_performance[a.name].specializations.get(
                        task.type.value, 0.5
                    ) * a.success_rate
                )
                if best_agent.name not in selected_agents:
                    selected_agents.append(best_agent.name)
        
        return selected_agents
    
    async def execute_task(self, task: SEOTask) -> Dict[str, Any]:
        """Выполнение SEO-задачи с участием агентов"""
        task.status = "in_progress"
        self.active_tasks[task.id] = task
        
        start_time = datetime.now()
        results = {}
        
        try:
            # Параллельное выполнение агентами
            agent_tasks = []
            for agent_name in task.assigned_agents:
                agent = self.network.get_agent(agent_name)
                if agent:
                    agent_tasks.append(
                        self._execute_agent_subtask(agent, task)
                    )
            
            # Ждём результаты от всех агентов
            if agent_tasks:
                agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
                
                for i, result in enumerate(agent_results):
                    agent_name = task.assigned_agents[i]
                    if isinstance(result, Exception):
                        results[agent_name] = {"error": str(result)}
                        self._update_agent_performance(agent_name, task.type, False, 0)
                    else:
                        results[agent_name] = result
                        response_time = (datetime.now() - start_time).total_seconds()
                        self._update_agent_performance(agent_name, task.type, True, response_time)
            
            # Объединяем результаты
            task.results = self._merge_agent_results(results, task.type)
            task.status = "completed"
            task.completed_at = datetime.now()
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"Task {task.id} failed: {e}")
        
        finally:
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            self.completed_tasks.append(task)
        
        return task.results
    
    async def _execute_agent_subtask(self, agent: AIAgent, task: SEOTask) -> Dict[str, Any]:
        """Выполнение подзадачи конкретным агентом"""
        # Формируем промпт для агента на основе его роли и задачи
        prompt = self._build_agent_prompt(agent, task)
        
        # Вызываем AI провайдер
        try:
            response = await self.provider_manager.generate(
                prompt=prompt,
                system_prompt=agent.system_prompt,
                provider=agent.provider,
                model=agent.model,
                max_tokens=4000
            )
            
            # Обновляем статистику агента
            agent.total_requests += 1
            agent.last_used = datetime.now()
            
            return {
                "agent": agent.name,
                "role": agent.role.value,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Agent {agent.name} failed: {e}")
            raise
    
    def _build_agent_prompt(self, agent: AIAgent, task: SEOTask) -> str:
        """Построение промпта для агента"""
        task_prompts = {
            SEOTaskType.KEYWORD_RESEARCH: f"""
Analyze and research keywords for the following context:
Domain: {task.data.get('domain', 'N/A')}
Niche: {task.data.get('niche', 'N/A')}
Current keywords: {task.data.get('keywords', [])}

Provide:
1. 20 new keyword opportunities (mix of short-tail and long-tail)
2. Search intent classification for each
3. Estimated difficulty and potential
4. Semantic clusters
""",
            SEOTaskType.CONTENT_GENERATION: f"""
Create SEO-optimized content for:
Topic: {task.data.get('topic', 'N/A')}
Target keywords: {task.data.get('keywords', [])}
Word count: {task.data.get('word_count', 1500)}
Content type: {task.data.get('content_type', 'article')}

Requirements:
- Natural keyword integration
- Compelling headline and subheadings
- Meta description
- Internal linking suggestions
""",
            SEOTaskType.COMPETITOR_ANALYSIS: f"""
Analyze competitors for:
Domain: {task.data.get('domain', 'N/A')}
Competitors: {task.data.get('competitors', [])}
Focus areas: {task.data.get('focus', ['content', 'keywords', 'backlinks'])}

Provide:
1. Content gap analysis
2. Keyword opportunities
3. Backlink strategies
4. Recommendations
""",
            SEOTaskType.TECHNICAL_AUDIT: f"""
Perform technical SEO audit for:
URL: {task.data.get('url', 'N/A')}
Current issues: {task.data.get('issues', [])}

Check and report on:
1. Page speed factors
2. Mobile optimization
3. Crawlability issues
4. Schema markup opportunities
5. Core Web Vitals recommendations
""",
            SEOTaskType.META_TAGS: f"""
Generate optimized meta tags for:
Page: {task.data.get('page', 'N/A')}
Keywords: {task.data.get('keywords', [])}
Content summary: {task.data.get('summary', 'N/A')}

Create:
1. Title tag (50-60 chars)
2. Meta description (150-160 chars)
3. Open Graph tags
4. Twitter Card tags
""",
            SEOTaskType.TRANSLATION: f"""
Translate and localize for SEO:
Source language: {task.data.get('source_lang', 'en')}
Target language: {task.data.get('target_lang', 'ru')}
Content: {task.data.get('content', '')}

Requirements:
- Preserve SEO value
- Localize keywords
- Maintain brand voice
""",
        }
        
        base_prompt = task_prompts.get(task.type, f"Execute SEO task: {task.type.value}\nData: {json.dumps(task.data)}")
        
        return f"""You are {agent.name}, a specialized {agent.role.value}.
Your capabilities: {', '.join(agent.capabilities)}

Task ID: {task.id}
Task Type: {task.type.value}
Priority: {task.priority}/10

{base_prompt}

Provide detailed, actionable results in JSON format."""
    
    def _merge_agent_results(self, results: Dict[str, Any], task_type: SEOTaskType) -> Dict[str, Any]:
        """Объединение результатов от нескольких агентов"""
        merged = {
            "task_type": task_type.value,
            "agents_involved": list(results.keys()),
            "timestamp": datetime.now().isoformat(),
            "individual_results": results,
            "combined_output": {}
        }
        
        # Извлекаем и объединяем ключевые данные
        all_responses = []
        for agent_name, result in results.items():
            if "response" in result and not "error" in result:
                all_responses.append(result["response"])
        
        merged["combined_output"]["responses"] = all_responses
        merged["combined_output"]["success_count"] = len(all_responses)
        merged["combined_output"]["error_count"] = len(results) - len(all_responses)
        
        return merged
    
    def _update_agent_performance(self, agent_name: str, task_type: SEOTaskType, 
                                   success: bool, response_time: float):
        """Обновление статистики производительности агента"""
        if agent_name not in self.agent_performance:
            self.agent_performance[agent_name] = AgentPerformance(agent_name=agent_name)
        
        perf = self.agent_performance[agent_name]
        perf.total_tasks += 1
        perf.last_active = datetime.now()
        
        if success:
            perf.successful_tasks += 1
            # Обновляем среднее время ответа
            perf.avg_response_time = (
                (perf.avg_response_time * (perf.successful_tasks - 1) + response_time) 
                / perf.successful_tasks
            )
            # Улучшаем специализацию для данного типа задачи
            current = perf.specializations.get(task_type.value, 0.5)
            perf.specializations[task_type.value] = min(1.0, current + 0.05)
        else:
            perf.failed_tasks += 1
            # Снижаем специализацию при неудаче
            current = perf.specializations.get(task_type.value, 0.5)
            perf.specializations[task_type.value] = max(0.1, current - 0.1)
        
        # Обновляем success_rate агента в сети
        agent = self.network.get_agent(agent_name)
        if agent:
            agent.success_rate = perf.successful_tasks / perf.total_tasks if perf.total_tasks > 0 else 1.0
    
    async def run_autopilot_cycle(self, domain: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Запуск полного цикла SEO-продвижения с участием всех агентов
        """
        config = config or {}
        cycle_results = {
            "domain": domain,
            "started_at": datetime.now().isoformat(),
            "tasks_completed": [],
            "agents_used": set(),
            "total_time": 0
        }
        
        start_time = datetime.now()
        
        # 1. Анализ сайта
        site_task_id = await self.add_task(
            SEOTaskType.SITE_ANALYSIS,
            {"domain": domain, "full_audit": True},
            priority=10
        )
        
        # 2. Исследование ключевых слов
        keyword_task_id = await self.add_task(
            SEOTaskType.KEYWORD_RESEARCH,
            {"domain": domain, "niche": config.get("niche", "general")},
            priority=9
        )
        
        # 3. Анализ конкурентов
        competitor_task_id = await self.add_task(
            SEOTaskType.COMPETITOR_ANALYSIS,
            {"domain": domain, "competitors": config.get("competitors", [])},
            priority=8
        )
        
        # 4. Технический аудит
        audit_task_id = await self.add_task(
            SEOTaskType.TECHNICAL_AUDIT,
            {"url": f"https://{domain}"},
            priority=8
        )
        
        # Выполняем первую волну задач параллельно
        first_wave_tasks = [
            self._get_and_execute_task(site_task_id),
            self._get_and_execute_task(keyword_task_id),
            self._get_and_execute_task(competitor_task_id),
            self._get_and_execute_task(audit_task_id)
        ]
        
        first_wave_results = await asyncio.gather(*first_wave_tasks, return_exceptions=True)
        
        for result in first_wave_results:
            if not isinstance(result, Exception) and result:
                cycle_results["tasks_completed"].append(result.get("task_type"))
                cycle_results["agents_used"].update(result.get("agents_involved", []))
        
        # 5. Генерация контента (на основе найденных ключевых слов)
        content_tasks = []
        for i in range(config.get("articles_count", 5)):
            task_id = await self.add_task(
                SEOTaskType.CONTENT_GENERATION,
                {
                    "topic": f"Article {i+1} for {domain}",
                    "keywords": [],  # Будут заполнены из результатов keyword research
                    "word_count": config.get("word_count", 1500)
                },
                priority=7
            )
            content_tasks.append(self._get_and_execute_task(task_id))
        
        content_results = await asyncio.gather(*content_tasks, return_exceptions=True)
        
        for result in content_results:
            if not isinstance(result, Exception) and result:
                cycle_results["tasks_completed"].append(result.get("task_type"))
                cycle_results["agents_used"].update(result.get("agents_involved", []))
        
        # 6. Генерация мета-тегов
        meta_task_id = await self.add_task(
            SEOTaskType.META_TAGS,
            {"domain": domain, "pages": config.get("pages", [])},
            priority=6
        )
        meta_result = await self._get_and_execute_task(meta_task_id)
        if meta_result:
            cycle_results["tasks_completed"].append(meta_result.get("task_type"))
        
        # 7. Индексация
        index_task_id = await self.add_task(
            SEOTaskType.INDEXING,
            {"domain": domain, "urls": config.get("urls", [])},
            priority=5
        )
        index_result = await self._get_and_execute_task(index_task_id)
        if index_result:
            cycle_results["tasks_completed"].append(index_result.get("task_type"))
        
        # Финализация
        cycle_results["completed_at"] = datetime.now().isoformat()
        cycle_results["total_time"] = (datetime.now() - start_time).total_seconds()
        cycle_results["agents_used"] = list(cycle_results["agents_used"])
        
        # Запускаем самообучение
        await self.self_learn_from_cycle(cycle_results)
        
        # Проверяем необходимость автообновления агентов
        await self.check_and_update_agents()
        
        return cycle_results
    
    async def _get_and_execute_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получение и выполнение задачи по ID"""
        task = next((t for t in self.task_queue if t.id == task_id), None)
        if task:
            self.task_queue.remove(task)
            return await self.execute_task(task)
        return None
    
    async def self_learn_from_cycle(self, cycle_results: Dict[str, Any]):
        """Самообучение на основе результатов цикла"""
        logger.info("Starting self-learning from cycle results...")
        
        # Анализируем производительность агентов
        for agent_name, perf in self.agent_performance.items():
            if perf.total_tasks > 0:
                success_rate = perf.successful_tasks / perf.total_tasks
                
                # Если агент показывает плохие результаты, пробуем другой провайдер
                if success_rate < 0.7:
                    agent = self.network.get_agent(agent_name)
                    if agent:
                        await self._try_alternative_provider(agent)
        
        # Сохраняем результаты обучения
        learning_data = {
            "timestamp": datetime.now().isoformat(),
            "cycle_domain": cycle_results.get("domain"),
            "tasks_completed": len(cycle_results.get("tasks_completed", [])),
            "agents_performance": {
                name: {
                    "success_rate": perf.successful_tasks / perf.total_tasks if perf.total_tasks > 0 else 0,
                    "avg_response_time": perf.avg_response_time,
                    "specializations": perf.specializations
                }
                for name, perf in self.agent_performance.items()
            }
        }
        
        # Сохраняем в файл
        learning_file = "/home/ubuntu/seo_monster/backend/data/autopilot/agent_learning.json"
        os.makedirs(os.path.dirname(learning_file), exist_ok=True)
        
        existing_data = []
        if os.path.exists(learning_file):
            try:
                with open(learning_file, 'r') as f:
                    existing_data = json.load(f)
            except:
                pass
        
        existing_data.append(learning_data)
        
        # Храним только последние 100 записей
        if len(existing_data) > 100:
            existing_data = existing_data[-100:]
        
        with open(learning_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        logger.info("Self-learning completed and saved")
    
    async def _try_alternative_provider(self, agent: AIAgent):
        """Попытка использовать альтернативный провайдер для агента"""
        available_providers = self.provider_manager.get_available_providers()
        
        for provider in available_providers:
            if provider["name"] != agent.provider and provider["enabled"]:
                old_provider = agent.provider
                agent.provider = provider["name"]
                agent.model = provider["model"]
                logger.info(f"Switched agent {agent.name} from {old_provider} to {provider['name']}")
                break
    
    async def check_and_update_agents(self):
        """Проверка и автоматическое обновление агентов"""
        now = datetime.now()
        
        if (now - self.last_auto_update).total_seconds() < self.auto_update_interval:
            return
        
        logger.info("Running automatic agent update check...")
        
        # Проверяем доступность провайдеров
        for agent in self.network.agents.values():
            provider_status = await self.provider_manager.check_provider_health(agent.provider)
            
            if not provider_status.get("healthy", False):
                await self._try_alternative_provider(agent)
        
        # Добавляем новых агентов если нужно
        await self._discover_new_agents()
        
        # Обновляем промпты агентов на основе обучения
        await self._update_agent_prompts()
        
        self.last_auto_update = now
        logger.info("Agent update check completed")
    
    async def _discover_new_agents(self):
        """Поиск и добавление новых AI-агентов"""
        # Проверяем внешние сервисы
        external_services = self.external.get_free_services()
        
        for service in external_services:
            if not service.get("connected", False):
                # Пробуем подключиться к новым сервисам
                try:
                    await self.external.connect_service(service["id"])
                    logger.info(f"Connected to new external service: {service['name']}")
                except:
                    pass
        
        # Проверяем новые модели у провайдеров
        for provider in self.provider_manager.get_available_providers():
            if provider.get("new_models"):
                for model in provider["new_models"]:
                    # Создаём нового агента для новой модели
                    new_agent = AIAgent(
                        name=f"agent_{provider['name']}_{model.replace('/', '_')}",
                        role=AIAgentRole.CONTENT_WRITER,  # По умолчанию
                        provider=provider["name"],
                        model=model,
                        system_prompt="You are a versatile AI assistant for SEO tasks.",
                        capabilities=["general", "content", "analysis"]
                    )
                    self.network.register_agent(new_agent)
    
    async def _update_agent_prompts(self):
        """Обновление промптов агентов на основе результатов обучения"""
        learning_file = "/home/ubuntu/seo_monster/backend/data/autopilot/agent_learning.json"
        
        if not os.path.exists(learning_file):
            return
        
        try:
            with open(learning_file, 'r') as f:
                learning_data = json.load(f)
            
            if not learning_data:
                return
            
            # Анализируем последние результаты
            recent_data = learning_data[-10:]  # Последние 10 циклов
            
            for agent in self.network.agents.values():
                # Находим лучшие специализации агента
                best_tasks = []
                for data in recent_data:
                    agent_perf = data.get("agents_performance", {}).get(agent.name, {})
                    specs = agent_perf.get("specializations", {})
                    for task_type, score in specs.items():
                        if score > 0.8:
                            best_tasks.append(task_type)
                
                # Обновляем capabilities агента
                if best_tasks:
                    agent.capabilities = list(set(agent.capabilities + best_tasks))
                    
        except Exception as e:
            logger.error(f"Error updating agent prompts: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получение текущего статуса оркестратора"""
        return {
            "is_running": self.is_running,
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "total_agents": len(self.network.agents),
            "active_agents": len([a for a in self.network.agents.values() if a.is_active]),
            "agent_performance": {
                name: {
                    "success_rate": perf.successful_tasks / perf.total_tasks if perf.total_tasks > 0 else 0,
                    "total_tasks": perf.total_tasks,
                    "avg_response_time": round(perf.avg_response_time, 2)
                }
                for name, perf in self.agent_performance.items()
            },
            "last_auto_update": self.last_auto_update.isoformat()
        }


# Глобальный экземпляр оркестратора
seo_orchestrator = AIAgentOrchestrator()


# Удобные функции для использования
async def run_seo_cycle(domain: str, config: Dict = None) -> Dict[str, Any]:
    """Запуск полного цикла SEO-продвижения"""
    return await seo_orchestrator.run_autopilot_cycle(domain, config)


async def add_seo_task(task_type: str, data: Dict, priority: int = 5) -> str:
    """Добавление SEO-задачи"""
    return await seo_orchestrator.add_task(SEOTaskType(task_type), data, priority)


def get_orchestrator_status() -> Dict[str, Any]:
    """Получение статуса оркестратора"""
    return seo_orchestrator.get_status()
