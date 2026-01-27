"""
SEO Monster - Localization API Routes
API для управления локализацией
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
from pydantic import BaseModel

from services.localization import localization, TRANSLATIONS, SUPPORTED_LANGUAGES

router = APIRouter(prefix="/api/localization", tags=["Localization"])


class LanguageRequest(BaseModel):
    language: str


class TranslationUpdate(BaseModel):
    key: str
    translations: Dict[str, str]


@router.get("/languages")
async def get_supported_languages():
    """Получение списка поддерживаемых языков"""
    return {
        "languages": SUPPORTED_LANGUAGES,
        "current": localization.get_language(),
        "default": "en"
    }


@router.get("/current")
async def get_current_language():
    """Получение текущего языка"""
    return {
        "language": localization.get_language()
    }


@router.post("/set")
async def set_language(request: LanguageRequest):
    """Установка текущего языка"""
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{request.language}' is not supported. Supported: {SUPPORTED_LANGUAGES}"
        )
    
    localization.set_language(request.language)
    return {
        "success": True,
        "language": request.language,
        "message": f"Language set to {request.language}"
    }


@router.get("/translations")
async def get_translations(lang: Optional[str] = Query(None)):
    """Получение всех переводов для языка"""
    language = lang or localization.get_language()
    
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{language}' is not supported"
        )
    
    return {
        "language": language,
        "translations": TRANSLATIONS.get(language, {})
    }


@router.get("/translate/{key}")
async def translate_key(key: str, lang: Optional[str] = Query(None)):
    """Получение перевода по ключу"""
    language = lang or localization.get_language()
    translation = localization.t(key, lang=language)
    
    return {
        "key": key,
        "language": language,
        "translation": translation
    }


@router.post("/translations/add")
async def add_translation(update: TranslationUpdate):
    """Добавление нового перевода"""
    localization.add_translation(update.key, update.translations)
    
    return {
        "success": True,
        "key": update.key,
        "message": "Translation added successfully"
    }


@router.post("/translations/save")
async def save_custom_translations(lang: str, translations: Dict[str, str]):
    """Сохранение пользовательских переводов"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{lang}' is not supported"
        )
    
    localization.save_custom_translations(lang, translations)
    
    return {
        "success": True,
        "language": lang,
        "count": len(translations),
        "message": "Translations saved successfully"
    }
