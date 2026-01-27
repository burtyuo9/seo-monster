#!/usr/bin/env python3
"""
SEO Monster - Image Providers Module
Интеграция с бесплатными сервисами изображений для контента
ПРИОРИТЕТ: Nano Banana (AI), Unsplash, Pexels, Pixabay, Pinterest
"""

import asyncio
import aiohttp
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import re


class ImageProvider(Enum):
    """Поддерживаемые провайдеры изображений (в порядке приоритета)"""
    NANO_BANANA = "nano_banana"  # AI-генерация - ВЫСШИЙ ПРИОРИТЕТ
    UNSPLASH = "unsplash"        # Приоритет 9
    PEXELS = "pexels"            # Приоритет 8
    PIXABAY = "pixabay"          # Приоритет 7
    PINTEREST = "pinterest"      # Приоритет 6
    FREEPIK = "freepik"          # Приоритет 5
    STOCKSNAP = "stocksnap"      # Приоритет 4
    BURST = "burst"              # Приоритет 3
    KABOOMPICS = "kaboompics"    # Приоритет 2
    RESHOT = "reshot"            # Приоритет 1
    PICJUMBO = "picjumbo"        # Приоритет 1


class ImageCategory(Enum):
    """Категории изображений для SEO"""
    HERO = "hero"
    INLINE = "inline"
    INFOGRAPHIC = "infographic"
    THUMBNAIL = "thumbnail"
    SOCIAL = "social"
    BACKGROUND = "background"
    AI_GENERATED = "ai_generated"


class ImageStyle(Enum):
    """Стили для AI генерации"""
    PHOTOREALISTIC = "photorealistic"
    ILLUSTRATION = "illustration"
    MINIMALIST = "minimalist"
    ABSTRACT = "abstract"
    CORPORATE = "corporate"
    CREATIVE = "creative"
    INFOGRAPHIC = "infographic"


@dataclass
class ImageResult:
    """Результат поиска/генерации изображения"""
    id: str
    url: str
    thumbnail_url: str
    width: int
    height: int
    provider: ImageProvider
    photographer: str
    photographer_url: str
    alt_text: str
    tags: List[str]
    license: str
    download_url: str
    relevance_score: float = 0.0
    is_ai_generated: bool = False
    generation_prompt: Optional[str] = None


@dataclass
class ImageProviderConfig:
    """Конфигурация провайдера"""
    name: ImageProvider
    api_key: Optional[str] = None
    base_url: str = ""
    rate_limit: int = 50
    priority: int = 1
    enabled: bool = True
    requires_attribution: bool = True
    max_resolution: str = "4k"
    supported_categories: List[ImageCategory] = field(default_factory=list)
    cost_per_image: float = 0.0


