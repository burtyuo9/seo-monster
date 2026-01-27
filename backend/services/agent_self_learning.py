"""
SEO Monster - Agent Self-Learning & Auto-Update Module
Система самообучения и автоматического обновления AI-агентов
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib
import random

from .ai_providers import ai_manager
from .ai_communication import ai_network, AIAgent, AIAgentRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LearningRecord:
    """Запись об обучении"""
    timestamp: str
    agent_name: str
    task_type: str
    input_data: Dict
    output_data: Dict
    success: bool
    feedback_score: float  # 0.0 - 1.0
    improvements: List[str] = field(default_factory=list)


@dataclass
class AgentEvolution:
    """Эволюция агента"""
    agent_name: str
    version: int
    created_at: str
    system_prompt: str
    capabilities: List[str]
    performance_metrics: Dict[str, float]
    parent_version: Optional[int] = None


class LearningStrategy(Enum):
    """Стратегии обучения"""
    REINFORCEMENT = "reinforcement"  # На основе успехов/неудач
    IMITATION = "imitation"          # Копирование успешных агентов
    EXPLORATION = "exploration"      # Экспериментирование
    COLLABORATIVE = "collaborative"  # Обучение от других агентов


class AgentSelfLearning:
    """
    Система самообучения AI-агентов
    Агенты учатся на своих результатах и автоматически улучшаются
    """
    
    def __init__(self):
        self.learning_records: List[LearningRecord] = []
        self.agent_evolutions: Dict[str, List[AgentEvolution]] = {}
        self.learning_enabled = True
        self.auto_update_enabled = True
        
        self.data_dir = "/home/ubuntu/seo_monster/backend/data/learning"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Загружаем историю обучения
        self._load_learning_history()
    
    def _load_learning_history(self):
        """Загрузка истории обучения"""
        history_file = f"{self.data_dir}/learning_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.learning_records = [
                        LearningRecord(**r) for r in data.get("records", [])
                    ]
            except Exception as e:
                logger.error(f"Error loading learning history: {e}")
    
    def _save_learning_history(self):
        """Сохранение истории обучения"""
        history_file = f"{self.data_dir}/learning_history.json"
        try:
            data = {
                "records": [asdict(r) for r in self.learning_records[-1000:]],  # Последние 1000
                "updated_at": datetime.now().isoformat()
            }
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning history: {e}")
    
    async def record_task_result(
        self,
        agent_name: str,
        task_type: str,
        input_data: Dict,
        output_data: Dict,
        success: bool,
        feedback_score: float = None
    ):
        """Запись результата выполнения задачи для обучения"""
        if not self.learning_enabled:
            return
        
        # Автоматическая оценка если не предоставлена
        if feedback_score is None:
            feedback_score = await self._auto_evaluate_output(output_data, task_type)
        
        record = LearningRecord(
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            task_type=task_type,
            input_data=input_data,
            output_data=output_data,
            success=success,
            feedback_score=feedback_score
        )
        
        self.learning_records.append(record)
        self._save_learning_history()
        
        # Анализируем и применяем улучшения
        if len(self.learning_records) % 10 == 0:  # Каждые 10 записей
            await self._analyze_and_improve(agent_name)
    
    async def _auto_evaluate_output(self, output: Dict, task_type: str) -> float:
        """Автоматическая оценка качества вывода"""
        score = 0.5  # Базовый балл
        
        # Проверяем наличие контента
        if output.get("response") or output.get("content"):
            score += 0.2
        
        # Проверяем длину ответа
        content = str(output.get("response", output.get("content", "")))
        if len(content) > 500:
            score += 0.1
        if len(content) > 1500:
            score += 0.1
        
        # Проверяем структуру (для контента)
        if task_type == "content_generation":
            if "##" in content or "<h" in content:  # Заголовки
                score += 0.05
            if any(kw in content.lower() for kw in ["keyword", "seo", "meta"]):
                score += 0.05
        
        return min(1.0, score)
    
    async def _analyze_and_improve(self, agent_name: str):
        """Анализ результатов и улучшение агента"""
        agent = ai_network.get_agent(agent_name)
        if not agent:
            return
        
        # Получаем последние записи для этого агента
        agent_records = [
            r for r in self.learning_records[-100:]
            if r.agent_name == agent_name
        ]
        
        if len(agent_records) < 5:
            return
        
        # Вычисляем метрики
        avg_score = sum(r.feedback_score for r in agent_records) / len(agent_records)
        success_rate = sum(1 for r in agent_records if r.success) / len(agent_records)
        
        logger.info(f"Agent {agent_name} metrics: avg_score={avg_score:.2f}, success_rate={success_rate:.2f}")
        
        # Если показатели низкие, пробуем улучшить
        if avg_score < 0.6 or success_rate < 0.7:
            await self._evolve_agent(agent, agent_records)
    
    async def _evolve_agent(self, agent: AIAgent, records: List[LearningRecord]):
        """Эволюция агента на основе обучения"""
        logger.info(f"Evolving agent {agent.name}...")
        
        # Анализируем успешные и неуспешные задачи
        successful = [r for r in records if r.success and r.feedback_score > 0.7]
        failed = [r for r in records if not r.success or r.feedback_score < 0.5]
        
        improvements = []
        
        # Стратегия 1: Усиление успешных паттернов
        if successful:
            successful_types = [r.task_type for r in successful]
            most_successful = max(set(successful_types), key=successful_types.count)
            improvements.append(f"Focus more on {most_successful} tasks")
        
        # Стратегия 2: Анализ неудач
        if failed:
            failed_types = [r.task_type for r in failed]
            most_failed = max(set(failed_types), key=failed_types.count)
            improvements.append(f"Improve handling of {most_failed} tasks")
        
        # Генерируем улучшенный системный промпт
        new_prompt = await self._generate_improved_prompt(agent, improvements)
        
        if new_prompt and new_prompt != agent.system_prompt:
            # Сохраняем эволюцию
            evolution = AgentEvolution(
                agent_name=agent.name,
                version=len(self.agent_evolutions.get(agent.name, [])) + 1,
                created_at=datetime.now().isoformat(),
                system_prompt=new_prompt,
                capabilities=agent.capabilities,
                performance_metrics={
                    "avg_score": sum(r.feedback_score for r in records) / len(records),
                    "success_rate": sum(1 for r in records if r.success) / len(records)
                },
                parent_version=len(self.agent_evolutions.get(agent.name, []))
            )
            
            if agent.name not in self.agent_evolutions:
                self.agent_evolutions[agent.name] = []
            self.agent_evolutions[agent.name].append(evolution)
            
            # Применяем новый промпт
            agent.system_prompt = new_prompt
            
            # Сохраняем эволюцию
            self._save_evolutions()
            
            logger.info(f"Agent {agent.name} evolved to version {evolution.version}")
    
    async def _generate_improved_prompt(
        self, 
        agent: AIAgent, 
        improvements: List[str]
    ) -> Optional[str]:
        """Генерация улучшенного системного промпта"""
        try:
            prompt = f"""You are an AI prompt engineer. Improve the following system prompt for an AI agent.

