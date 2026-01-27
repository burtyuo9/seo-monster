"""
SEO Monster - AI Provider Manager
Модуль для работы с множеством AI-провайдеров (бесплатных и платных)
Позволяет SEO Monster работать полностью автономно без OpenAI
"""

import os
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProviderType(Enum):
    """Типы AI провайдеров"""
    OPENAI = "openai"
    GROQ = "groq"
    TOGETHER = "together"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    COHERE = "cohere"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"
    GOOGLE_GEMINI = "google_gemini"
    CLOUDFLARE = "cloudflare"
    PERPLEXITY = "perplexity"


@dataclass
class AIProviderConfig:
    """Конфигурация AI провайдера"""
    name: str
    provider_type: AIProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = ""
    is_free: bool = False
    rate_limit: int = 100  # запросов в минуту
    max_tokens: int = 4096
    enabled: bool = True
    priority: int = 1  # 1 = высший приоритет


# Список бесплатных AI провайдеров
FREE_AI_PROVIDERS = {
    # Groq - бесплатный, очень быстрый
    "groq": AIProviderConfig(
        name="Groq (Free)",
        provider_type=AIProviderType.GROQ,
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
        is_free=True,
        rate_limit=30,
        max_tokens=8192,
        priority=1
    ),
    
    # Together AI - бесплатный тир
    "together": AIProviderConfig(
        name="Together AI (Free Tier)",
        provider_type=AIProviderType.TOGETHER,
        base_url="https://api.together.xyz/v1",
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        is_free=True,
        rate_limit=60,
        max_tokens=4096,
        priority=2
    ),
    
    # HuggingFace Inference API - бесплатный
    "huggingface": AIProviderConfig(
        name="HuggingFace (Free)",
        provider_type=AIProviderType.HUGGINGFACE,
        base_url="https://api-inference.huggingface.co/models",
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        is_free=True,
        rate_limit=30,
        max_tokens=4096,
        priority=3
    ),
    
    # Ollama - локальный, полностью бесплатный
    "ollama": AIProviderConfig(
        name="Ollama (Local)",
        provider_type=AIProviderType.OLLAMA,
        base_url="http://localhost:11434",
        model="llama3.2",
        is_free=True,
        rate_limit=1000,
        max_tokens=8192,
        priority=4
    ),
    
    # Cohere - бесплатный тир
    "cohere": AIProviderConfig(
        name="Cohere (Free Tier)",
        provider_type=AIProviderType.COHERE,
        base_url="https://api.cohere.ai/v1",
        model="command-r-plus",
        is_free=True,
        rate_limit=20,
        max_tokens=4096,
        priority=5
    ),
    
    # Mistral AI - бесплатный тир
    "mistral": AIProviderConfig(
        name="Mistral AI (Free)",
        provider_type=AIProviderType.MISTRAL,
        base_url="https://api.mistral.ai/v1",
        model="mistral-large-latest",
        is_free=True,
        rate_limit=30,
        max_tokens=8192,
        priority=6
    ),
    
    # DeepSeek - очень дешёвый/бесплатный
    "deepseek": AIProviderConfig(
        name="DeepSeek (Free Tier)",
        provider_type=AIProviderType.DEEPSEEK,
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        is_free=True,
        rate_limit=60,
        max_tokens=8192,
        priority=7
    ),
    
    # OpenRouter - агрегатор с бесплатными моделями
    "openrouter": AIProviderConfig(
        name="OpenRouter (Free Models)",
        provider_type=AIProviderType.OPENROUTER,
        base_url="https://openrouter.ai/api/v1",
        model="meta-llama/llama-3.2-3b-instruct:free",
        is_free=True,
        rate_limit=20,
        max_tokens=4096,
        priority=8
    ),
    
    # Google Gemini - бесплатный тир
    "google_gemini": AIProviderConfig(
        name="Google Gemini (Free)",
        provider_type=AIProviderType.GOOGLE_GEMINI,
        base_url="https://generativelanguage.googleapis.com/v1beta",
        model="gemini-1.5-flash",
        is_free=True,
        rate_limit=60,
        max_tokens=8192,
        priority=9
    ),
    
    # Cloudflare Workers AI - бесплатный тир
    "cloudflare": AIProviderConfig(
        name="Cloudflare Workers AI (Free)",
        provider_type=AIProviderType.CLOUDFLARE,
        base_url="https://api.cloudflare.com/client/v4/accounts",
        model="@cf/meta/llama-3.1-8b-instruct",
        is_free=True,
        rate_limit=50,
        max_tokens=2048,
        priority=10
    ),
}


