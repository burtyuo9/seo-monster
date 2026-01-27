#!/usr/bin/env python3
"""
SEO Monster - Image Content Integration
Интеграция изображений в генерацию контента с самообучением
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import re

from .image_providers import (
    ImageProviderManager, 
    ImageProvider, 
    ImageCategory, 
    ImageResult,
    ImageStyle,
    image_provider_manager
)
from .priority_system import (
    PriorityManager,
    PriorityLevel,
    TaskType,
    ResourceType,
    ResourcePriority,
    priority_manager
)


@dataclass
class ImagePerformance:
    """Метрики производительности изображения"""
    image_id: str
    provider: ImageProvider
    article_id: str
    position: str  # hero, inline_1, inline_2, etc.
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    avg_time_on_page: float = 0.0
    bounce_rate: float = 0.0
    social_shares: int = 0
    performance_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ArticleImageStats:
    """Статистика изображений в статье"""
    article_id: str
    title: str
    url: str
    images: List[ImagePerformance]
    total_impressions: int = 0
    total_clicks: int = 0
    overall_ctr: float = 0.0
    avg_time_on_page: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


class ImageLearningSystem:
    """Система самообучения для оптимизации выбора изображений"""
    
    def __init__(self):
        self.performance_data: Dict[str, ImagePerformance] = {}
        self.article_stats: Dict[str, ArticleImageStats] = {}
        self.provider_scores: Dict[ImageProvider, float] = {}
        self.category_scores: Dict[Tuple[str, ImageCategory], float] = {}
        self.keyword_image_mapping: Dict[str, List[str]] = {}
        
        # Параметры обучения
        self.learning_rate = 0.1
        self.min_samples_for_learning = 10
        self.performance_decay = 0.95  # Коэффициент затухания старых данных
        
        # Оптимальные параметры (обновляются при обучении)
        self.optimal_params = {
            "images_per_article": 3,
            "hero_image_weight": 0.4,
            "inline_image_weight": 0.3,
            "preferred_providers": [],
            "preferred_categories": {},
            "optimal_image_positions": [0, 3, 6]  # После каких абзацев
        }
        
        self._initialize_provider_scores()
    
    def _initialize_provider_scores(self):
        """Инициализация начальных scores провайдеров"""
        for provider in ImageProvider:
            self.provider_scores[provider] = 0.5  # Начальный нейтральный score
    
    def record_image_performance(
        self,
        image_id: str,
        provider: ImageProvider,
        article_id: str,
        position: str,
        metrics: Dict[str, Any]
    ):
        """Запись метрик производительности изображения"""
        
        perf = ImagePerformance(
            image_id=image_id,
            provider=provider,
            article_id=article_id,
            position=position,
            impressions=metrics.get("impressions", 0),
            clicks=metrics.get("clicks", 0),
            ctr=metrics.get("ctr", 0.0),
            avg_time_on_page=metrics.get("avg_time_on_page", 0.0),
            bounce_rate=metrics.get("bounce_rate", 0.0),
            social_shares=metrics.get("social_shares", 0)
        )
        
        # Рассчитываем performance score
        perf.performance_score = self._calculate_performance_score(perf)
        
        self.performance_data[f"{article_id}_{image_id}"] = perf
        
        # Обновляем scores провайдера
        self._update_provider_score(provider, perf.performance_score)
    
    def _calculate_performance_score(self, perf: ImagePerformance) -> float:
        """Расчёт общего score производительности"""
        
        # Нормализуем метрики
        ctr_score = min(perf.ctr / 0.05, 1.0)  # 5% CTR = максимум
        time_score = min(perf.avg_time_on_page / 180, 1.0)  # 3 минуты = максимум
        bounce_score = 1 - min(perf.bounce_rate, 1.0)  # Меньше bounce = лучше
        social_score = min(perf.social_shares / 100, 1.0)  # 100 shares = максимум
        
        # Взвешенная сумма
        score = (
            0.3 * ctr_score +
            0.3 * time_score +
            0.2 * bounce_score +
            0.2 * social_score
        )
        
        return score
    
    def _update_provider_score(self, provider: ImageProvider, new_score: float):
        """Обновление score провайдера (экспоненциальное скользящее среднее)"""
        
        current_score = self.provider_scores.get(provider, 0.5)
        updated_score = (1 - self.learning_rate) * current_score + self.learning_rate * new_score
        self.provider_scores[provider] = updated_score
    
    def get_recommended_provider(self, category: ImageCategory) -> ImageProvider:
        """Получение рекомендуемого провайдера для категории"""
        
        # Фильтруем провайдеры, поддерживающие категорию
        suitable_providers = []
        for provider in ImageProvider:
            config = image_provider_manager.providers.get(provider)
            if config and config.enabled and category in config.supported_categories:
                suitable_providers.append(provider)
        
        if not suitable_providers:
            return ImageProvider.UNSPLASH  # Fallback
        
        # Выбираем провайдера с лучшим score
        best_provider = max(
            suitable_providers,
            key=lambda p: self.provider_scores.get(p, 0.5)
        )
        
        return best_provider
    
    def learn_from_articles(self):
        """Обучение на основе накопленных данных"""
        
        if len(self.performance_data) < self.min_samples_for_learning:
            return
        
        # Анализируем данные по провайдерам
        provider_performance = defaultdict(list)
        for perf in self.performance_data.values():
            provider_performance[perf.provider].append(perf.performance_score)
        
        # Обновляем scores провайдеров
        for provider, scores in provider_performance.items():
            avg_score = sum(scores) / len(scores)
            self.provider_scores[provider] = avg_score
        
        # Определяем оптимальное количество изображений
        self._learn_optimal_image_count()
        
        # Определяем лучшие позиции для изображений
        self._learn_optimal_positions()
        
        # Обновляем приоритеты провайдеров в системе приоритетов
        self._update_provider_priorities()
    
    def _learn_optimal_image_count(self):
        """Определение оптимального количества изображений"""
        
        # Группируем статьи по количеству изображений
        articles_by_image_count = defaultdict(list)
        
        for article_id, stats in self.article_stats.items():
            image_count = len(stats.images)
            articles_by_image_count[image_count].append(stats.overall_ctr)
        
        # Находим оптимальное количество
        best_count = 3
        best_ctr = 0
        
        for count, ctrs in articles_by_image_count.items():
            if len(ctrs) >= 5:  # Минимум 5 статей для статистики
                avg_ctr = sum(ctrs) / len(ctrs)
                if avg_ctr > best_ctr:
                    best_ctr = avg_ctr
                    best_count = count
        
        self.optimal_params["images_per_article"] = best_count
    
    def _learn_optimal_positions(self):
        """Определение оптимальных позиций для изображений"""
        
        position_performance = defaultdict(list)
        
        for perf in self.performance_data.values():
            position_performance[perf.position].append(perf.performance_score)
        
        # Сортируем позиции по средней производительности
        sorted_positions = sorted(
            position_performance.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            reverse=True
        )
        
        # Извлекаем номера позиций для inline изображений
        optimal_positions = []
        for pos, _ in sorted_positions[:5]:
            if pos.startswith("inline_"):
                try:
                    pos_num = int(pos.split("_")[1])
                    optimal_positions.append(pos_num * 3)  # Конвертируем в номер абзаца
                except:
                    pass
        
        if optimal_positions:
            self.optimal_params["optimal_image_positions"] = sorted(optimal_positions)
    
    def _update_provider_priorities(self):
        """Обновление приоритетов провайдеров в системе"""
        
        # Сортируем провайдеры по score
        sorted_providers = sorted(
            self.provider_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Обновляем приоритеты (1-10)
        for i, (provider, score) in enumerate(sorted_providers):
            priority = 10 - i  # Первый получает 10, второй 9, и т.д.
            priority = max(1, min(10, priority))
            image_provider_manager.set_provider_priority(provider, priority)
        
        # Сохраняем список предпочтительных провайдеров
        self.optimal_params["preferred_providers"] = [
            p.value for p, _ in sorted_providers[:3]
        ]
    
    def get_learning_report(self) -> Dict[str, Any]:
        """Получение отчёта об обучении"""
        
        return {
            "total_samples": len(self.performance_data),
            "provider_scores": {p.value: s for p, s in self.provider_scores.items()},
            "optimal_params": self.optimal_params,
            "articles_analyzed": len(self.article_stats),
            "learning_status": "active" if len(self.performance_data) >= self.min_samples_for_learning else "collecting_data"
        }
    
    def export_model(self) -> Dict[str, Any]:
        """Экспорт обученной модели"""
        
        return {
            "provider_scores": {p.value: s for p, s in self.provider_scores.items()},
            "optimal_params": self.optimal_params,
            "category_scores": {
                f"{k[0]}_{k[1].value}": v 
                for k, v in self.category_scores.items()
            },
            "exported_at": datetime.now().isoformat()
        }
    
    def import_model(self, model_data: Dict[str, Any]):
        """Импорт обученной модели"""
        
        if "provider_scores" in model_data:
            for provider_str, score in model_data["provider_scores"].items():
                try:
                    provider = ImageProvider(provider_str)
                    self.provider_scores[provider] = score
                except ValueError:
                    pass
        
        if "optimal_params" in model_data:
            self.optimal_params.update(model_data["optimal_params"])


class SmartImageSelector:
    """Умный селектор изображений с использованием обучения"""
    
    def __init__(
        self,
        image_manager: ImageProviderManager,
        learning_system: ImageLearningSystem
    ):
        self.image_manager = image_manager
        self.learning_system = learning_system
    
    async def select_images_for_article(
        self,
        article_content: str,
        keywords: List[str],
        title: str,
        target_audience: str = "general"
    ) -> Dict[str, Any]:
        """
        Умный выбор изображений для статьи
        
        Args:
            article_content: Текст статьи
            keywords: Ключевые слова
            title: Заголовок статьи
            target_audience: Целевая аудитория
        
        Returns:
            Словарь с выбранными изображениями
        """
        
        result = {
            "hero_image": None,
            "inline_images": [],
            "thumbnail": None,
            "social_image": None,
            "attribution_required": []
        }
        
        # Определяем оптимальное количество изображений
        optimal_count = self.learning_system.optimal_params["images_per_article"]
        
        # Анализируем контент для определения тем
        content_themes = self._extract_themes(article_content, keywords)
        
        # Выбираем hero изображение
        hero_provider = self.learning_system.get_recommended_provider(ImageCategory.HERO)
        hero_images = await self.image_manager.search_images(
            query=self._build_search_query(title, keywords[:2]),
            category=ImageCategory.HERO,
            count=3,
            min_width=1200,
            orientation="landscape"
        )
        
        if hero_images:
            best_hero = self._select_best_image(hero_images, content_themes)
            result["hero_image"] = {
                "url": best_hero.url,
                "alt": self._generate_alt_text(best_hero, title),
                "attribution": self.image_manager.get_attribution(best_hero),
                "provider": best_hero.provider.value
            }
            if self.image_manager.providers[best_hero.provider].requires_attribution:
                result["attribution_required"].append(best_hero.provider.value)
        
        # Выбираем inline изображения
        optimal_positions = self.learning_system.optimal_params["optimal_image_positions"]
        paragraphs = article_content.split("\n\n")
        
        for i, pos in enumerate(optimal_positions[:optimal_count - 1]):
            if pos < len(paragraphs):
                # Извлекаем контекст из абзаца
                context = paragraphs[pos] if pos < len(paragraphs) else ""
                context_keywords = self._extract_keywords_from_text(context)
                
                search_query = self._build_search_query(
                    context_keywords[0] if context_keywords else keywords[0],
                    keywords
                )
                
                inline_images = await self.image_manager.search_images(
                    query=search_query,
                    category=ImageCategory.INLINE,
                    count=2,
                    min_width=800,
                    orientation="landscape"
                )
                
                if inline_images:
                    best_inline = self._select_best_image(inline_images, content_themes)
                    result["inline_images"].append({
                        "url": best_inline.url,
                        "alt": self._generate_alt_text(best_inline, context_keywords[0] if context_keywords else keywords[0]),
                        "attribution": self.image_manager.get_attribution(best_inline),
                        "position": pos,
                        "provider": best_inline.provider.value
                    })
        
        # Выбираем thumbnail
        thumbnail_images = await self.image_manager.search_images(
            query=keywords[0],
            category=ImageCategory.THUMBNAIL,
            count=1,
            min_width=400,
            orientation="square"
        )
        
        if thumbnail_images:
            result["thumbnail"] = {
                "url": thumbnail_images[0].thumbnail_url,
                "alt": title
            }
        
        # Выбираем изображение для соцсетей
        social_images = await self.image_manager.search_images(
            query=self._build_search_query(title, keywords[:2]),
            category=ImageCategory.SOCIAL,
            count=1,
            min_width=1200,
            orientation="landscape"
        )
        
        if social_images:
            result["social_image"] = {
                "url": social_images[0].url,
                "alt": title
            }
        
        return result
    
    def _extract_themes(self, content: str, keywords: List[str]) -> List[str]:
        """Извлечение тем из контента"""
        
        themes = list(keywords)
        
        # Простой анализ частотности слов
        words = re.findall(r'\b[a-zA-Zа-яА-Я]{4,}\b', content.lower())
        word_freq = defaultdict(int)
        
        for word in words:
            word_freq[word] += 1
        
        # Добавляем топ-5 частых слов как темы
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        themes.extend([word for word, _ in sorted_words[:5] if word not in themes])
        
        return themes[:10]
    
    def _build_search_query(self, main_term: str, keywords: List[str]) -> str:
        """Построение поискового запроса"""
        
        query_parts = [main_term]
        
        # Добавляем 1-2 ключевых слова для контекста
        for kw in keywords[:2]:
            if kw.lower() != main_term.lower():
                query_parts.append(kw)
                break
        
        return " ".join(query_parts)
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Извлечение ключевых слов из текста"""
        
        # Простое извлечение на основе частотности
        words = re.findall(r'\b[a-zA-Zа-яА-Я]{4,}\b', text.lower())
        word_freq = defaultdict(int)
        
        for word in words:
            word_freq[word] += 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:5]]
    
    def _select_best_image(
        self,
        images: List[ImageResult],
        themes: List[str]
    ) -> ImageResult:
        """Выбор лучшего изображения на основе релевантности и качества"""
        
        scored_images = []
        
        for img in images:
            score = img.relevance_score
            
            # Бонус за совпадение с темами
            for theme in themes:
                if theme.lower() in img.alt_text.lower():
                    score += 0.1
                for tag in img.tags:
                    if theme.lower() in tag.lower():
                        score += 0.05
            
            # Бонус за качество (разрешение)
            if img.width >= 1920:
                score += 0.1
            elif img.width >= 1200:
                score += 0.05
            
            # Учитываем score провайдера из системы обучения
            provider_score = self.learning_system.provider_scores.get(img.provider, 0.5)
            score *= (0.5 + provider_score * 0.5)
            
            scored_images.append((score, img))
        
        scored_images.sort(key=lambda x: x[0], reverse=True)
        return scored_images[0][1]
    
    def _generate_alt_text(self, image: ImageResult, context: str) -> str:
        """Генерация SEO-оптимизированного alt текста"""
        
        if image.alt_text and len(image.alt_text) > 10:
            return f"{context}: {image.alt_text}"
        
        return f"{context} - {image.provider.value.title()} image"


