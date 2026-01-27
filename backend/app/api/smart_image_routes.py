"""
SEO Monster - Smart Image Decision API Routes
API для умной системы принятия решений об использовании изображений
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services'))

from services.smart_image_decision import (
    smart_image_decision,
    ContentType,
    ImageNecessity,
    ArticlePerformance
)
from services.image_providers import image_provider_manager


router = APIRouter(prefix="/api/smart-images", tags=["Smart Images"])


class AnalyzeContentRequest(BaseModel):
    title: str
    content: str
    keywords: List[str]
    target_audience: str = "general"
    competitor_has_images: bool = False


class GetImagesIfNeededRequest(BaseModel):
    title: str
    content: str
    keywords: List[str]
    target_audience: str = "general"
    competitor_has_images: bool = False
    prefer_ai: bool = True


class RecordPerformanceRequest(BaseModel):
    article_id: str
    has_images: bool
    image_count: int
    content_type: str
    keywords: List[str]
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    conversions: int = 0
    conversion_rate: float = 0.0
    avg_time_on_page: float = 0.0
    bounce_rate: float = 0.0


@router.post("/analyze")
async def analyze_content_for_images(request: AnalyzeContentRequest):
    """
    Анализ контента и определение необходимости изображений
    
    Возвращает рекомендацию: нужны ли изображения и сколько
    """
    
    decision = smart_image_decision.analyze_content(
        title=request.title,
        content=request.content,
        keywords=request.keywords,
        target_audience=request.target_audience,
        competitor_has_images=request.competitor_has_images
    )
    
    return {
        "success": True,
        "decision": {
            "should_use_images": decision.should_use_images,
            "necessity_level": decision.necessity_level.value,
            "recommended_count": decision.recommended_count,
            "hero_image": decision.hero_image,
            "inline_images": decision.inline_images,
            "reasons": decision.reasons,
            "confidence_score": decision.confidence_score,
            "content_type": decision.content_type.value,
            "conversion_impact_estimate": f"{decision.conversion_impact_estimate * 100:.1f}%"
        }
    }


@router.post("/get-if-needed")
async def get_images_if_needed(request: GetImagesIfNeededRequest):
    """
    Получить изображения ТОЛЬКО если они улучшат конверсию
    
    Сначала анализирует контент, затем получает изображения только если нужно
    """
    
    # 1. Анализируем контент
    decision = smart_image_decision.analyze_content(
        title=request.title,
        content=request.content,
        keywords=request.keywords,
        target_audience=request.target_audience,
        competitor_has_images=request.competitor_has_images
    )
    
    result = {
        "success": True,
        "images_needed": decision.should_use_images,
        "decision": {
            "necessity_level": decision.necessity_level.value,
            "content_type": decision.content_type.value,
            "reasons": decision.reasons,
            "confidence_score": decision.confidence_score,
            "conversion_impact_estimate": f"{decision.conversion_impact_estimate * 100:.1f}%"
        },
        "images": None
    }
    
    # 2. Получаем изображения ТОЛЬКО если нужно
    if decision.should_use_images:
        images = await image_provider_manager.get_images_for_content(
            title=request.title,
            content=request.content,
            keywords=request.keywords,
            image_count=decision.recommended_count,
            include_hero=decision.hero_image,
            prefer_ai=request.prefer_ai
        )
        result["images"] = images
    
    return result


@router.post("/record-performance")
async def record_article_performance(request: RecordPerformanceRequest):
    """
    Запись данных о производительности статьи для обучения системы
    """
    
    try:
        content_type = ContentType(request.content_type)
    except ValueError:
        content_type = ContentType.GENERAL
    
    performance = ArticlePerformance(
        article_id=request.article_id,
        has_images=request.has_images,
        image_count=request.image_count,
        content_type=content_type,
        keywords=request.keywords,
        impressions=request.impressions,
        clicks=request.clicks,
        ctr=request.ctr,
        conversions=request.conversions,
        conversion_rate=request.conversion_rate,
        avg_time_on_page=request.avg_time_on_page,
        bounce_rate=request.bounce_rate
    )
    
    smart_image_decision.record_article_performance(performance)
    
    return {
        "success": True,
        "message": "Performance data recorded for learning"
    }


@router.get("/learning-stats")
async def get_learning_stats():
    """
    Получение статистики обучения системы
    """
    
    return {
        "success": True,
        "stats": smart_image_decision.get_learning_stats()
    }


@router.get("/content-types")
async def get_content_types():
    """
    Получение списка типов контента и их требований к изображениям
    """
    
    return {
        "success": True,
        "content_types": [
            {
                "type": ct.value,
                "necessity": smart_image_decision.content_type_rules.get(ct, ImageNecessity.OPTIONAL).value,
                "description": {
                    ContentType.PRODUCT_REVIEW: "Обзоры товаров - изображения обязательны",
                    ContentType.TUTORIAL: "Инструкции и туториалы - изображения обязательны",
                    ContentType.HOW_TO: "Практические руководства - изображения обязательны",
                    ContentType.TRAVEL: "Путешествия и туризм - изображения обязательны",
                    ContentType.FOOD_RECIPE: "Рецепты и кулинария - изображения обязательны",
                    ContentType.FASHION: "Мода и стиль - изображения обязательны",
                    ContentType.REAL_ESTATE: "Недвижимость - изображения обязательны",
                    ContentType.ECOMMERCE: "Товары и покупки - изображения обязательны",
                    ContentType.NEWS: "Новости - изображения опционально",
                    ContentType.TECHNICAL: "Технические статьи - изображения опционально",
                    ContentType.LEGAL: "Юридические тексты - изображения не нужны",
                    ContentType.FINANCIAL: "Финансовые статьи - изображения не нужны",
                    ContentType.ACADEMIC: "Академические тексты - изображения не нужны",
                    ContentType.GENERAL: "Общий контент - требуется анализ"
                }.get(ct, "")
            }
            for ct in ContentType
        ]
    }


@router.get("/necessity-levels")
async def get_necessity_levels():
    """
    Получение уровней необходимости изображений
    """
    
    return {
        "success": True,
        "levels": [
            {
                "level": level.value,
                "description": {
                    ImageNecessity.REQUIRED: "Изображения обязательны для конверсии",
                    ImageNecessity.RECOMMENDED: "Изображения рекомендуются",
                    ImageNecessity.OPTIONAL: "Изображения опционально",
                    ImageNecessity.NOT_NEEDED: "Изображения не улучшат конверсию"
                }.get(level, "")
            }
            for level in ImageNecessity
        ]
    }
