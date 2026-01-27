"""
SEO Monster - Parallel SEO Executor
Параллельное выполнение SEO-задач несколькими AI-агентами одновременно
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

from .ai_providers import ai_manager
from .ai_communication import ai_network, ai_collaboration, AIAgentRole
from .ai_seo_integration import seo_orchestrator, SEOTaskType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Режимы выполнения"""
    SEQUENTIAL = "sequential"  # Последовательно
    PARALLEL = "parallel"      # Параллельно (asyncio)
    DISTRIBUTED = "distributed"  # Распределённо (multiprocessing)


@dataclass
class ParallelTaskResult:
    """Результат параллельного выполнения"""
    task_id: str
    agent_name: str
    success: bool
    result: Any
    execution_time: float
    error: Optional[str] = None


class ParallelSEOExecutor:
    """
    Параллельный исполнитель SEO-задач
    Координирует работу множества агентов одновременно
    """
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_executions: Dict[str, Dict] = {}
        self.execution_history: List[Dict] = []
        
        # Семафоры для контроля нагрузки на провайдеров
        self.provider_semaphores: Dict[str, asyncio.Semaphore] = {}
        self._init_provider_semaphores()
    
    def _init_provider_semaphores(self):
        """Инициализация семафоров для провайдеров"""
        # Лимиты запросов в минуту для каждого провайдера
        provider_limits = {
            "groq": 30,
            "together": 60,
            "huggingface": 30,
            "ollama": 100,  # Локальный, без ограничений
            "cohere": 20,
            "mistral": 30,
            "deepseek": 60,
            "openrouter": 20,
            "google": 60,
            "cloudflare": 50,
            "openai": 60
        }
        
        for provider, limit in provider_limits.items():
            # Делим лимит на 4 для безопасности (15 сек окно)
            self.provider_semaphores[provider] = asyncio.Semaphore(max(1, limit // 4))
    
    async def execute_parallel_seo_workflow(
        self, 
        domain: str, 
        tasks: List[Dict[str, Any]],
        mode: ExecutionMode = ExecutionMode.PARALLEL
    ) -> Dict[str, Any]:
        """
        Выполнение SEO-воркфлоу с параллельной обработкой задач
        """
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        self.active_executions[execution_id] = {
            "domain": domain,
            "started_at": start_time.isoformat(),
            "status": "running",
            "tasks_total": len(tasks),
            "tasks_completed": 0
        }
        
        results = {
            "execution_id": execution_id,
            "domain": domain,
            "mode": mode.value,
            "started_at": start_time.isoformat(),
            "tasks": [],
            "summary": {}
        }
        
        try:
            if mode == ExecutionMode.SEQUENTIAL:
                task_results = await self._execute_sequential(tasks)
            elif mode == ExecutionMode.PARALLEL:
                task_results = await self._execute_parallel(tasks)
            else:
                task_results = await self._execute_distributed(tasks)
            
            results["tasks"] = task_results
            results["summary"] = self._generate_summary(task_results)
            
        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {e}")
            results["error"] = str(e)
        
        finally:
            results["completed_at"] = datetime.now().isoformat()
            results["total_time"] = (datetime.now() - start_time).total_seconds()
            
            self.active_executions[execution_id]["status"] = "completed"
            self.active_executions[execution_id]["completed_at"] = results["completed_at"]
            
            self.execution_history.append(results)
        
        return results
    
    async def _execute_sequential(self, tasks: List[Dict]) -> List[Dict]:
        """Последовательное выполнение задач"""
        results = []
        for task in tasks:
            result = await self._execute_single_task(task)
            results.append(result)
        return results
    
    async def _execute_parallel(self, tasks: List[Dict]) -> List[Dict]:
        """Параллельное выполнение задач с asyncio"""
        # Группируем задачи по провайдерам для балансировки
        provider_tasks: Dict[str, List] = {}
        
        for task in tasks:
            provider = task.get("provider", "groq")
            if provider not in provider_tasks:
                provider_tasks[provider] = []
            provider_tasks[provider].append(task)
        
        # Создаём корутины с учётом семафоров
        coroutines = []
        for provider, provider_task_list in provider_tasks.items():
            for task in provider_task_list:
                coroutines.append(
                    self._execute_with_semaphore(provider, task)
                )
        
        # Выполняем параллельно
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Обрабатываем результаты
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_distributed(self, tasks: List[Dict]) -> List[Dict]:
        """Распределённое выполнение с multiprocessing"""
        # Для тяжёлых задач используем процессы
        loop = asyncio.get_event_loop()
        
        with ProcessPoolExecutor(max_workers=min(self.max_workers, multiprocessing.cpu_count())) as executor:
            futures = [
                loop.run_in_executor(executor, self._sync_execute_task, task)
                for task in tasks
            ]
            results = await asyncio.gather(*futures, return_exceptions=True)
        
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({"success": False, "error": str(result)})
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_with_semaphore(self, provider: str, task: Dict) -> Dict:
        """Выполнение задачи с учётом семафора провайдера"""
        semaphore = self.provider_semaphores.get(provider, asyncio.Semaphore(10))
        
        async with semaphore:
            return await self._execute_single_task(task)
    
    async def _execute_single_task(self, task: Dict) -> Dict:
        """Выполнение одной задачи"""
        start_time = datetime.now()
        task_type = task.get("type", "content_generation")
        
        try:
            # Получаем агентов для задачи
            agents = self._get_agents_for_task(task_type)
            
            # Выполняем задачу каждым агентом параллельно
            agent_results = await asyncio.gather(*[
                self._execute_agent_task(agent, task)
                for agent in agents
            ], return_exceptions=True)
            
            # Объединяем результаты
            combined_result = self._combine_agent_results(agent_results)
            
            return {
                "task_type": task_type,
                "success": True,
                "agents_used": [a.name for a in agents],
                "result": combined_result,
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            return {
                "task_type": task_type,
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    def _sync_execute_task(self, task: Dict) -> Dict:
        """Синхронная обёртка для выполнения задачи в процессе"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._execute_single_task(task))
        finally:
            loop.close()
    
    def _get_agents_for_task(self, task_type: str) -> List:
        """Получение подходящих агентов для типа задачи"""
        role_mapping = {
            "keyword_research": AIAgentRole.KEYWORD_RESEARCHER,
            "content_generation": AIAgentRole.CONTENT_WRITER,
            "competitor_analysis": AIAgentRole.COMPETITOR_ANALYST,
            "technical_audit": AIAgentRole.SEO_ANALYST,
            "translation": AIAgentRole.TRANSLATOR,
            "fact_checking": AIAgentRole.FACT_CHECKER,
            "reporting": AIAgentRole.DATA_ANALYST
        }
        
        role = role_mapping.get(task_type, AIAgentRole.CONTENT_WRITER)
        agents = ai_network.get_agents_by_role(role)
        
        # Добавляем редактора для контента
        if task_type == "content_generation":
            editors = ai_network.get_agents_by_role(AIAgentRole.EDITOR)
            agents.extend(editors)
        
        return agents[:3]  # Максимум 3 агента на задачу
    
    async def _execute_agent_task(self, agent, task: Dict) -> Dict:
        """Выполнение задачи конкретным агентом"""
        prompt = self._build_task_prompt(task)
        
        try:
            response = await ai_manager.generate(
                prompt=prompt,
                system_prompt=agent.system_prompt,
                provider=agent.provider,
                model=agent.model,
                max_tokens=3000
            )
            
            return {
                "agent": agent.name,
                "success": True,
                "response": response
            }
        except Exception as e:
            return {
                "agent": agent.name,
                "success": False,
                "error": str(e)
            }
    
    def _build_task_prompt(self, task: Dict) -> str:
        """Построение промпта для задачи"""
        task_type = task.get("type", "general")
        data = task.get("data", {})
        
        prompts = {
            "keyword_research": f"Research keywords for: {data.get('topic', 'general')}. Find 20 relevant keywords with search intent.",
            "content_generation": f"Write SEO-optimized article about: {data.get('topic', 'general')}. Include keywords: {data.get('keywords', [])}",
            "competitor_analysis": f"Analyze competitors: {data.get('competitors', [])} for domain {data.get('domain', '')}",
            "technical_audit": f"Perform technical SEO audit for: {data.get('url', '')}",
            "translation": f"Translate to {data.get('target_lang', 'en')}: {data.get('content', '')}",
            "meta_tags": f"Generate meta tags for: {data.get('page', '')} with keywords: {data.get('keywords', [])}"
        }
        
        return prompts.get(task_type, f"Execute SEO task: {task_type}")
    
    def _combine_agent_results(self, results: List) -> Dict:
        """Объединение результатов от нескольких агентов"""
        successful = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed = [r for r in results if isinstance(r, dict) and not r.get("success")]
        
        return {
            "successful_agents": len(successful),
            "failed_agents": len(failed),
            "responses": [r.get("response") for r in successful if r.get("response")],
            "errors": [r.get("error") for r in failed if r.get("error")]
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Генерация сводки по результатам"""
        successful = sum(1 for r in results if r.get("success"))
        total_time = sum(r.get("execution_time", 0) for r in results)
        
        return {
            "total_tasks": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "success_rate": successful / len(results) if results else 0,
            "total_execution_time": round(total_time, 2),
            "avg_task_time": round(total_time / len(results), 2) if results else 0
        }
    
    async def run_full_seo_campaign(
        self, 
        domain: str, 
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Запуск полной SEO-кампании с параллельным выполнением всех этапов
        """
        config = config or {}
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting full SEO campaign {campaign_id} for {domain}")
        
        # Этап 1: Анализ (параллельно)
        analysis_tasks = [
            {"type": "keyword_research", "data": {"domain": domain, "topic": config.get("niche", "general")}},
            {"type": "competitor_analysis", "data": {"domain": domain, "competitors": config.get("competitors", [])}},
            {"type": "technical_audit", "data": {"url": f"https://{domain}"}}
        ]
        
        analysis_results = await self.execute_parallel_seo_workflow(
            domain, analysis_tasks, ExecutionMode.PARALLEL
        )
        
        # Этап 2: Генерация контента (параллельно)
        content_tasks = []
        for i in range(config.get("articles_count", 5)):
            content_tasks.append({
                "type": "content_generation",
                "data": {
                    "topic": f"Article {i+1} about {config.get('niche', 'topic')}",
                    "keywords": config.get("keywords", []),
                    "word_count": config.get("word_count", 1500)
                }
            })
        
        content_results = await self.execute_parallel_seo_workflow(
            domain, content_tasks, ExecutionMode.PARALLEL
        )
        
        # Этап 3: Оптимизация (параллельно)
        optimization_tasks = [
            {"type": "meta_tags", "data": {"domain": domain, "pages": config.get("pages", [])}},
            {"type": "translation", "data": {"content": "Sample content", "target_lang": "ru"}} if config.get("translate") else None
        ]
        optimization_tasks = [t for t in optimization_tasks if t]
        
        optimization_results = await self.execute_parallel_seo_workflow(
            domain, optimization_tasks, ExecutionMode.PARALLEL
        ) if optimization_tasks else {"tasks": []}
        
        # Объединяем результаты
        campaign_results = {
            "campaign_id": campaign_id,
            "domain": domain,
            "config": config,
            "phases": {
                "analysis": analysis_results,
                "content": content_results,
                "optimization": optimization_results
            },
            "summary": {
                "total_tasks": (
                    len(analysis_results.get("tasks", [])) +
                    len(content_results.get("tasks", [])) +
                    len(optimization_results.get("tasks", []))
                ),
                "total_time": (
                    analysis_results.get("total_time", 0) +
                    content_results.get("total_time", 0) +
                    optimization_results.get("total_time", 0)
                )
            },
            "completed_at": datetime.now().isoformat()
        }
        
        # Сохраняем результаты кампании
        await self._save_campaign_results(campaign_results)
        
        return campaign_results
    
    async def _save_campaign_results(self, results: Dict):
        """Сохранение результатов кампании"""
        campaigns_dir = "/home/ubuntu/seo_monster/backend/data/campaigns"
        os.makedirs(campaigns_dir, exist_ok=True)
        
        filename = f"{campaigns_dir}/{results['campaign_id']}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Campaign results saved to {filename}")
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Получение статуса выполнения"""
        return {
            "active_executions": len(self.active_executions),
            "executions": self.active_executions,
            "history_count": len(self.execution_history),
            "provider_limits": {
                provider: semaphore._value
                for provider, semaphore in self.provider_semaphores.items()
            }
        }


# Глобальный экземпляр исполнителя
parallel_executor = ParallelSEOExecutor()


# Удобные функции
async def run_parallel_seo(domain: str, tasks: List[Dict]) -> Dict:
    """Запуск параллельного SEO"""
    return await parallel_executor.execute_parallel_seo_workflow(domain, tasks)


async def run_seo_campaign(domain: str, config: Dict = None) -> Dict:
    """Запуск полной SEO-кампании"""
    return await parallel_executor.run_full_seo_campaign(domain, config)


def get_executor_status() -> Dict:
    """Получение статуса исполнителя"""
    return parallel_executor.get_execution_status()
