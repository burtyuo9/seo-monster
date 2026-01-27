"""
SEO Monster - Core Engine
Главное ядро системы с полной интеграцией AI-агентов
Работает полностью автономно с бесплатными LLM
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

# Импортируем все модули AI
from .ai_providers import ai_manager, AIProviderManager
from .ai_communication import ai_network, ai_collaboration, AIAgent, AIAgentRole
from .ai_seo_integration import seo_orchestrator, SEOTaskType
from .parallel_seo_executor import parallel_executor, run_parallel_seo, run_seo_campaign
from .agent_self_learning import (
    agent_learning, agent_updater, agent_populator,
    record_learning, check_and_update_agents, ensure_agents
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonsterMode(Enum):
    """Режимы работы Monster"""
    IDLE = "idle"              # Ожидание
    ANALYZING = "analyzing"    # Анализ
    GENERATING = "generating"  # Генерация контента
    OPTIMIZING = "optimizing"  # Оптимизация
    INDEXING = "indexing"      # Индексация
    LEARNING = "learning"      # Самообучение
    FULL_AUTO = "full_auto"    # Полный автопилот


@dataclass
class MonsterState:
    """Состояние Monster"""
    mode: MonsterMode = MonsterMode.IDLE
    current_domain: Optional[str] = None
    session_started: Optional[str] = None
    tasks_completed: int = 0
    articles_generated: int = 0
    words_written: int = 0
    agents_active: int = 0
    providers_healthy: int = 0
    last_learning_cycle: Optional[str] = None
    errors: List[str] = field(default_factory=list)


class SEOMonsterCore:
    """
    SEO Monster - Главное ядро системы
    
    Возможности:
    - Полностью автономная работа без OpenAI
    - Параллельное выполнение задач несколькими AI-агентами
    - Самообучение и автоматическое улучшение
    - Автоматическое обновление и пополнение агентов
    - Интеграция с 10+ бесплатными LLM провайдерами
    """
    
    def __init__(self):
        self.state = MonsterState()
        self.config: Dict[str, Any] = {}
        self.data_dir = "/home/ubuntu/seo_monster/backend/data"
        
        # Инициализируем подсистемы
        self._init_subsystems()
        
        # Загружаем конфигурацию
        self._load_config()
        
        logger.info("🦖 SEO Monster Core initialized!")
    
    def _init_subsystems(self):
        """Инициализация всех подсистем"""
        # AI Manager уже инициализирован как singleton
        self.ai_manager = ai_manager
        
        # AI Network уже инициализирован
        self.ai_network = ai_network
        
        # SEO Orchestrator
        self.seo_orchestrator = seo_orchestrator
        
        # Parallel Executor
        self.parallel_executor = parallel_executor
        
        # Learning System
        self.learning = agent_learning
        
        # Auto Updater
        self.updater = agent_updater
        
        # Agent Populator
        self.populator = agent_populator
    
    def _load_config(self):
        """Загрузка конфигурации"""
        config_file = f"{self.data_dir}/monster_config.json"
        
        default_config = {
            "ai_agents_enabled": True,  # Master switch for AI Agents module
            "auto_learning": True,
            "auto_update_agents": True,
            "parallel_execution": True,
            "max_parallel_tasks": 10,
            "preferred_providers": ["groq", "together", "ollama"],
            "fallback_providers": ["huggingface", "cohere", "deepseek"],
            "content_settings": {
                "min_words": 1000,
                "max_words": 3000,
                "include_images": True,
                "include_schema": True
            },
            "indexing_settings": {
                "use_indexnow": True,
                "use_ping": True,
                "auto_sitemap": True
            },
            "geo_settings": {
                "excluded_countries": ["RU", "BY", "KZ", "UA", "UZ", "TJ", "KG", "AM", "AZ", "MD", "TM"],
                "target_regions": ["US", "UK", "EU", "APAC"]
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            except:
                self.config = default_config
        else:
            self.config = default_config
            self._save_config()
    
    def _save_config(self):
        """Сохранение конфигурации"""
        config_file = f"{self.data_dir}/monster_config.json"
        os.makedirs(self.data_dir, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    async def start_session(self, domain: str) -> Dict[str, Any]:
        """Запуск сессии работы с доменом"""
        logger.info(f"🦖 Starting Monster session for {domain}")
        
        self.state.mode = MonsterMode.ANALYZING
        self.state.current_domain = domain
        self.state.session_started = datetime.now().isoformat()
        self.state.tasks_completed = 0
        self.state.articles_generated = 0
        self.state.words_written = 0
        self.state.errors = []
        
        # Проверяем и обновляем агентов перед началом (только если AI Agents включены)
        if self.config.get("ai_agents_enabled") and self.config.get("auto_update_agents"):
            await self._prepare_agents()
        elif not self.config.get("ai_agents_enabled"):
            logger.info("AI Agents module is DISABLED - running in basic mode")
            self.state.agents_active = 0
            self.state.providers_healthy = 0
        
        return {
            "status": "session_started",
            "domain": domain,
            "started_at": self.state.session_started,
            "agents_ready": self.state.agents_active,
            "providers_healthy": self.state.providers_healthy
        }
    
    async def _prepare_agents(self):
        """Подготовка агентов к работе"""
        logger.info("Preparing AI agents...")
        
        # Проверяем здоровье провайдеров
        health_status = await self.ai_manager.check_all_providers_health()
        self.state.providers_healthy = sum(
            1 for p in health_status.values() if p.get("healthy")
        )
        
        # Обеспечиваем минимальное количество агентов
        await ensure_agents()
        
        # Подсчитываем активных агентов
        self.state.agents_active = len(self.ai_network.agents)
        
        logger.info(f"Agents ready: {self.state.agents_active}, Providers healthy: {self.state.providers_healthy}")
    
    async def run_full_autopilot(
        self, 
        domain: str, 
        duration_minutes: int = 30,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Запуск полного автопилота
        Monster работает автономно указанное время
        """
        config = config or {}
        
        # Запускаем сессию
        await self.start_session(domain)
        self.state.mode = MonsterMode.FULL_AUTO
        
        results = {
            "domain": domain,
            "started_at": self.state.session_started,
            "duration_minutes": duration_minutes,
            "cycles": [],
            "total_stats": {
                "articles_generated": 0,
                "words_written": 0,
                "keywords_found": 0,
                "urls_indexed": 0
            }
        }
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        cycle_number = 0
        
        logger.info(f"🦖 Monster FULL AUTOPILOT started for {duration_minutes} minutes")
        
        while datetime.now() < end_time:
            cycle_number += 1
            logger.info(f"🔄 Starting cycle {cycle_number}")
            
            try:
                # Выполняем цикл SEO-работы
                cycle_result = await self._run_seo_cycle(domain, cycle_number, config)
                results["cycles"].append(cycle_result)
                
                # Обновляем статистику
                results["total_stats"]["articles_generated"] += cycle_result.get("articles_generated", 0)
                results["total_stats"]["words_written"] += cycle_result.get("words_written", 0)
                results["total_stats"]["keywords_found"] += cycle_result.get("keywords_found", 0)
                results["total_stats"]["urls_indexed"] += cycle_result.get("urls_indexed", 0)
                
                # Самообучение после каждого цикла
                if self.config.get("auto_learning"):
                    await self._run_learning_cycle()
                
                # Небольшая пауза между циклами
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Cycle {cycle_number} error: {e}")
                self.state.errors.append(f"Cycle {cycle_number}: {str(e)}")
        
        # Финализация
        results["completed_at"] = datetime.now().isoformat()
        results["total_cycles"] = cycle_number
        results["errors"] = self.state.errors
        
        # Сохраняем результаты
        await self._save_session_results(results)
        
        self.state.mode = MonsterMode.IDLE
        
        logger.info(f"🦖 Monster AUTOPILOT completed: {cycle_number} cycles, {results['total_stats']['articles_generated']} articles")
        
        return results
    
    async def _run_seo_cycle(
        self, 
        domain: str, 
        cycle_number: int,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнение одного цикла SEO-работы"""
        cycle_result = {
            "cycle": cycle_number,
            "started_at": datetime.now().isoformat(),
            "articles_generated": 0,
            "words_written": 0,
            "keywords_found": 0,
            "urls_indexed": 0,
            "tasks": []
        }
        
        # Проверяем, включены ли AI Agents
        ai_agents_enabled = self.config.get("ai_agents_enabled", True)
        
        # Фаза 1: Анализ и сбор ключевых слов
        self.state.mode = MonsterMode.ANALYZING
        
        if ai_agents_enabled:
            # Режим с AI Agents - параллельное выполнение
            analysis_tasks = [
                {"type": "keyword_research", "data": {"domain": domain, "cycle": cycle_number}},
                {"type": "competitor_analysis", "data": {"domain": domain}}
            ]
            
            if self.config.get("parallel_execution"):
                analysis_results = await run_parallel_seo(domain, analysis_tasks)
            else:
                analysis_results = await self.seo_orchestrator.execute_seo_task(
                    SEOTaskType.KEYWORD_RESEARCH, domain, {}
                )
        else:
            # Базовый режим без AI Agents - используем встроенные методы
            analysis_results = await self._basic_keyword_research(domain)
            logger.info("Running in BASIC mode without AI Agents")
        
        cycle_result["tasks"].append({"phase": "analysis", "result": analysis_results})
        
        # Фаза 2: Генерация контента
        self.state.mode = MonsterMode.GENERATING
        
        articles_count = config.get("articles_per_cycle", 5)
        
        if ai_agents_enabled:
            # Режим с AI Agents - параллельная генерация
            content_tasks = []
            for i in range(articles_count):
                content_tasks.append({
                    "type": "content_generation",
                    "data": {
                        "topic": f"Article {cycle_number}_{i+1}",
                        "domain": domain,
                        "word_count": self.config["content_settings"]["min_words"]
                    }
                })
            
            content_results = await run_parallel_seo(domain, content_tasks)
            
            # Подсчитываем результаты
            for task_result in content_results.get("tasks", []):
                if task_result.get("success"):
                    cycle_result["articles_generated"] += 1
                    response = task_result.get("result", {}).get("responses", [""])[0]
                    if response:
                        cycle_result["words_written"] += len(str(response).split())
        else:
            # Базовый режим - последовательная генерация через базовый провайдер
            content_results = await self._basic_content_generation(domain, articles_count, cycle_number)
            cycle_result["articles_generated"] = content_results.get("articles_generated", 0)
            cycle_result["words_written"] = content_results.get("words_written", 0)
        
        cycle_result["tasks"].append({"phase": "content", "result": content_results})
        
        # Фаза 3: Оптимизация и индексация
        self.state.mode = MonsterMode.INDEXING
        
        if ai_agents_enabled:
            indexing_tasks = [
                {"type": "meta_tags", "data": {"domain": domain}},
                {"type": "sitemap_update", "data": {"domain": domain}}
            ]
            indexing_results = await run_parallel_seo(domain, indexing_tasks)
        else:
            indexing_results = await self._basic_indexing(domain)
        
        cycle_result["urls_indexed"] = len(indexing_results.get("tasks", [])) if ai_agents_enabled else indexing_results.get("urls_indexed", 0)
        cycle_result["tasks"].append({"phase": "indexing", "result": indexing_results})
        
        # Обновляем состояние
        self.state.articles_generated += cycle_result["articles_generated"]
        self.state.words_written += cycle_result["words_written"]
        self.state.tasks_completed += len(cycle_result["tasks"])
        
        cycle_result["completed_at"] = datetime.now().isoformat()
        
        return cycle_result
    
    async def _run_learning_cycle(self):
        """Цикл самообучения"""
        self.state.mode = MonsterMode.LEARNING
        self.state.last_learning_cycle = datetime.now().isoformat()
        
        logger.info("🧠 Running learning cycle...")
        
        # Проверяем и обновляем агентов
        update_result = await check_and_update_agents()
        
        # Обеспечиваем наличие агентов
        populate_result = await ensure_agents()
        
        logger.info(f"Learning cycle completed: {update_result}, {populate_result}")
    
    async def _save_session_results(self, results: Dict):
        """Сохранение результатов сессии"""
        sessions_dir = f"{self.data_dir}/sessions"
        os.makedirs(sessions_dir, exist_ok=True)
        
        filename = f"{sessions_dir}/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Session results saved to {filename}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получение текущего статуса Monster"""
        return {
            "mode": self.state.mode.value,
            "current_domain": self.state.current_domain,
            "session_started": self.state.session_started,
            "stats": {
                "tasks_completed": self.state.tasks_completed,
                "articles_generated": self.state.articles_generated,
                "words_written": self.state.words_written
            },
            "ai_status": {
                "agents_active": self.state.agents_active,
                "providers_healthy": self.state.providers_healthy,
                "last_learning": self.state.last_learning_cycle
            },
            "errors": self.state.errors[-10:],  # Последние 10 ошибок
            "config": {
                "auto_learning": self.config.get("auto_learning"),
                "parallel_execution": self.config.get("parallel_execution"),
                "preferred_providers": self.config.get("preferred_providers")
            }
        }
    
    def get_available_providers(self) -> List[Dict]:
        """Получение списка доступных провайдеров"""
        return self.ai_manager.get_available_providers()
    
    def get_active_agents(self) -> List[Dict]:
        """Получение списка активных агентов"""
        return [
            {
                "name": agent.name,
                "role": agent.role.value,
                "provider": agent.provider,
                "model": agent.model,
                "capabilities": agent.capabilities
            }
            for agent in self.ai_network.agents.values()
        ]
    
    async def add_custom_provider(
        self, 
        name: str, 
        api_key: str, 
        base_url: str,
        model: str
    ) -> Dict[str, Any]:
        """Добавление пользовательского провайдера"""
        result = self.ai_manager.add_custom_provider(name, api_key, base_url, model)
        
        if result.get("success"):
            # Создаём агентов для нового провайдера
            await self.populator.populate_agents_for_provider(name, model)
        
        return result
    
    async def generate_content(
        self, 
        topic: str, 
        keywords: List[str] = None,
        word_count: int = 1500
    ) -> Dict[str, Any]:
        """Генерация контента с использованием AI-агентов"""
        task = {
            "type": "content_generation",
            "data": {
                "topic": topic,
                "keywords": keywords or [],
                "word_count": word_count
            }
        }
        
        result = await run_parallel_seo(
            self.state.current_domain or "default",
            [task]
        )
        
        # Записываем для обучения
        if result.get("tasks"):
            task_result = result["tasks"][0]
            await record_learning(
                agent_name="content_writer",
                task_type="content_generation",
                input_data=task["data"],
                output_data=task_result.get("result", {}),
                success=task_result.get("success", False)
            )
        
        return result
    
    async def research_keywords(self, topic: str, count: int = 20) -> Dict[str, Any]:
        """Исследование ключевых слов"""
        task = {
            "type": "keyword_research",
            "data": {
                "topic": topic,
                "count": count
            }
        }
        
        return await run_parallel_seo(
            self.state.current_domain or "default",
            [task]
        )
    
    async def analyze_competitors(self, competitors: List[str]) -> Dict[str, Any]:
        """Анализ конкурентов"""
        task = {
            "type": "competitor_analysis",
            "data": {
                "competitors": competitors,
                "domain": self.state.current_domain
            }
        }
        
        return await run_parallel_seo(
            self.state.current_domain or "default",
            [task]
        )


    # ==================== БАЗОВЫЕ МЕТОДЫ (без AI Agents) ====================
    
    async def _basic_keyword_research(self, domain: str) -> Dict[str, Any]:
        """Базовый сбор ключевых слов без AI Agents"""
        logger.info(f"Basic keyword research for {domain}")
        
        # Используем простой провайдер напрямую
        try:
            response = await self.ai_manager.generate(
                prompt=f"Generate 10 SEO keywords for website about: {domain}. Return as JSON array of strings.",
                max_tokens=500
            )
            return {
                "success": True,
                "keywords": response.get("content", []),
                "mode": "basic"
            }
        except Exception as e:
            logger.error(f"Basic keyword research error: {e}")
            return {"success": False, "error": str(e), "mode": "basic"}
    
    async def _basic_content_generation(
        self, 
        domain: str, 
        count: int, 
        cycle: int
    ) -> Dict[str, Any]:
        """Базовая генерация контента без AI Agents (последовательно)"""
        logger.info(f"Basic content generation: {count} articles for {domain}")
        
        articles_generated = 0
        words_written = 0
        articles = []
        
        for i in range(count):
            try:
                response = await self.ai_manager.generate(
                    prompt=f"Write a 500-word SEO article about {domain}. Article #{cycle}_{i+1}.",
                    max_tokens=1500
                )
                
                content = response.get("content", "")
                if content:
                    articles_generated += 1
                    words_written += len(content.split())
                    articles.append({
                        "id": f"article_{cycle}_{i+1}",
                        "content": content,
                        "words": len(content.split())
                    })
                    
            except Exception as e:
                logger.error(f"Basic content generation error: {e}")
        
        return {
            "success": articles_generated > 0,
            "articles_generated": articles_generated,
            "words_written": words_written,
            "articles": articles,
            "mode": "basic"
        }
    
    async def _basic_indexing(self, domain: str) -> Dict[str, Any]:
        """Базовая индексация без AI Agents"""
        logger.info(f"Basic indexing for {domain}")
        
        # Простой ping без агентов
        import aiohttp
        
        urls_indexed = 0
        try:
            async with aiohttp.ClientSession() as session:
                # Ping Google
                ping_url = f"https://www.google.com/ping?sitemap=https://{domain}/sitemap.xml"
                async with session.get(ping_url, timeout=10) as resp:
                    if resp.status == 200:
                        urls_indexed += 1
        except:
            pass
        
        return {
            "success": True,
            "urls_indexed": urls_indexed,
            "mode": "basic"
        }
    
    # ==================== УПРАВЛЕНИЕ AI AGENTS ====================
    
    def set_ai_agents_enabled(self, enabled: bool) -> Dict[str, Any]:
        """Включение/выключение модуля AI Agents"""
        self.config["ai_agents_enabled"] = enabled
        self._save_config()
        
        status = "enabled" if enabled else "disabled"
        logger.info(f"🤖 AI Agents module {status}")
        
        return {
            "success": True,
            "ai_agents_enabled": enabled,
            "message": f"AI Agents module is now {status}"
        }
    
    def is_ai_agents_enabled(self) -> bool:
        """Проверка статуса модуля AI Agents"""
        return self.config.get("ai_agents_enabled", True)
    
    def get_ai_agents_status(self) -> Dict[str, Any]:
        """Получение полного статуса модуля AI Agents"""
        enabled = self.is_ai_agents_enabled()
        
        return {
            "enabled": enabled,
            "agents_active": self.state.agents_active if enabled else 0,
            "providers_healthy": self.state.providers_healthy if enabled else 0,
            "auto_learning": self.config.get("auto_learning", False) if enabled else False,
            "auto_update": self.config.get("auto_update_agents", False) if enabled else False,
            "parallel_execution": self.config.get("parallel_execution", False) if enabled else False,
            "mode": "advanced" if enabled else "basic"
        }


# Глобальный экземпляр Monster
monster = SEOMonsterCore()


# Удобные функции для API
async def start_monster_session(domain: str) -> Dict:
    """Запуск сессии Monster"""
    return await monster.start_session(domain)


async def run_monster_autopilot(domain: str, duration: int = 30, config: Dict = None) -> Dict:
    """Запуск автопилота Monster"""
    return await monster.run_full_autopilot(domain, duration, config)


def get_monster_status() -> Dict:
    """Получение статуса Monster"""
    return monster.get_status()


def get_monster_providers() -> List[Dict]:
    """Получение провайдеров Monster"""
    return monster.get_available_providers()


def get_monster_agents() -> List[Dict]:
    """Получение агентов Monster"""
    return monster.get_active_agents()