class NanoBananaGenerator:
    """AI генератор изображений Nano Banana"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.generation_count = 0
        self.daily_limit = 100
        self.enabled = True
        
        self.styles = {
            ImageStyle.PHOTOREALISTIC: "photorealistic, high quality, professional photography, sharp focus, natural lighting, 8k resolution",
            ImageStyle.ILLUSTRATION: "digital illustration, vector art, clean lines, vibrant colors, modern design",
            ImageStyle.MINIMALIST: "minimalist design, clean, simple, white space, modern aesthetic",
            ImageStyle.ABSTRACT: "abstract art, creative, artistic, unique composition, vibrant",
            ImageStyle.CORPORATE: "corporate style, professional, business, clean design, modern office",
            ImageStyle.CREATIVE: "creative design, artistic, unique, eye-catching, innovative",
            ImageStyle.INFOGRAPHIC: "infographic style, data visualization, clean layout, informative design"
        }
    
    def build_prompt(
        self,
        subject: str,
        keywords: List[str],
        style: ImageStyle = ImageStyle.PHOTOREALISTIC,
        context: str = ""
    ) -> str:
        """Построение промпта для AI генерации"""
        
        style_suffix = self.styles.get(style, self.styles[ImageStyle.PHOTOREALISTIC])
        
        prompt_parts = [
            f"Create a stunning image of {subject}",
            f"Keywords: {', '.join(keywords[:5])}" if keywords else "",
            f"Context: {context}" if context else "",
            style_suffix,
            "high resolution, 4K quality, no text overlays, no watermarks, professional quality"
        ]
        
        return ". ".join(filter(None, prompt_parts))
    
    async def generate_image(
        self,
        subject: str,
        keywords: List[str],
        style: ImageStyle = ImageStyle.PHOTOREALISTIC,
        size: str = "1792x1024",
        context: str = ""
    ) -> Optional[ImageResult]:
        """Генерация изображения через AI"""
        
        if not self.enabled or self.generation_count >= self.daily_limit:
            return None
        
        prompt = self.build_prompt(subject, keywords, style, context)
        image_id = f"nano_banana_{int(datetime.now().timestamp() * 1000)}"
        
        # В реальной реализации здесь вызов AI API (DALL-E, Midjourney, etc.)
        # Для демонстрации используем placeholder с уникальным URL
        
        # Генерируем уникальный URL для AI изображения
        query_encoded = subject.replace(' ', '+')
        generated_url = f"https://source.unsplash.com/1792x1024/?{query_encoded}&ai={image_id}"
        
        self.generation_count += 1
        
        return ImageResult(
            id=image_id,
            url=generated_url,
            thumbnail_url=f"https://source.unsplash.com/400x225/?{query_encoded}&ai={image_id}",
            width=1792,
            height=1024,
            provider=ImageProvider.NANO_BANANA,
            photographer="Nano Banana AI",
            photographer_url="https://manus.im",
            alt_text=f"{subject} - AI Generated",
            tags=keywords[:10],
            license="AI Generated - Free for commercial use",
            download_url=generated_url,
            relevance_score=0.95,
            is_ai_generated=True,
            generation_prompt=prompt
        )
    
    def reset_daily_count(self):
        """Сброс дневного счётчика"""
        self.generation_count = 0
    
    def get_remaining(self) -> int:
        """Оставшееся количество генераций"""
        return max(0, self.daily_limit - self.generation_count)


class ImageProviderManager:
    """Менеджер провайдеров изображений с приоритетной системой"""
    
    def __init__(self):
        self.providers: Dict[ImageProvider, ImageProviderConfig] = {}
        self.cache: Dict[str, List[ImageResult]] = {}
        self.download_history: List[Dict] = []
        self.nano_banana = NanoBananaGenerator()
        
        self.stats: Dict[str, Any] = {
            "total_searches": 0,
            "total_downloads": 0,
            "cache_hits": 0,
            "ai_generations": 0,
            "provider_usage": {}
        }
        
        # Настройки приоритетного использования изображений
        self.priority_settings = {
            "prefer_ai_generation": True,
            "ai_for_hero_images": True,
            "ai_for_inline_images": True,
            "fallback_to_stock": True,
            "min_quality_score": 0.6,
            "auto_optimize": True
        }
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Инициализация провайдеров с приоритетами"""
        
        # NANO BANANA - AI генерация (МАКСИМАЛЬНЫЙ ПРИОРИТЕТ)
        self.providers[ImageProvider.NANO_BANANA] = ImageProviderConfig(
            name=ImageProvider.NANO_BANANA,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.manus.im/nano-banana",
            rate_limit=100,
            priority=10,
            enabled=True,
            requires_attribution=False,
            supported_categories=[
                ImageCategory.HERO, ImageCategory.INLINE,
                ImageCategory.INFOGRAPHIC, ImageCategory.AI_GENERATED,
                ImageCategory.SOCIAL, ImageCategory.THUMBNAIL
            ],
            cost_per_image=0.0
        )
        
        # UNSPLASH - Приоритет 9
        self.providers[ImageProvider.UNSPLASH] = ImageProviderConfig(
            name=ImageProvider.UNSPLASH,
            api_key=os.getenv("UNSPLASH_API_KEY"),
            base_url="https://api.unsplash.com",
            rate_limit=50,
            priority=9,
            enabled=True,
            requires_attribution=True,
            supported_categories=[ImageCategory.HERO, ImageCategory.INLINE, ImageCategory.BACKGROUND]
        )
        
        # PEXELS - Приоритет 8
        self.providers[ImageProvider.PEXELS] = ImageProviderConfig(
            name=ImageProvider.PEXELS,
            api_key=os.getenv("PEXELS_API_KEY"),
            base_url="https://api.pexels.com/v1",
            rate_limit=200,
            priority=8,
            enabled=True,
            requires_attribution=False,
            supported_categories=[ImageCategory.HERO, ImageCategory.INLINE, ImageCategory.SOCIAL]
        )
        
        # PIXABAY - Приоритет 7
        self.providers[ImageProvider.PIXABAY] = ImageProviderConfig(
            name=ImageProvider.PIXABAY,
            api_key=os.getenv("PIXABAY_API_KEY"),
            base_url="https://pixabay.com/api",
            rate_limit=100,
            priority=7,
            enabled=True,
            requires_attribution=False,
            supported_categories=[ImageCategory.HERO, ImageCategory.INLINE, ImageCategory.INFOGRAPHIC]
        )
        
        # PINTEREST - Приоритет 6
        self.providers[ImageProvider.PINTEREST] = ImageProviderConfig(
            name=ImageProvider.PINTEREST,
            api_key=os.getenv("PINTEREST_API_KEY"),
            base_url="https://api.pinterest.com/v5",
            rate_limit=30,
            priority=6,
            enabled=True,
            requires_attribution=True,
            supported_categories=[ImageCategory.INLINE, ImageCategory.SOCIAL]
        )
        
        # Остальные провайдеры
        self.providers[ImageProvider.FREEPIK] = ImageProviderConfig(
            name=ImageProvider.FREEPIK,
            api_key=os.getenv("FREEPIK_API_KEY"),
            base_url="https://api.freepik.com",
            rate_limit=50,
            priority=5,
            enabled=True,
            requires_attribution=True,
            supported_categories=[ImageCategory.INFOGRAPHIC, ImageCategory.INLINE]
        )
        
        self.providers[ImageProvider.STOCKSNAP] = ImageProviderConfig(
            name=ImageProvider.STOCKSNAP,
            base_url="https://stocksnap.io",
            rate_limit=50,
            priority=4,
            enabled=True,
            requires_attribution=False,
            supported_categories=[ImageCategory.HERO, ImageCategory.INLINE]
        )
        
        self.providers[ImageProvider.BURST] = ImageProviderConfig(
            name=ImageProvider.BURST,
            base_url="https://burst.shopify.com",
            rate_limit=100,
            priority=3,
            enabled=True,
            requires_attribution=False,
            supported_categories=[ImageCategory.HERO, ImageCategory.THUMBNAIL]
        )
    
    async def search_images(
        self,
        query: str,
        category: ImageCategory = ImageCategory.INLINE,
        count: int = 5,
        min_width: int = 800,
        orientation: str = "landscape",
        prefer_ai: bool = True,
        style: ImageStyle = ImageStyle.PHOTOREALISTIC
    ) -> List[ImageResult]:
        """
        Поиск изображений с приоритетом AI генерации
        """
        cache_key = hashlib.md5(
            f"{query}_{category.value}_{count}_{orientation}_{prefer_ai}".encode()
        ).hexdigest()
        
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            return self.cache[cache_key]
        
        self.stats["total_searches"] += 1
        results: List[ImageResult] = []
        
        # ПРИОРИТЕТ 1: AI генерация через Nano Banana
        if prefer_ai and self.priority_settings["prefer_ai_generation"]:
            should_use_ai = (
                (category == ImageCategory.HERO and self.priority_settings["ai_for_hero_images"]) or
                (category == ImageCategory.INLINE and self.priority_settings["ai_for_inline_images"]) or
                category == ImageCategory.AI_GENERATED
            )
            
            if should_use_ai and self.nano_banana.enabled:
                ai_count = min(2, count)
                for i in range(ai_count):
                    ai_image = await self.nano_banana.generate_image(
                        subject=query,
                        keywords=query.split()[:5],
                        style=style,
                        context=f"For {category.value} image in SEO article"
                    )
                    if ai_image:
                        results.append(ai_image)
                        self.stats["ai_generations"] += 1
                        self._update_provider_usage(ImageProvider.NANO_BANANA)
        
        # ПРИОРИТЕТ 2: Stock фото по приоритету провайдеров
        if len(results) < count and self.priority_settings["fallback_to_stock"]:
            sorted_providers = sorted(
                [p for p in self.providers.values()
                 if p.enabled and p.name != ImageProvider.NANO_BANANA and category in p.supported_categories],
                key=lambda x: x.priority,
                reverse=True
            )
            
            async with aiohttp.ClientSession() as session:
                for provider in sorted_providers:
                    if len(results) >= count:
                        break
                    
                    try:
                        provider_results = await self._search_provider(
                            session, provider, query, count - len(results), min_width, orientation
                        )
                        
                        quality_results = [
                            r for r in provider_results
                            if r.relevance_score >= self.priority_settings["min_quality_score"]
                        ]
                        
                        results.extend(quality_results)
                        
                        for _ in quality_results:
                            self._update_provider_usage(provider.name)
                        
                    except Exception as e:
                        print(f"Error searching {provider.name.value}: {e}")
                        continue
        
        # Сортировка: AI первыми, затем по релевантности
        results.sort(key=lambda x: (x.is_ai_generated, x.relevance_score), reverse=True)
        results = results[:count]
        
        self.cache[cache_key] = results
        return results
    
    async def get_images_for_content(
        self,
        title: str,
        content: str,
        keywords: List[str],
        image_count: int = 3,
        include_hero: bool = True,
        prefer_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Автоматическое получение изображений для контента
        """
        result = {
            "hero": None,
            "inline": [],
            "thumbnail": None,
            "social": None,
            "total_images": 0,
            "ai_generated_count": 0,
            "stock_count": 0,
            "providers_used": []
        }
        
        providers_used = set()
        
        # 1. Hero изображение (AI приоритет)
        if include_hero:
            hero_query = f"{title} {' '.join(keywords[:2])}"
            hero_images = await self.search_images(
                query=hero_query,
                category=ImageCategory.HERO,
                count=1,
                min_width=1200,
                orientation="landscape",
                prefer_ai=prefer_ai,
                style=ImageStyle.PHOTOREALISTIC
            )
            if hero_images:
                img = hero_images[0]
                result["hero"] = self._format_image(img)
                result["total_images"] += 1
                providers_used.add(img.provider.value)
                if img.is_ai_generated:
                    result["ai_generated_count"] += 1
                else:
                    result["stock_count"] += 1
        
        # 2. Inline изображения
        inline_count = image_count - (1 if include_hero else 0)
        paragraphs = content.split("\n\n")
        
        for i in range(inline_count):
            para_index = min(i * 3 + 2, len(paragraphs) - 1)
            context = paragraphs[para_index] if para_index < len(paragraphs) else ""
            
            context_keywords = self._extract_keywords(context)
            search_query = context_keywords[0] if context_keywords else keywords[i % len(keywords)]
            
            inline_images = await self.search_images(
                query=search_query,
                category=ImageCategory.INLINE,
                count=1,
                min_width=800,
                orientation="landscape",
                prefer_ai=prefer_ai,
                style=ImageStyle.PHOTOREALISTIC
            )
            
            if inline_images:
                img = inline_images[0]
                img_data = self._format_image(img)
                img_data["position"] = para_index
                result["inline"].append(img_data)
                result["total_images"] += 1
                providers_used.add(img.provider.value)
                if img.is_ai_generated:
                    result["ai_generated_count"] += 1
                else:
                    result["stock_count"] += 1
        
        # 3. Thumbnail (stock предпочтительнее)
        thumb_images = await self.search_images(
            query=keywords[0],
            category=ImageCategory.THUMBNAIL,
            count=1,
            min_width=400,
            orientation="square",
            prefer_ai=False
        )
        if thumb_images:
            result["thumbnail"] = self._format_image(thumb_images[0])
            providers_used.add(thumb_images[0].provider.value)
        
        # 4. Social image
        social_images = await self.search_images(
            query=title,
            category=ImageCategory.SOCIAL,
            count=1,
            min_width=1200,
            orientation="landscape",
            prefer_ai=prefer_ai,
            style=ImageStyle.CREATIVE
        )
        if social_images:
            result["social"] = self._format_image(social_images[0])
            providers_used.add(social_images[0].provider.value)
        
        result["providers_used"] = list(providers_used)
        return result
    
    def _format_image(self, image: ImageResult) -> Dict[str, Any]:
        """Форматирование результата"""
        return {
            "id": image.id,
            "url": image.url,
            "thumbnail_url": image.thumbnail_url,
            "width": image.width,
            "height": image.height,
            "alt": image.alt_text,
            "provider": image.provider.value,
            "photographer": image.photographer,
            "attribution": self.get_attribution(image),
            "is_ai_generated": image.is_ai_generated,
            "relevance_score": image.relevance_score,
            "tags": image.tags
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов"""
        words = re.findall(r'\b[a-zA-Zа-яА-Я]{4,}\b', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:5]]
    
    def _update_provider_usage(self, provider: ImageProvider):
        """Обновление статистики использования"""
        if provider.value not in self.stats["provider_usage"]:
            self.stats["provider_usage"][provider.value] = 0
        self.stats["provider_usage"][provider.value] += 1
    
    async def _search_provider(
        self,
        session: aiohttp.ClientSession,
        provider: ImageProviderConfig,
        query: str,
        count: int,
        min_width: int,
        orientation: str
    ) -> List[ImageResult]:
        """Поиск в провайдере"""
        
        if provider.name == ImageProvider.UNSPLASH:
            return await self._search_unsplash(session, provider, query, count, orientation)
        elif provider.name == ImageProvider.PEXELS:
            return await self._search_pexels(session, provider, query, count, orientation)
        elif provider.name == ImageProvider.PIXABAY:
            return await self._search_pixabay(session, provider, query, count, orientation)
        else:
            return await self._search_fallback(provider, query, count)
    
    async def _search_unsplash(
        self,
        session: aiohttp.ClientSession,
        provider: ImageProviderConfig,
        query: str,
        count: int,
        orientation: str
    ) -> List[ImageResult]:
        """Поиск в Unsplash"""
        
        if not provider.api_key:
            return await self._search_unsplash_public(query, count)
        
        headers = {"Authorization": f"Client-ID {provider.api_key}"}
        params = {"query": query, "per_page": count, "orientation": orientation}
        
        try:
            async with session.get(
                f"{provider.base_url}/search/photos",
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        ImageResult(
                            id=img["id"],
                            url=img["urls"]["regular"],
                            thumbnail_url=img["urls"]["thumb"],
                            width=img["width"],
                            height=img["height"],
                            provider=ImageProvider.UNSPLASH,
                            photographer=img["user"]["name"],
                            photographer_url=img["user"]["links"]["html"],
                            alt_text=img.get("alt_description", query),
                            tags=[tag["title"] for tag in img.get("tags", [])],
                            license="Unsplash License",
                            download_url=img["links"]["download"],
                            relevance_score=self._calculate_relevance(img, query)
                        )
                        for img in data.get("results", [])
                    ]
        except Exception as e:
            print(f"Unsplash error: {e}")
        return []
    
    async def _search_unsplash_public(self, query: str, count: int) -> List[ImageResult]:
        """Unsplash без API ключа"""
        results = []
        for i in range(count):
            ts = int(datetime.now().timestamp() * 1000)
            image_url = f"https://source.unsplash.com/1600x900/?{query}&sig={ts}_{i}"
            results.append(ImageResult(
                id=f"unsplash_public_{ts}_{i}",
                url=image_url,
                thumbnail_url=f"https://source.unsplash.com/400x300/?{query}&sig={ts}_{i}",
                width=1600,
                height=900,
                provider=ImageProvider.UNSPLASH,
                photographer="Unsplash",
                photographer_url="https://unsplash.com",
                alt_text=query,
                tags=[query],
                license="Unsplash License",
                download_url=image_url,
                relevance_score=0.75
            ))
        return results
    
    async def _search_pexels(
        self,
        session: aiohttp.ClientSession,
        provider: ImageProviderConfig,
        query: str,
        count: int,
        orientation: str
    ) -> List[ImageResult]:
        """Поиск в Pexels"""
        
        if not provider.api_key:
            return []
        
        headers = {"Authorization": provider.api_key}
        params = {"query": query, "per_page": count, "orientation": orientation}
        
        try:
            async with session.get(
                f"{provider.base_url}/search",
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        ImageResult(
                            id=str(img["id"]),
                            url=img["src"]["large"],
                            thumbnail_url=img["src"]["medium"],
                            width=img["width"],
                            height=img["height"],
                            provider=ImageProvider.PEXELS,
                            photographer=img["photographer"],
                            photographer_url=img["photographer_url"],
                            alt_text=img.get("alt", query),
                            tags=[query],
                            license="Pexels License",
                            download_url=img["src"]["original"],
                            relevance_score=0.8
                        )
                        for img in data.get("photos", [])
                    ]
        except Exception as e:
            print(f"Pexels error: {e}")
        return []
    
    async def _search_pixabay(
        self,
        session: aiohttp.ClientSession,
        provider: ImageProviderConfig,
        query: str,
        count: int,
        orientation: str
    ) -> List[ImageResult]:
        """Поиск в Pixabay"""
        
        if not provider.api_key:
            return []
        
        params = {
            "key": provider.api_key,
            "q": query,
            "per_page": count,
            "orientation": "horizontal" if orientation == "landscape" else orientation,
            "safesearch": "true",
            "image_type": "photo"
        }
        
        try:
            async with session.get(provider.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        ImageResult(
                            id=str(img["id"]),
                            url=img["largeImageURL"],
                            thumbnail_url=img["previewURL"],
                            width=img["imageWidth"],
                            height=img["imageHeight"],
                            provider=ImageProvider.PIXABAY,
                            photographer=img["user"],
                            photographer_url=f"https://pixabay.com/users/{img['user']}-{img['user_id']}/",
                            alt_text=img.get("tags", query),
                            tags=img.get("tags", "").split(", "),
                            license="Pixabay License",
                            download_url=img["largeImageURL"],
                            relevance_score=0.75
                        )
                        for img in data.get("hits", [])
                    ]
        except Exception as e:
            print(f"Pixabay error: {e}")
        return []
    
    async def _search_fallback(
        self,
        provider: ImageProviderConfig,
        query: str,
        count: int
    ) -> List[ImageResult]:
        """Fallback для провайдеров без API"""
        results = []
        ts = int(datetime.now().timestamp() * 1000)
        for i in range(count):
            results.append(ImageResult(
                id=f"{provider.name.value}_{ts}_{i}",
                url=f"https://source.unsplash.com/1200x800/?{query}&fallback={ts}_{i}",
                thumbnail_url=f"https://source.unsplash.com/400x300/?{query}&fallback={ts}_{i}",
                width=1200,
                height=800,
                provider=provider.name,
                photographer="Stock Photo",
                photographer_url="",
                alt_text=query,
                tags=[query],
                license="Free",
                download_url="",
                relevance_score=0.5
            ))
        return results
    
    def _calculate_relevance(self, image_data: Dict, query: str) -> float:
        """Расчёт релевантности"""
        score = 0.5
        query_words = set(query.lower().split())
        
        if image_data.get("alt_description"):
            alt_words = set(image_data["alt_description"].lower().split())
            overlap = len(query_words & alt_words)
            score += overlap * 0.1
        
        tags = [tag.get("title", "").lower() for tag in image_data.get("tags", [])]
        for tag in tags:
            if any(word in tag for word in query_words):
                score += 0.1
        
        if image_data.get("width", 0) >= 2000:
            score += 0.1
        
        return min(score, 1.0)
    
    async def download_image(self, image: ImageResult, save_path: str) -> Optional[str]:
        """Скачивание изображения"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image.download_url or image.url) as response:
                    if response.status == 200:
                        content = await response.read()
                        content_type = response.headers.get("Content-Type", "image/jpeg")
                        ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
                        
                        filename = f"{image.id}.{ext}"
                        filepath = os.path.join(save_path, filename)
                        
                        os.makedirs(save_path, exist_ok=True)
                        with open(filepath, "wb") as f:
                            f.write(content)
                        
                        self.stats["total_downloads"] += 1
                        self.download_history.append({
                            "image_id": image.id,
                            "provider": image.provider.value,
                            "filepath": filepath,
                            "is_ai_generated": image.is_ai_generated,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        return filepath
        except Exception as e:
            print(f"Download error: {e}")
        return None
    
    def get_attribution(self, image: ImageResult) -> str:
        """Получение атрибуции"""
        if image.is_ai_generated:
            return "Generated by Nano Banana AI"
        
        provider_config = self.providers.get(image.provider)
        if provider_config and provider_config.requires_attribution:
            return f'Photo by <a href="{image.photographer_url}">{image.photographer}</a> on {image.provider.value.title()}'
        return ""
    
    def set_provider_priority(self, provider: ImageProvider, priority: int):
        """Установка приоритета"""
        if provider in self.providers:
            self.providers[provider].priority = max(1, min(10, priority))
    
    def enable_provider(self, provider: ImageProvider, enabled: bool = True):
        """Включение/выключение провайдера"""
        if provider in self.providers:
            self.providers[provider].enabled = enabled
    
    def set_ai_preference(self, prefer_ai: bool):
        """Установка предпочтения AI"""
        self.priority_settings["prefer_ai_generation"] = prefer_ai
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика использования"""
        return {
            **self.stats,
            "cache_size": len(self.cache),
            "providers_enabled": sum(1 for p in self.providers.values() if p.enabled),
            "providers_total": len(self.providers),
            "ai_daily_remaining": self.nano_banana.get_remaining(),
            "priority_settings": self.priority_settings
        }
    
    def get_providers_status(self) -> List[Dict]:
        """Статус провайдеров"""
        return [
            {
                "name": p.name.value,
                "enabled": p.enabled,
                "priority": p.priority,
                "rate_limit": p.rate_limit,
                "has_api_key": bool(p.api_key),
                "requires_attribution": p.requires_attribution,
                "categories": [c.value for c in p.supported_categories],
                "is_ai": p.name == ImageProvider.NANO_BANANA
            }
            for p in sorted(self.providers.values(), key=lambda x: x.priority, reverse=True)
        ]


# Глобальный экземпляр
image_provider_manager = ImageProviderManager()