Current prompt:
{agent.system_prompt}

Agent role: {agent.role.value}
Agent capabilities: {', '.join(agent.capabilities)}

Suggested improvements based on performance analysis:
{chr(10).join(f'- {imp}' for imp in improvements)}

Generate an improved system prompt that:
1. Maintains the core role and capabilities
2. Addresses the suggested improvements
3. Is clear and actionable
4. Encourages better SEO-focused outputs

Return ONLY the improved prompt, nothing else."""

            response = await ai_manager.generate(
                prompt=prompt,
                max_tokens=1000
            )
            
            if response and len(response) > 100:
                return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating improved prompt: {e}")
        
        return None
    
    def _save_evolutions(self):
        """Сохранение эволюций агентов"""
        evolutions_file = f"{self.data_dir}/agent_evolutions.json"
        try:
            data = {
                agent_name: [asdict(e) for e in evolutions]
                for agent_name, evolutions in self.agent_evolutions.items()
            }
            with open(evolutions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving evolutions: {e}")


class AgentAutoUpdater:
    """
    Система автоматического обновления агентов
    Поиск новых моделей, провайдеров и улучшений
    """
    
    def __init__(self):
        self.update_interval = 3600  # 1 час
        self.last_update = datetime.now()
        self.update_sources = [
            "https://api.groq.com/openai/v1/models",
            "https://api.together.xyz/v1/models",
            "https://huggingface.co/api/models"
        ]
        self.discovered_models: List[Dict] = []
        self.data_dir = "/home/ubuntu/seo_monster/backend/data/updates"
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def check_for_updates(self) -> Dict[str, Any]:
        """Проверка наличия обновлений"""
        updates = {
            "timestamp": datetime.now().isoformat(),
            "new_models": [],
            "deprecated_models": [],
            "provider_status": {},
            "recommendations": []
        }
        
        # Проверяем каждый провайдер
        for provider in ai_manager.get_available_providers():
            status = await self._check_provider_status(provider["name"])
            updates["provider_status"][provider["name"]] = status
            
            if status.get("new_models"):
                updates["new_models"].extend(status["new_models"])
        
        # Генерируем рекомендации
        updates["recommendations"] = self._generate_recommendations(updates)
        
        # Сохраняем результаты проверки
        self._save_update_check(updates)
        
        return updates
    
    async def _check_provider_status(self, provider_name: str) -> Dict:
        """Проверка статуса провайдера"""
        status = {
            "name": provider_name,
            "healthy": False,
            "latency_ms": 0,
            "new_models": [],
            "checked_at": datetime.now().isoformat()
        }
        
        try:
            # Проверяем здоровье провайдера
            health = await ai_manager.check_provider_health(provider_name)
            status["healthy"] = health.get("healthy", False)
            status["latency_ms"] = health.get("latency_ms", 0)
            
        except Exception as e:
            logger.error(f"Error checking provider {provider_name}: {e}")
        
        return status
    
    def _generate_recommendations(self, updates: Dict) -> List[str]:
        """Генерация рекомендаций по обновлению"""
        recommendations = []
        
        # Проверяем нездоровые провайдеры
        unhealthy = [
            name for name, status in updates["provider_status"].items()
            if not status.get("healthy")
        ]
        
        if unhealthy:
            recommendations.append(
                f"Consider switching from unhealthy providers: {', '.join(unhealthy)}"
            )
        
        # Рекомендуем новые модели
        if updates["new_models"]:
            recommendations.append(
                f"New models available: {len(updates['new_models'])}. Consider testing them."
            )
        
        return recommendations
    
    def _save_update_check(self, updates: Dict):
        """Сохранение результатов проверки обновлений"""
        filename = f"{self.data_dir}/update_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(updates, f, indent=2)
    
    async def auto_update_agents(self) -> Dict[str, Any]:
        """Автоматическое обновление агентов"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "agents_updated": [],
            "new_agents_added": [],
            "agents_removed": []
        }
        
        # Проверяем обновления
        updates = await self.check_for_updates()
        
        # Обновляем агентов с нездоровыми провайдерами
        for agent in ai_network.agents.values():
            provider_status = updates["provider_status"].get(agent.provider, {})
            
            if not provider_status.get("healthy", True):
                # Ищем альтернативный провайдер
                for provider_name, status in updates["provider_status"].items():
                    if status.get("healthy") and provider_name != agent.provider:
                        old_provider = agent.provider
                        agent.provider = provider_name
                        results["agents_updated"].append({
                            "agent": agent.name,
                            "old_provider": old_provider,
                            "new_provider": provider_name
                        })
                        break
        
        # Добавляем новых агентов для новых моделей
        for model_info in updates.get("new_models", [])[:3]:  # Максимум 3 новых
            new_agent = self._create_agent_for_model(model_info)
            if new_agent:
                ai_network.register_agent(new_agent)
                results["new_agents_added"].append(new_agent.name)
        
        self.last_update = datetime.now()
        
        return results
    
    def _create_agent_for_model(self, model_info: Dict) -> Optional[AIAgent]:
        """Создание нового агента для модели"""
        try:
            model_name = model_info.get("id", model_info.get("name", ""))
            provider = model_info.get("provider", "unknown")
            
            agent = AIAgent(
                name=f"agent_{provider}_{model_name.replace('/', '_').replace('-', '_')}",
                role=AIAgentRole.CONTENT_WRITER,
                provider=provider,
                model=model_name,
                system_prompt=f"You are an AI assistant using {model_name}. Help with SEO tasks.",
                capabilities=["general", "content", "analysis"]
            )
            
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent for model: {e}")
            return None
    
    async def discover_new_free_services(self) -> List[Dict]:
        """Поиск новых бесплатных AI-сервисов"""
        discovered = []
        
        # Список потенциальных бесплатных сервисов для проверки
        potential_services = [
            {"name": "Perplexity", "url": "https://www.perplexity.ai/", "type": "search"},
            {"name": "You.com", "url": "https://you.com/", "type": "search"},
            {"name": "Phind", "url": "https://www.phind.com/", "type": "code"},
            {"name": "HuggingChat", "url": "https://huggingface.co/chat/", "type": "chat"},
            {"name": "Poe", "url": "https://poe.com/", "type": "chat"},
            {"name": "Forefront", "url": "https://chat.forefront.ai/", "type": "chat"},
            {"name": "Ora.ai", "url": "https://ora.ai/", "type": "chat"},
            {"name": "ChatGPT Free", "url": "https://chat.openai.com/", "type": "chat"},
            {"name": "Claude Free", "url": "https://claude.ai/", "type": "chat"},
            {"name": "Gemini", "url": "https://gemini.google.com/", "type": "chat"}
        ]
        
        for service in potential_services:
            try:
                # Проверяем доступность
                async with aiohttp.ClientSession() as session:
                    async with session.head(service["url"], timeout=5) as response:
                        if response.status == 200:
                            discovered.append({
                                **service,
                                "status": "available",
                                "checked_at": datetime.now().isoformat()
                            })
            except:
                pass
        
        self.discovered_models = discovered
        return discovered


