#!/usr/bin/env python3
"""
SEO Monster - Smart Image Decision System
Умная система принятия решений об использовании изображений
Изображения добавляются ТОЛЬКО когда это улучшит конверсию
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class ContentType(Enum):
    """Типы контента"""
    PRODUCT_REVIEW = "product_review"      # Обзоры товаров - НУЖНЫ изображения
    TUTORIAL = "tutorial"                   # Инструкции - НУЖНЫ изображения
    HOW_TO = "how_to"                       # Как сделать - НУЖНЫ изображения
    TRAVEL = "travel"                       # Путешествия - НУЖНЫ изображения
    FOOD_RECIPE = "food_recipe"             # Рецепты - НУЖНЫ изображения
    FASHION = "fashion"                     # Мода - НУЖНЫ изображения
    REAL_ESTATE = "real_estate"             # Недвижимость - НУЖНЫ изображения
    ECOMMERCE = "ecommerce"                 # Товары - НУЖНЫ изображения
    NEWS = "news"                           # Новости - ОПЦИОНАЛЬНО
    TECHNICAL = "technical"                 # Технические статьи - ОПЦИОНАЛЬНО
    LEGAL = "legal"                         # Юридические - НЕ НУЖНЫ
    FINANCIAL = "financial"                 # Финансовые - НЕ НУЖНЫ
    ACADEMIC = "academic"                   # Академические - НЕ НУЖНЫ
    GENERAL = "general"                     # Общие - АНАЛИЗ НУЖЕН


class ImageNecessity(Enum):
    """Уровень необходимости изображений"""
    REQUIRED = "required"           # Обязательно нужны
    RECOMMENDED = "recommended"     # Рекомендуется
    OPTIONAL = "optional"           # Опционально
    NOT_NEEDED = "not_needed"       # Не нужны


@dataclass
class ImageDecision:
    """Решение об использовании изображений"""
    should_use_images: bool
    necessity_level: ImageNecessity
    recommended_count: int
    hero_image: bool
    inline_images: int
    reasons: List[str]
    confidence_score: float  # 0-1
    content_type: ContentType
    conversion_impact_estimate: float  # Оценка влияния на конверсию


@dataclass
class ArticlePerformance:
    """Данные о производительности статьи"""
    article_id: str
    has_images: bool
    image_count: int
    content_type: ContentType
    keywords: List[str]
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    conversions: int = 0
    conversion_rate: float = 0.0
    avg_time_on_page: float = 0.0
    bounce_rate: float = 0.0


class SmartImageDecisionSystem:
    """Система умного принятия решений об изображениях"""
    
    def __init__(self):
        # Исторические данные для обучения
        self.performance_history: List[ArticlePerformance] = []
        
        # Правила для типов контента
        self.content_type_rules = {
            ContentType.PRODUCT_REVIEW: ImageNecessity.REQUIRED,
            ContentType.TUTORIAL: ImageNecessity.REQUIRED,
            ContentType.HOW_TO: ImageNecessity.REQUIRED,
            ContentType.TRAVEL: ImageNecessity.REQUIRED,
            ContentType.FOOD_RECIPE: ImageNecessity.REQUIRED,
            ContentType.FASHION: ImageNecessity.REQUIRED,
            ContentType.REAL_ESTATE: ImageNecessity.REQUIRED,
            ContentType.ECOMMERCE: ImageNecessity.REQUIRED,
            ContentType.NEWS: ImageNecessity.OPTIONAL,
            ContentType.TECHNICAL: ImageNecessity.OPTIONAL,
            ContentType.LEGAL: ImageNecessity.NOT_NEEDED,
            ContentType.FINANCIAL: ImageNecessity.NOT_NEEDED,
            ContentType.ACADEMIC: ImageNecessity.NOT_NEEDED,
            ContentType.GENERAL: ImageNecessity.OPTIONAL,
        }
        
        # Ключевые слова для определения типа контента
        self.content_type_keywords = {
            ContentType.PRODUCT_REVIEW: [
                "review", "обзор", "тест", "сравнение", "лучший", "топ", 
                "рейтинг", "характеристики", "плюсы", "минусы", "отзыв"
            ],
            ContentType.TUTORIAL: [
                "tutorial", "guide", "руководство", "инструкция", "урок",
                "пошаговый", "step by step", "learn", "научиться"
            ],
            ContentType.HOW_TO: [
                "how to", "как сделать", "как настроить", "способ",
                "метод", "советы", "tips", "лайфхак"
            ],
            ContentType.TRAVEL: [
                "travel", "путешествие", "отель", "hotel", "туризм",
                "достопримечательности", "vacation", "отдых", "курорт"
            ],
            ContentType.FOOD_RECIPE: [
                "recipe", "рецепт", "готовить", "блюдо", "ингредиенты",
                "cooking", "кухня", "еда", "food"
            ],
            ContentType.FASHION: [
                "fashion", "мода", "стиль", "одежда", "outfit",
                "тренд", "look", "образ", "аксессуары"
            ],
            ContentType.REAL_ESTATE: [
                "недвижимость", "квартира", "дом", "аренда", "покупка",
                "real estate", "property", "apartment", "house"
            ],
            ContentType.ECOMMERCE: [
                "купить", "цена", "магазин", "товар", "заказать",
                "buy", "price", "shop", "product", "скидка", "sale"
            ],
            ContentType.TECHNICAL: [
                "api", "code", "программирование", "разработка", "software",
                "algorithm", "database", "server", "framework"
            ],
            ContentType.LEGAL: [
                "закон", "право", "юридический", "договор", "суд",
                "legal", "law", "contract", "attorney"
            ],
            ContentType.FINANCIAL: [
                "инвестиции", "акции", "банк", "кредит", "финансы",
                "investment", "stock", "bank", "finance", "налог"
            ],
            ContentType.ACADEMIC: [
                "исследование", "научный", "диссертация", "теория",
                "research", "academic", "study", "thesis"
            ]
        }
        
        # Визуальные ключевые слова (требуют изображений)
        self.visual_keywords = [
            "фото", "photo", "картинка", "image", "видео", "video",
            "внешний вид", "дизайн", "design", "цвет", "color",
            "размер", "size", "форма", "shape", "красивый", "beautiful",
            "стильный", "stylish", "визуальный", "visual", "смотреть", "look"
        ]
        
        # Статистика по типам контента
        self.type_conversion_stats: Dict[ContentType, Dict[str, float]] = {}
        
        # Минимальный порог улучшения конверсии для добавления изображений
        self.min_conversion_improvement = 0.05  # 5%
    
    def analyze_content(
        self,
        title: str,
        content: str,
        keywords: List[str],
        target_audience: str = "general",
        competitor_has_images: bool = False
    ) -> ImageDecision:
        """
        Анализ контента и принятие решения об использовании изображений
        
        Args:
            title: Заголовок статьи
            content: Текст статьи
            keywords: Ключевые слова
            target_audience: Целевая аудитория
            competitor_has_images: Используют ли конкуренты изображения
        
        Returns:
            ImageDecision с рекомендацией
        """
        
        # 1. Определяем тип контента
        content_type = self._detect_content_type(title, content, keywords)
        
        # 2. Получаем базовое правило для типа контента
        base_necessity = self.content_type_rules.get(content_type, ImageNecessity.OPTIONAL)
        
        # 3. Анализируем визуальные ключевые слова
        visual_score = self._calculate_visual_score(title, content, keywords)
        
        # 4. Проверяем исторические данные
        historical_impact = self._get_historical_conversion_impact(content_type, keywords)
        
        # 5. Учитываем конкурентов
        competitor_factor = 1.2 if competitor_has_images else 1.0
        
        # 6. Принимаем решение
        decision = self._make_decision(
            content_type=content_type,
            base_necessity=base_necessity,
            visual_score=visual_score,
            historical_impact=historical_impact,
            competitor_factor=competitor_factor,
            content_length=len(content)
        )
        
        return decision
    
    def _detect_content_type(
        self,
        title: str,
        content: str,
        keywords: List[str]
    ) -> ContentType:
        """Определение типа контента"""
        
        combined_text = f"{title} {content} {' '.join(keywords)}".lower()
        
        type_scores = {}
        
        for content_type, type_keywords in self.content_type_keywords.items():
            score = 0
            for keyword in type_keywords:
                if keyword.lower() in combined_text:
                    score += 1
            type_scores[content_type] = score
        
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            if best_type[1] > 0:
                return best_type[0]
        
        return ContentType.GENERAL
    
    def _calculate_visual_score(
        self,
        title: str,
        content: str,
        keywords: List[str]
    ) -> float:
        """Расчёт визуального score (насколько контент требует изображений)"""
        
        combined_text = f"{title} {content} {' '.join(keywords)}".lower()
        
        visual_count = 0
        for keyword in self.visual_keywords:
            if keyword.lower() in combined_text:
                visual_count += 1
        
        # Нормализуем score (0-1)
        max_visual = len(self.visual_keywords)
        visual_score = min(visual_count / (max_visual * 0.3), 1.0)
        
        return visual_score
    
    def _get_historical_conversion_impact(
        self,
        content_type: ContentType,
        keywords: List[str]
    ) -> float:
        """Получение исторического влияния изображений на конверсию"""
        
        if content_type not in self.type_conversion_stats:
            # Нет данных - возвращаем нейтральное значение
            return 0.0
        
        stats = self.type_conversion_stats[content_type]
        
        # Сравниваем конверсию с изображениями и без
        with_images = stats.get("conversion_with_images", 0)
        without_images = stats.get("conversion_without_images", 0)
        
        if without_images == 0:
            return 0.0
        
        # Процент улучшения
        improvement = (with_images - without_images) / without_images
        
        return improvement
    
    def _make_decision(
        self,
        content_type: ContentType,
        base_necessity: ImageNecessity,
        visual_score: float,
        historical_impact: float,
        competitor_factor: float,
        content_length: int
    ) -> ImageDecision:
        """Принятие финального решения"""
        
        reasons = []
        
        # Базовое решение на основе типа контента
        if base_necessity == ImageNecessity.REQUIRED:
            should_use = True
            reasons.append(f"Тип контента '{content_type.value}' требует изображений")
        elif base_necessity == ImageNecessity.NOT_NEEDED:
            should_use = False
            reasons.append(f"Тип контента '{content_type.value}' не требует изображений")
        else:
            # Для OPTIONAL и RECOMMENDED - анализируем дополнительные факторы
            should_use = False
            
            # Проверяем визуальный score
            if visual_score > 0.3:
                should_use = True
                reasons.append(f"Высокий визуальный score ({visual_score:.2f})")
            
            # Проверяем исторические данные
            if historical_impact > self.min_conversion_improvement:
                should_use = True
                reasons.append(f"Исторические данные показывают улучшение конверсии на {historical_impact*100:.1f}%")
            
            # Проверяем конкурентов
            if competitor_factor > 1.0:
                should_use = True
                reasons.append("Конкуренты используют изображения")
        
        # Определяем количество изображений
        if should_use:
            if base_necessity == ImageNecessity.REQUIRED:
                hero_image = True
                inline_count = self._calculate_inline_count(content_length, content_type)
            else:
                hero_image = visual_score > 0.5
                inline_count = max(1, int(visual_score * 3))
        else:
            hero_image = False
            inline_count = 0
        
        # Рассчитываем confidence
        confidence = self._calculate_confidence(
            base_necessity, visual_score, historical_impact, len(self.performance_history)
        )
        
        # Оценка влияния на конверсию
        conversion_impact = self._estimate_conversion_impact(
            content_type, visual_score, historical_impact
        )
        
        return ImageDecision(
            should_use_images=should_use,
            necessity_level=base_necessity,
            recommended_count=inline_count + (1 if hero_image else 0),
            hero_image=hero_image,
            inline_images=inline_count,
            reasons=reasons,
            confidence_score=confidence,
            content_type=content_type,
            conversion_impact_estimate=conversion_impact
        )
    
    def _calculate_inline_count(self, content_length: int, content_type: ContentType) -> int:
        """Расчёт количества inline изображений"""
        
        # Базовое количество на основе длины контента
        base_count = content_length // 1500  # 1 изображение на 1500 символов
        
        # Корректировка для типа контента
        type_multipliers = {
            ContentType.TUTORIAL: 1.5,
            ContentType.HOW_TO: 1.5,
            ContentType.FOOD_RECIPE: 2.0,
            ContentType.PRODUCT_REVIEW: 1.3,
            ContentType.TRAVEL: 1.5,
            ContentType.FASHION: 1.5,
        }
        
        multiplier = type_multipliers.get(content_type, 1.0)
        
        return max(1, min(int(base_count * multiplier), 5))
    
    def _calculate_confidence(
        self,
        base_necessity: ImageNecessity,
        visual_score: float,
        historical_impact: float,
        history_size: int
    ) -> float:
        """Расчёт уверенности в решении"""
        
        confidence = 0.5
        
        # Уверенность выше для явных типов контента
        if base_necessity in [ImageNecessity.REQUIRED, ImageNecessity.NOT_NEEDED]:
            confidence += 0.3
        
        # Уверенность выше при наличии исторических данных
        if history_size > 100:
            confidence += 0.15
        elif history_size > 50:
            confidence += 0.1
        
        # Уверенность выше при явном визуальном score
        if visual_score > 0.5 or visual_score < 0.2:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _estimate_conversion_impact(
        self,
        content_type: ContentType,
        visual_score: float,
        historical_impact: float
    ) -> float:
        """Оценка влияния на конверсию"""
        
        # Базовое влияние по типу контента
        base_impacts = {
            ContentType.PRODUCT_REVIEW: 0.25,
            ContentType.ECOMMERCE: 0.30,
            ContentType.TUTORIAL: 0.15,
            ContentType.HOW_TO: 0.15,
            ContentType.FOOD_RECIPE: 0.20,
            ContentType.TRAVEL: 0.20,
            ContentType.FASHION: 0.25,
            ContentType.REAL_ESTATE: 0.35,
            ContentType.NEWS: 0.05,
            ContentType.TECHNICAL: 0.05,
            ContentType.LEGAL: 0.0,
            ContentType.FINANCIAL: 0.02,
            ContentType.ACADEMIC: 0.0,
            ContentType.GENERAL: 0.08,
        }
        
        base = base_impacts.get(content_type, 0.05)
        
        # Корректируем на основе visual score и исторических данных
        adjusted = base * (0.5 + visual_score * 0.5)
        
        if historical_impact > 0:
            adjusted = (adjusted + historical_impact) / 2
        
        return adjusted
    
    def record_article_performance(self, performance: ArticlePerformance):
        """Запись данных о производительности статьи для обучения"""
        
        self.performance_history.append(performance)
        
        # Обновляем статистику по типу контента
        if performance.content_type not in self.type_conversion_stats:
            self.type_conversion_stats[performance.content_type] = {
                "conversion_with_images": 0.0,
                "conversion_without_images": 0.0,
                "count_with_images": 0,
                "count_without_images": 0
            }
        
        stats = self.type_conversion_stats[performance.content_type]
        
        if performance.has_images:
            # Обновляем среднее для статей с изображениями
            total = stats["conversion_with_images"] * stats["count_with_images"]
            stats["count_with_images"] += 1
            stats["conversion_with_images"] = (total + performance.conversion_rate) / stats["count_with_images"]
        else:
            # Обновляем среднее для статей без изображений
            total = stats["conversion_without_images"] * stats["count_without_images"]
            stats["count_without_images"] += 1
            stats["conversion_without_images"] = (total + performance.conversion_rate) / stats["count_without_images"]
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Получение статистики обучения"""
        
        return {
            "total_articles_analyzed": len(self.performance_history),
            "content_type_stats": {
                ct.value: {
                    "with_images_conversion": stats.get("conversion_with_images", 0),
                    "without_images_conversion": stats.get("conversion_without_images", 0),
                    "improvement": (
                        (stats.get("conversion_with_images", 0) - stats.get("conversion_without_images", 0)) 
                        / stats.get("conversion_without_images", 1) * 100
                        if stats.get("conversion_without_images", 0) > 0 else 0
                    ),
                    "sample_size": stats.get("count_with_images", 0) + stats.get("count_without_images", 0)
                }
                for ct, stats in self.type_conversion_stats.items()
            },
            "min_conversion_improvement_threshold": self.min_conversion_improvement
        }


# Глобальный экземпляр
smart_image_decision = SmartImageDecisionSystem()