class BaseAIProvider(ABC):
    """Базовый класс для AI провайдеров"""
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.api_key = config.api_key or os.getenv(f"{config.provider_type.value.upper()}_API_KEY", "")
        
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Генерация текста"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Чат с историей сообщений"""
        pass
    
    async def is_available(self) -> bool:
        """Проверка доступности провайдера"""
        try:
            response = await self.generate("Hello", max_tokens=10)
            return len(response) > 0
        except Exception as e:
            logger.warning(f"Provider {self.config.name} unavailable: {e}")
            return False


class GroqProvider(BaseAIProvider):
    """Groq - бесплатный и очень быстрый"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": kwargs.get("model", self.config.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", 0.7)
            }
            async with session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    raise Exception(f"Groq API error: {error}")


class TogetherProvider(BaseAIProvider):
    """Together AI - бесплатный тир"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": kwargs.get("model", self.config.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", 0.7)
            }
            async with session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    raise Exception(f"Together API error: {error}")


class HuggingFaceProvider(BaseAIProvider):
    """HuggingFace Inference API - бесплатный"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", 0.7),
                    "return_full_text": False
                }
            }
            model = kwargs.get("model", self.config.model)
            async with session.post(
                f"{self.config.base_url}/{model}",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get("generated_text", "")
                    return str(data)
                else:
                    error = await response.text()
                    raise Exception(f"HuggingFace API error: {error}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # Конвертируем chat формат в prompt
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        prompt_parts.append("Assistant:")
        return await self.generate("\n".join(prompt_parts), **kwargs)


class OllamaProvider(BaseAIProvider):
    """Ollama - локальный, полностью бесплатный"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": kwargs.get("model", self.config.model),
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }
            async with session.post(
                f"{self.config.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                else:
                    error = await response.text()
                    raise Exception(f"Ollama API error: {error}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": kwargs.get("model", self.config.model),
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", 0.7)
                }
            }
            async with session.post(
                f"{self.config.base_url}/api/chat",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("message", {}).get("content", "")
                else:
                    error = await response.text()
                    raise Exception(f"Ollama API error: {error}")


class CohereProvider(BaseAIProvider):
    """Cohere - бесплатный тир"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": kwargs.get("model", self.config.model),
                "message": prompt,
                "preamble": system_prompt if system_prompt else None,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", 0.7)
            }
            async with session.post(
                f"{self.config.base_url}/chat",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("text", "")
                else:
                    error = await response.text()
                    raise Exception(f"Cohere API error: {error}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # Извлекаем последнее сообщение пользователя
        user_message = ""
        chat_history = []
        system_prompt = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                if user_message:
                    chat_history.append({"role": "USER", "message": user_message})
                user_message = msg["content"]
            elif msg["role"] == "assistant":
                chat_history.append({"role": "CHATBOT", "message": msg["content"]})
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": kwargs.get("model", self.config.model),
                "message": user_message,
                "chat_history": chat_history if chat_history else None,
                "preamble": system_prompt if system_prompt else None,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", 0.7)
            }
            async with session.post(
                f"{self.config.base_url}/chat",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("text", "")
                else:
                    error = await response.text()
                    raise Exception(f"Cohere API error: {error}")


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter - агрегатор с бесплатными моделями"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://seo-monster.local",
                "X-Title": "SEO Monster"
            }
            payload = {
                "model": kwargs.get("model", self.config.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", 0.7)
            }
            async with session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    raise Exception(f"OpenRouter API error: {error}")


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek - очень дешёвый/бесплатный"""
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": kwargs.get("model", self.config.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", 0.7)
            }
            async with session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    raise Exception(f"DeepSeek API error: {error}")