class AgentPopulator:
    """
    Система автоматического пополнения агентов
    Создаёт новых специализированных агентов на основе потребностей
    """
    
    def __init__(self):
        self.agent_templates = {
            AIAgentRole.CONTENT_WRITER: {
                "system_prompt": """You are an expert SEO content writer. Your tasks:
- Write engaging, SEO-optimized articles
- Use keywords naturally throughout the content
- Create compelling headlines and meta descriptions
- Structure content with proper headings (H1, H2, H3)
- Include internal linking suggestions
- Maintain readability while optimizing for search engines""",
                "capabilities": ["content_writing", "seo_optimization", "copywriting"]
            },
            AIAgentRole.KEYWORD_RESEARCHER: {
                "system_prompt": """You are a keyword research specialist. Your tasks:
- Identify high-value keywords and phrases
- Analyze search intent (informational, navigational, transactional)
- Find long-tail keyword opportunities
- Cluster keywords by topic and intent
- Estimate keyword difficulty and potential
- Discover semantic variations and LSI keywords""",
                "capabilities": ["keyword_research", "search_intent", "semantic_analysis"]
            },
            AIAgentRole.COMPETITOR_ANALYST: {
                "system_prompt": """You are a competitive analysis expert. Your tasks:
- Analyze competitor content strategies
- Identify content gaps and opportunities
- Study competitor keyword targeting
- Evaluate backlink profiles
- Assess technical SEO implementations
- Provide actionable competitive insights""",
                "capabilities": ["competitor_analysis", "gap_analysis", "strategy"]
            },
            AIAgentRole.SEO_ANALYST: {
                "system_prompt": """You are a technical SEO analyst. Your tasks:
- Audit website technical health
- Identify crawlability issues
- Check page speed factors
- Analyze mobile optimization
- Review schema markup implementation
- Evaluate Core Web Vitals
- Provide technical recommendations""",
                "capabilities": ["technical_seo", "site_audit", "performance"]
            },
            AIAgentRole.EDITOR: {
                "system_prompt": """You are a professional content editor. Your tasks:
- Review and improve content quality
- Ensure proper grammar and style
- Optimize readability scores
- Maintain consistent brand voice
- Enhance SEO elements
- Fact-check and verify information""",
                "capabilities": ["editing", "proofreading", "quality_assurance"]
            },
            AIAgentRole.TRANSLATOR: {
                "system_prompt": """You are a multilingual SEO translator. Your tasks:
- Translate content while preserving SEO value
- Localize keywords for target markets
- Adapt cultural references appropriately
- Maintain brand voice across languages
- Optimize translated meta tags
- Ensure natural language flow""",
                "capabilities": ["translation", "localization", "multilingual_seo"]
            },
            AIAgentRole.DATA_ANALYST: {
                "system_prompt": """You are an SEO data analyst. Your tasks:
- Analyze traffic and ranking data
- Identify trends and patterns
- Create performance reports
- Forecast SEO outcomes
- Measure campaign effectiveness
- Provide data-driven recommendations""",
                "capabilities": ["data_analysis", "reporting", "forecasting"]
            },
            AIAgentRole.FACT_CHECKER: {
                "system_prompt": """You are a fact-checking specialist. Your tasks:
- Verify claims and statistics
- Check source credibility
- Identify potential misinformation
- Ensure content accuracy
- Validate data and references
- Flag questionable content""",
                "capabilities": ["fact_checking", "verification", "research"]
            }
        }
    
    async def populate_agents_for_provider(self, provider_name: str, model: str) -> List[AIAgent]:
        """Создание набора агентов для провайдера"""
        created_agents = []
        
        for role, template in self.agent_templates.items():
            agent_name = f"{role.value}_{provider_name}_{model.replace('/', '_').replace('-', '_')}"
            
            # Проверяем, существует ли уже такой агент
            if ai_network.get_agent(agent_name):
                continue
            
            agent = AIAgent(
                name=agent_name,
                role=role,
                provider=provider_name,
                model=model,
                system_prompt=template["system_prompt"],
                capabilities=template["capabilities"]
            )
            
            ai_network.register_agent(agent)
            created_agents.append(agent)
            
            logger.info(f"Created agent: {agent_name}")
        
        return created_agents
    
    async def ensure_minimum_agents(self) -> Dict[str, Any]:
        """Обеспечение минимального количества агентов для каждой роли"""
        results = {
            "checked_at": datetime.now().isoformat(),
            "roles_status": {},
            "agents_created": []
        }
        
        min_agents_per_role = 2
        
        for role in AIAgentRole:
            agents = ai_network.get_agents_by_role(role)
            results["roles_status"][role.value] = len(agents)
            
            if len(agents) < min_agents_per_role:
                # Создаём дополнительных агентов
                needed = min_agents_per_role - len(agents)
                providers = ai_manager.get_available_providers()
                
                for i, provider in enumerate(providers[:needed]):
                    if provider.get("enabled"):
                        new_agents = await self.populate_agents_for_provider(
                            provider["name"],
                            provider["model"]
                        )
                        results["agents_created"].extend([a.name for a in new_agents])
        
        return results


