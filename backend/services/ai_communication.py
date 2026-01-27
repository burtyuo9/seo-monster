"""
SEO Monster - AI-to-AI Communication Module
Модуль для общения с другими AI-агентами и сервисами
Позволяет SEO Monster координировать работу с внешними AI-помощниками
"""

import os
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAgentRole(Enum):
    """Роли AI-агентов"""
    CONTENT_WRITER = "content_writer"      # Написание контента
    SEO_ANALYST = "seo_analyst"            # SEO анализ
    KEYWORD_RESEARCHER = "keyword_researcher"  # Исследование ключевых слов
    COMPETITOR_ANALYST = "competitor_analyst"  # Анализ конкурентов
    TRANSLATOR = "translator"              # Перевод
    EDITOR = "editor"                      # Редактирование
    FACT_CHECKER = "fact_checker"          # Проверка фактов
    CODE_ASSISTANT = "code_assistant"      # Помощь с кодом
    DATA_ANALYST = "data_analyst"          # Анализ данных
    CREATIVE_WRITER = "creative_writer"    # Креативное письмо


@dataclass
class AIAgent:
    """Описание AI-агента"""
    name: str
    role: AIAgentRole
    provider: str  # groq, together, huggingface, etc.
    model: str
    system_prompt: str
    capabilities: List[str] = field(default_factory=list)
    is_active: bool = True
    last_used: Optional[datetime] = None
    success_rate: float = 1.0
    total_requests: int = 0