class AIProviderManager:
    """
    Менеджер AI провайдеров
    Автоматически выбирает лучший доступный провайдер
    Поддерживает fallback между провайдерами
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.provider_configs: Dict[str, AIProviderConfig] = {}
        self.active_provider: Optional[str] = None
        self._load_providers()
    
    def _load_providers(self):
        """Загрузка всех доступных провайдеров"""
        provider_classes = {
            AIProviderType.GROQ: GroqProvider,
            AIProviderType.TOGETHER: TogetherProvider,
            AIProviderType.HUGGINGFACE: HuggingFaceProvider,
            AIProviderType.OLLAMA: OllamaProvider,
            AIProviderType.COHERE: CohereProvider,
            AIProviderType.OPENROUTER: OpenRouterProvider,
            AIProviderType.DEEPSEEK: DeepSeekProvider,
        }
        
        for name, config in FREE_AI_PROVIDERS.items():
            if config.provider_type in provider_classes:
                provider_class = provider_classes[config.provider_type]
                self.providers[name] = provider_class(config)
                self.provider_configs[name] = config
                logger.info(f"Loaded provider: {config.name}")
    
    def add_provider(self, name: str, config: AIProviderConfig):
        """Добавление нового провайдера"""
        provider_classes = {
            AIProviderType.GROQ: GroqProvider,
            AIProviderType.TOGETHER: TogetherProvider,
            AIProviderType.HUGGINGFACE: HuggingFaceProvider,
            AIProviderType.OLLAMA: OllamaProvider,
            AIProviderType.COHERE: CohereProvider,
            AIProviderType.OPENROUTER: OpenRouterProvider,
            AIProviderType.DEEPSEEK: DeepSeekProvider,
        }
        
        if config.provider_type in provider_classes:
            provider_class = provider_classes[config.provider_type]
            self.providers[name] = provider_class(config)
            self.provider_configs[name] = config
            logger.info(f"Added provider: {config.name}")
    
    def set_api_key(self, provider_name: str, api_key: str):
        """Установка API ключа для провайдера"""
        if provider_name in self.providers:
            self.providers[provider_name].api_key = api_key
            logger.info(f"API key set for {provider_name}")
    
    def get_available_providers(self) -> List[str]:
        """Получение списка доступных провайдеров"""
        return list(self.providers.keys())
    
    def get_free_providers(self) -> List[str]:
        """Получение списка бесплатных провайдеров"""
        return [name for name, config in self.provider_configs.items() if config.is_free]
    
    async def get_best_provider(self) -> Optional[str]:
        """Выбор лучшего доступного провайдера по приоритету"""
        # Сортируем по приоритету
        sorted_providers = sorted(
            self.provider_configs.items(),
            key=lambda x: x[1].priority
        )
        
        for name, config in sorted_providers:
            if config.enabled and name in self.providers:
                provider = self.providers[name]
                if await provider.is_available():
                    return name
        
        return None
    
    async def generate(self, prompt: str, system_prompt: str = "", 
                       provider_name: Optional[str] = None, **kwargs) -> str:
        """
        Генерация текста с автоматическим fallback
        """
        if provider_name and provider_name in self.providers:
            providers_to_try = [provider_name]
        else:
            # Сортируем по приоритету
            providers_to_try = sorted(
                [n for n, c in self.provider_configs.items() if c.enabled],
                key=lambda x: self.provider_configs[x].priority
            )
        
        last_error = None
        for name in providers_to_try:
            try:
                provider = self.providers[name]
                result = await provider.generate(prompt, system_prompt, **kwargs)
                self.active_provider = name
                logger.info(f"Generated with {name}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {name} failed: {e}")
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    async def chat(self, messages: List[Dict[str, str]], 
                   provider_name: Optional[str] = None, **kwargs) -> str:
        """
        Чат с автоматическим fallback
        """
        if provider_name and provider_name in self.providers:
            providers_to_try = [provider_name]
        else:
            providers_to_try = sorted(
                [n for n, c in self.provider_configs.items() if c.enabled],
                key=lambda x: self.provider_configs[x].priority
            )
        
        last_error = None
        for name in providers_to_try:
            try:
                provider = self.providers[name]
                result = await provider.chat(messages, **kwargs)
                self.active_provider = name
                logger.info(f"Chat completed with {name}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {name} failed: {e}")
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    def get_provider_info(self) -> List[Dict[str, Any]]:
        """Получение информации о всех провайдерах"""
        info = []
        for name, config in self.provider_configs.items():
            info.append({
                "name": name,
                "display_name": config.name,
                "type": config.provider_type.value,
                "model": config.model,
                "is_free": config.is_free,
                "rate_limit": config.rate_limit,
                "max_tokens": config.max_tokens,
                "enabled": config.enabled,
                "priority": config.priority,
                "has_api_key": bool(self.providers[name].api_key) if name in self.providers else False
            })
        return sorted(info, key=lambda x: x["priority"])


# Глобальный экземпляр менеджера
ai_manager = AIProviderManager()


# Функции для удобного использования
async def generate_text(prompt: str, system_prompt: str = "", **kwargs) -> str:
    """Генерация текста через лучший доступный провайдер"""
    return await ai_manager.generate(prompt, system_prompt, **kwargs)


async def chat_completion(messages: List[Dict[str, str]], **kwargs) -> str:
    """Чат через лучший доступный провайдер"""
    return await ai_manager.chat(messages, **kwargs)


def get_available_providers() -> List[str]:
    """Получение списка доступных провайдеров"""
    return ai_manager.get_available_providers()


def get_provider_info() -> List[Dict[str, Any]]:
    """Получение информации о провайдерах"""
    return ai_manager.get_provider_info()