class ArticleImageEnricher:
    """Обогащение статей изображениями"""
    
    def __init__(self):
        self.image_manager = image_provider_manager
        self.learning_system = ImageLearningSystem()
        self.smart_selector = SmartImageSelector(self.image_manager, self.learning_system)
    
    async def enrich_article(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обогащение статьи изображениями
        
        Args:
            article: Словарь с данными статьи (title, content, keywords)
        
        Returns:
            Обновлённая статья с изображениями
        """
        
        title = article.get("title", "")
        content = article.get("content", "")
        keywords = article.get("keywords", [])
        
        # Получаем изображения
        images = await self.smart_selector.select_images_for_article(
            article_content=content,
            keywords=keywords,
            title=title
        )
        
        # Добавляем изображения в статью
        article["images"] = images
        
        # Вставляем изображения в HTML контент
        if images["hero_image"]:
            hero_html = self._generate_image_html(
                images["hero_image"],
                css_class="hero-image"
            )
            article["hero_html"] = hero_html
        
        # Генерируем HTML для inline изображений
        inline_html_list = []
        for img_data in images["inline_images"]:
            inline_html = self._generate_image_html(
                img_data,
                css_class="inline-image"
            )
            inline_html_list.append({
                "html": inline_html,
                "position": img_data["position"]
            })
        article["inline_images_html"] = inline_html_list
        
        # Генерируем Open Graph теги
        article["og_tags"] = self._generate_og_tags(article, images)
        
        return article
    
    def _generate_image_html(
        self,
        image_data: Dict[str, Any],
        css_class: str = ""
    ) -> str:
        """Генерация HTML для изображения"""
        
        html = f'''
<figure class="{css_class}">
    <img src="{image_data['url']}" 
         alt="{image_data['alt']}" 
         loading="lazy"
         class="responsive-image">
'''
        
        if image_data.get("attribution"):
            html += f'''    <figcaption class="image-attribution">
        {image_data['attribution']}
    </figcaption>
'''
        
        html += '</figure>'
        return html
    
    def _generate_og_tags(
        self,
        article: Dict[str, Any],
        images: Dict[str, Any]
    ) -> Dict[str, str]:
        """Генерация Open Graph тегов"""
        
        og_tags = {
            "og:title": article.get("title", ""),
            "og:type": "article",
            "og:description": article.get("meta_description", "")[:200]
        }
        
        if images.get("social_image"):
            og_tags["og:image"] = images["social_image"]["url"]
            og_tags["og:image:alt"] = images["social_image"]["alt"]
        elif images.get("hero_image"):
            og_tags["og:image"] = images["hero_image"]["url"]
            og_tags["og:image:alt"] = images["hero_image"]["alt"]
        
        return og_tags
    
    def record_article_performance(
        self,
        article_id: str,
        performance_data: Dict[str, Any]
    ):
        """Запись данных о производительности статьи для обучения"""
        
        # Записываем метрики для каждого изображения
        for img_perf in performance_data.get("image_performance", []):
            self.learning_system.record_image_performance(
                image_id=img_perf["image_id"],
                provider=ImageProvider(img_perf["provider"]),
                article_id=article_id,
                position=img_perf["position"],
                metrics=img_perf["metrics"]
            )
        
        # Запускаем обучение
        self.learning_system.learn_from_articles()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        
        return {
            "image_provider_stats": self.image_manager.get_stats(),
            "learning_report": self.learning_system.get_learning_report(),
            "providers_status": self.image_manager.get_providers_status()
        }


# Глобальный экземпляр
article_image_enricher = ArticleImageEnricher()