@dataclass
class AIMessage:
    """Сообщение между AI-агентами"""
    sender: str
    receiver: str
    content: str
    message_type: str  # request, response, broadcast
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIAgentNetwork:
    """
    Сеть AI-агентов для SEO Monster
    Позволяет координировать работу множества специализированных AI
    """
    
    def __init__(self):
        self.agents: Dict[str, AIAgent] = {}
        self.message_history: List[AIMessage] = []
        self.task_queue: List[Dict[str, Any]] = []
        self._setup_default_agents()
    
    def _setup_default_agents(self):
        """Настройка стандартных AI-агентов"""
        
        # SEO Content Writer - специализируется на SEO-контенте
        self.register_agent(AIAgent(
            name="seo_writer",
            role=AIAgentRole.CONTENT_WRITER,
            provider="groq",
            model="llama-3.3-70b-versatile",
            system_prompt="""You are an expert SEO content writer. Your task is to create 
            high-quality, engaging, and SEO-optimized content. Focus on:
            - Natural keyword integration
            - Compelling headlines and subheadings
            - Readable and engaging prose
            - Proper content structure (H1, H2, H3)
            - Meta descriptions and title tags
            Always write in a professional yet accessible tone.""",
            capabilities=["article_writing", "meta_tags", "headlines", "product_descriptions"]
        ))
        
        # Keyword Research Specialist
        self.register_agent(AIAgent(
            name="keyword_specialist",
            role=AIAgentRole.KEYWORD_RESEARCHER,
            provider="together",
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            system_prompt="""You are a keyword research specialist. Your expertise includes:
            - Identifying high-value keywords and phrases
            - Understanding search intent (informational, transactional, navigational)
            - Finding long-tail keyword opportunities
            - Analyzing keyword difficulty and competition
            - Suggesting semantic keyword clusters
            Provide actionable keyword recommendations with estimated metrics.""",
            capabilities=["keyword_analysis", "search_intent", "competitor_keywords", "long_tail"]
        ))
        
        # Competitor Analyst
        self.register_agent(AIAgent(
            name="competitor_analyst",
            role=AIAgentRole.COMPETITOR_ANALYST,
            provider="groq",
            model="llama-3.3-70b-versatile",
            system_prompt="""You are a competitive intelligence analyst specializing in SEO.
            Your tasks include:
            - Analyzing competitor content strategies
            - Identifying content gaps and opportunities
            - Evaluating backlink profiles
            - Assessing technical SEO implementations
            - Recommending competitive advantages
            Provide detailed, actionable competitive insights.""",
            capabilities=["competitor_analysis", "gap_analysis", "backlink_analysis", "strategy"]
        ))
        
        # Technical SEO Expert
        self.register_agent(AIAgent(
            name="tech_seo_expert",
            role=AIAgentRole.SEO_ANALYST,
            provider="deepseek",
            model="deepseek-chat",
            system_prompt="""You are a technical SEO expert. Your expertise covers:
            - Site architecture and crawlability
            - Page speed optimization
            - Mobile-first indexing
            - Schema markup and structured data
            - Core Web Vitals optimization
            - XML sitemaps and robots.txt
            Provide specific technical recommendations with implementation details.""",
            capabilities=["technical_audit", "schema_markup", "speed_optimization", "crawlability"]
        ))
        
        # Content Editor
        self.register_agent(AIAgent(
            name="content_editor",
            role=AIAgentRole.EDITOR,
            provider="cohere",
            model="command-r-plus",
            system_prompt="""You are a professional content editor. Your responsibilities:
            - Improving content clarity and readability
            - Ensuring grammatical correctness
            - Enhancing content flow and structure
            - Maintaining consistent tone and voice
            - Optimizing for both users and search engines
            Edit content to be engaging, error-free, and impactful.""",
            capabilities=["proofreading", "style_editing", "content_improvement", "readability"]
        ))
        
        # Multilingual Translator
        self.register_agent(AIAgent(
            name="translator",
            role=AIAgentRole.TRANSLATOR,
            provider="groq",
            model="llama-3.3-70b-versatile",
            system_prompt="""You are a professional translator specializing in SEO content.
            Your capabilities:
            - Accurate translation while preserving SEO value
            - Localization of keywords for target markets
            - Cultural adaptation of content
            - Maintaining brand voice across languages
            Translate content naturally while optimizing for local search.""",
            capabilities=["translation", "localization", "multilingual_seo", "cultural_adaptation"]
        ))
        
        # Data Analyst
        self.register_agent(AIAgent(
            name="data_analyst",
            role=AIAgentRole.DATA_ANALYST,
            provider="together",
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            system_prompt="""You are a data analyst specializing in SEO metrics and analytics.
            Your expertise includes:
            - Analyzing traffic patterns and trends
            - Interpreting ranking data
            - Identifying performance anomalies
            - Creating actionable reports
            - Forecasting SEO outcomes
            Provide data-driven insights and recommendations.""",
            capabilities=["analytics", "reporting", "forecasting", "trend_analysis"]
        ))
        
        # Creative Content Writer
        self.register_agent(AIAgent(
            name="creative_writer",
            role=AIAgentRole.CREATIVE_WRITER,
            provider="openrouter",
            model="meta-llama/llama-3.2-3b-instruct:free",
            system_prompt="""You are a creative content writer with SEO expertise.
            Your strengths:
            - Crafting compelling narratives
            - Creating viral-worthy headlines
            - Writing engaging social media content
            - Developing unique content angles
            - Storytelling that connects with audiences
            Create content that captivates readers while meeting SEO goals.""",
            capabilities=["creative_writing", "storytelling", "social_content", "viral_content"]
        ))
        
        # Fact Checker
        self.register_agent(AIAgent(
            name="fact_checker",
            role=AIAgentRole.FACT_CHECKER,
            provider="huggingface",
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            system_prompt="""You are a meticulous fact-checker. Your responsibilities:
            - Verifying claims and statistics
            - Identifying potential misinformation
            - Checking source credibility
            - Ensuring content accuracy
            - Flagging unverified claims
            Maintain the highest standards of accuracy and truthfulness.""",
            capabilities=["fact_checking", "source_verification", "accuracy_review", "claim_validation"]
        ))
    
    def register_agent(self, agent: AIAgent):
        """Регистрация нового AI-агента"""
        self.agents[agent.name] = agent
        logger.info(f"Registered AI agent: {agent.name} ({agent.role.value})")
    
    def get_agent(self, name: str) -> Optional[AIAgent]:
        """Получение агента по имени"""
        return self.agents.get(name)
    
    def get_agents_by_role(self, role: AIAgentRole) -> List[AIAgent]:
        """Получение агентов по роли"""
        return [a for a in self.agents.values() if a.role == role and a.is_active]
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Получение информации о всех агентах"""
        return [
            {
                "name": a.name,
                "role": a.role.value,
                "provider": a.provider,
                "model": a.model,
                "capabilities": a.capabilities,
                "is_active": a.is_active,
                "success_rate": a.success_rate,
                "total_requests": a.total_requests
            }
            for a in self.agents.values()
        ]
    
    async def send_message(self, sender: str, receiver: str, content: str, 
                          message_type: str = "request", metadata: Dict = None) -> AIMessage:
        """Отправка сообщения между агентами"""
        message = AIMessage(
            sender=sender,
            receiver=receiver,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        self.message_history.append(message)
        logger.info(f"Message sent: {sender} -> {receiver}")
        return message
    
    async def broadcast(self, sender: str, content: str, 
                       target_roles: List[AIAgentRole] = None) -> List[AIMessage]:
        """Рассылка сообщения нескольким агентам"""
        messages = []
        for agent in self.agents.values():
            if target_roles is None or agent.role in target_roles:
                if agent.is_active and agent.name != sender:
                    msg = await self.send_message(sender, agent.name, content, "broadcast")
                    messages.append(msg)
        return messages
    
    def get_message_history(self, agent_name: str = None, limit: int = 100) -> List[Dict]:
        """Получение истории сообщений"""
        history = self.message_history
        if agent_name:
            history = [m for m in history if m.sender == agent_name or m.receiver == agent_name]
        return [
            {
                "sender": m.sender,
                "receiver": m.receiver,
                "content": m.content[:200] + "..." if len(m.content) > 200 else m.content,
                "type": m.message_type,
                "timestamp": m.timestamp.isoformat()
            }
            for m in history[-limit:]
        ]


class AICollaborationManager:
    """
    Менеджер коллаборации AI-агентов
    Координирует совместную работу над задачами
    """
    
    def __init__(self, network: AIAgentNetwork):
        self.network = network
        self.active_collaborations: Dict[str, Dict] = {}
    
    async def create_collaboration(self, task_name: str, 
                                   required_roles: List[AIAgentRole],
                                   task_description: str) -> str:
        """Создание новой коллаборации для задачи"""
        collaboration_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_name}"
        
        # Подбираем агентов для каждой роли
        assigned_agents = {}
        for role in required_roles:
            agents = self.network.get_agents_by_role(role)
            if agents:
                # Выбираем агента с лучшим success_rate
                best_agent = max(agents, key=lambda a: a.success_rate)
                assigned_agents[role.value] = best_agent.name
        
        self.active_collaborations[collaboration_id] = {
            "task_name": task_name,
            "description": task_description,
            "agents": assigned_agents,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "results": {}
        }
        
        logger.info(f"Created collaboration: {collaboration_id} with agents: {assigned_agents}")
        return collaboration_id
    
    async def execute_collaborative_task(self, collaboration_id: str, 
                                         task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение задачи с участием нескольких агентов"""
        if collaboration_id not in self.active_collaborations:
            raise ValueError(f"Collaboration {collaboration_id} not found")
        
        collab = self.active_collaborations[collaboration_id]
        results = {}
        
        # Каждый агент выполняет свою часть
        for role, agent_name in collab["agents"].items():
            agent = self.network.get_agent(agent_name)
            if agent:
                # Здесь будет вызов AI провайдера для выполнения задачи
                results[role] = {
                    "agent": agent_name,
                    "status": "completed",
                    "output": f"Task completed by {agent_name}"
                }
                agent.total_requests += 1
                agent.last_used = datetime.now()
        
        collab["results"] = results
        collab["status"] = "completed"
        
        return results
    
    def get_collaboration_status(self, collaboration_id: str) -> Dict[str, Any]:
        """Получение статуса коллаборации"""
        return self.active_collaborations.get(collaboration_id, {})