# Глобальные экземпляры
agent_learning = AgentSelfLearning()
agent_updater = AgentAutoUpdater()
agent_populator = AgentPopulator()


# Удобные функции
async def record_learning(agent_name: str, task_type: str, input_data: Dict, 
                          output_data: Dict, success: bool):
    """Запись результата для обучения"""
    await agent_learning.record_task_result(
        agent_name, task_type, input_data, output_data, success
    )


async def check_and_update_agents() -> Dict:
    """Проверка и обновление агентов"""
    return await agent_updater.auto_update_agents()


async def ensure_agents() -> Dict:
    """Обеспечение наличия агентов"""
    return await agent_populator.ensure_minimum_agents()


# Метод get_stats для совместимости с диагностикой
def get_stats(self=None) -> Dict:
    """Получение статистики системы обучения"""
    if self is None:
        self = agent_learning
    
    return {
        "learning_enabled": self.learning_enabled,
        "auto_update_enabled": self.auto_update_enabled,
        "total_records": len(self.learning_records),
        "agent_evolutions": len(self.agent_evolutions),
        "success_rate": sum(1 for r in self.learning_records if r.success) / max(len(self.learning_records), 1),
        "last_update": getattr(self, 'last_update', None)
    }

# Добавляем метод к классу
AgentSelfLearning.get_stats = get_stats
