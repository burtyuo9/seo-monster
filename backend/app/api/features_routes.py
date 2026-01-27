"""
API Routes для опциональных функций
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict

router = APIRouter(prefix="/api/features", tags=["features"])


@router.get("/optional")
async def get_optional_features() -> List[Dict]:
    """Получить список всех опциональных функций"""
    from services.optional_features import optional_features_service
    
    features = optional_features_service.get_all_features()
    return [f.to_dict() for f in features]


@router.get("/optional/{feature_id}")
async def get_feature_by_id(feature_id: str) -> Dict:
    """Получить информацию о конкретной функции"""
    from services.optional_features import optional_features_service
    
    feature = optional_features_service.get_feature_by_id(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature {feature_id} not found")
    return feature.to_dict()


@router.get("/setup-progress")
async def get_setup_progress() -> Dict:
    """Получить прогресс настройки системы"""
    from services.optional_features import optional_features_service
    
    return optional_features_service.get_setup_progress()


@router.get("/summary")
async def get_features_summary() -> Dict:
    """Получить краткую сводку по функциям"""
    from services.optional_features import optional_features_service
    
    features = optional_features_service.get_all_features()
    progress = optional_features_service.get_setup_progress()
    
    configured = [f for f in features if f.status.value == "configured"]
    not_configured = [f for f in features if f.status.value == "not_configured"]
    
    return {
        "total_features": len(features),
        "configured_count": len(configured),
        "not_configured_count": len(not_configured),
        "configured_features": [{"id": f.id, "name": f.name, "icon": f.icon} for f in configured],
        "available_features": [{"id": f.id, "name": f.name, "icon": f.icon, "config_url": f.config_url} for f in not_configured],
        "overall_progress": progress["overall"]["progress"],
        "core_progress": progress["core"]["progress"],
        "optional_progress": progress["optional"]["progress"]
    }