class ExternalAIConnector:
    """
    Коннектор для связи с внешними AI-сервисами и агентами
    """
    
    # Список бесплатных AI-сервисов для интеграции
    EXTERNAL_AI_SERVICES = {
        "perplexity": {
            "name": "Perplexity AI",
            "url": "https://api.perplexity.ai",
            "capabilities": ["search", "research", "fact_checking"],
            "is_free": True,
            "description": "AI-powered search engine with real-time information"
        },
        "you_com": {
            "name": "You.com AI",
            "url": "https://api.you.com",
            "capabilities": ["search", "chat", "code"],
            "is_free": True,
            "description": "AI search assistant with multiple modes"
        },
        "phind": {
            "name": "Phind",
            "url": "https://api.phind.com",
            "capabilities": ["code", "technical_search"],
            "is_free": True,
            "description": "AI search engine for developers"
        },
        "poe": {
            "name": "Poe by Quora",
            "url": "https://poe.com/api",
            "capabilities": ["chat", "multiple_models"],
            "is_free": True,
            "description": "Access to multiple AI models through one interface"
        },
        "chatgpt_free": {
            "name": "ChatGPT (Free)",
            "url": "https://chat.openai.com",
            "capabilities": ["chat", "analysis", "writing"],
            "is_free": True,
            "description": "OpenAI's ChatGPT free tier"
        },
        "claude_free": {
            "name": "Claude (Free)",
            "url": "https://claude.ai",
            "capabilities": ["chat", "analysis", "coding"],
            "is_free": True,
            "description": "Anthropic's Claude free tier"
        },
        "gemini_free": {
            "name": "Google Gemini (Free)",
            "url": "https://gemini.google.com",
            "capabilities": ["chat", "multimodal", "search"],
            "is_free": True,
            "description": "Google's Gemini AI free tier"
        },
        "copilot_free": {
            "name": "Microsoft Copilot (Free)",
            "url": "https://copilot.microsoft.com",
            "capabilities": ["chat", "search", "image_generation"],
            "is_free": True,
            "description": "Microsoft's AI assistant with Bing integration"
        },
        "huggingchat": {
            "name": "HuggingChat",
            "url": "https://huggingface.co/chat",
            "capabilities": ["chat", "open_source_models"],
            "is_free": True,
            "description": "Free chat interface for open-source models"
        },
        "forefront": {
            "name": "Forefront AI",
            "url": "https://chat.forefront.ai",
            "capabilities": ["chat", "personas", "multiple_models"],
            "is_free": True,
            "description": "Free access to GPT-4 and Claude with personas"
        }
    }
    
    def __init__(self):
        self.connected_services: Dict[str, bool] = {}
    
    def get_available_services(self) -> List[Dict[str, Any]]:
        """Получение списка доступных внешних AI-сервисов"""
        return [
            {
                "id": service_id,
                **service_info,
                "connected": self.connected_services.get(service_id, False)
            }
            for service_id, service_info in self.EXTERNAL_AI_SERVICES.items()
        ]
    
    def get_free_services(self) -> List[Dict[str, Any]]:
        """Получение только бесплатных сервисов"""
        return [s for s in self.get_available_services() if s["is_free"]]
    
    async def connect_service(self, service_id: str, api_key: str = None) -> bool:
        """Подключение к внешнему AI-сервису"""
        if service_id in self.EXTERNAL_AI_SERVICES:
            self.connected_services[service_id] = True
            logger.info(f"Connected to external AI service: {service_id}")
            return True
        return False
    
    async def query_service(self, service_id: str, query: str) -> Dict[str, Any]:
        """Запрос к внешнему AI-сервису"""
        if service_id not in self.connected_services:
            raise ValueError(f"Service {service_id} is not connected")
        
        # Здесь будет реальная интеграция с сервисом
        return {
            "service": service_id,
            "query": query,
            "response": f"Response from {service_id}",
            "timestamp": datetime.now().isoformat()
        }


# Глобальные экземпляры
ai_network = AIAgentNetwork()
ai_collaboration = AICollaborationManager(ai_network)
external_connector = ExternalAIConnector()


# Удобные функции для использования
def get_all_ai_agents() -> List[Dict[str, Any]]:
    """Получение списка всех AI-агентов"""
    return ai_network.get_all_agents()


def get_external_ai_services() -> List[Dict[str, Any]]:
    """Получение списка внешних AI-сервисов"""
    return external_connector.get_available_services()


def get_free_ai_helpers() -> Dict[str, Any]:
    """Получение полного списка бесплатных AI-помощников"""
    return {
        "internal_agents": ai_network.get_all_agents(),
        "external_services": external_connector.get_free_services(),
        "total_agents": len(ai_network.agents),
        "total_services": len(external_connector.EXTERNAL_AI_SERVICES)
    }
