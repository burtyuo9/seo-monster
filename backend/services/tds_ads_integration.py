"""
SEO Monster - TDS & Ad Campaigns Integration
Интеграция трекера с рекламными кампаниями
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
ADS_DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/ad_campaigns")


class TDSAdsIntegration:
    """
    Интеграция TDS трекера с модулем рекламных кампаний
    """
    
    def __init__(self):
        self.integration_file = DATA_DIR / "ads_integration.json"
        self._init_data()
    
    def _init_data(self):
        """Инициализация данных интеграции"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        ADS_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if not self.integration_file.exists():
            default_data = {
                "ad_campaigns_mapping": {},
                "click_attribution": {},
                "conversion_postbacks": [],
                "stats_sync": {
                    "last_sync": None,
                    "sync_interval": 300
                },
                "fraud_stats": {
                    "total_blocked": 0,
                    "blocked_by_source": {},
                    "money_saved": 0.0
                }
            }
            self._save_data(default_data)
    
    def _load_data(self) -> dict:
        """Загрузка данных"""
        try:
            with open(self.integration_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_data(self, data: dict):
        """Сохранение данных"""
        with open(self.integration_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def link_ad_campaign_to_tds(self, ad_campaign_id: str, tds_campaign_id: str) -> Dict:
        """Связать рекламную кампанию с TDS кампанией"""
        data = self._load_data()
        if "ad_campaigns_mapping" not in data:
            data["ad_campaigns_mapping"] = {}
        data["ad_campaigns_mapping"][ad_campaign_id] = {
            "tds_campaign_id": tds_campaign_id,
            "linked_at": datetime.now().isoformat(),
            "clicks": 0,
            "conversions": 0,
            "blocked_clicks": 0,
            "fraud_saved": 0.0
        }
        self._save_data(data)
        return {"success": True, "message": "Campaign linked"}
    
    def track_ad_click(self, click_data: Dict) -> Dict:
        """Отслеживание клика из рекламной кампании"""
        data = self._load_data()
        
        ad_campaign_id = click_data.get("ad_campaign_id")
        click_id = click_data.get("click_id")
        is_fraud = click_data.get("is_fraud", False)
        cpc = click_data.get("cpc", 0.0)
        
        # Атрибуция клика
        if "click_attribution" not in data:
            data["click_attribution"] = {}
        data["click_attribution"][click_id] = {
            "ad_campaign_id": ad_campaign_id,
            "timestamp": datetime.now().isoformat(),
            "is_fraud": is_fraud,
            "cpc": cpc
        }
        
        # Обновление статистики маппинга
        if ad_campaign_id in data.get("ad_campaigns_mapping", {}):
            mapping = data["ad_campaigns_mapping"][ad_campaign_id]
            mapping["clicks"] = mapping.get("clicks", 0) + 1
            if is_fraud:
                mapping["blocked_clicks"] = mapping.get("blocked_clicks", 0) + 1
                mapping["fraud_saved"] = mapping.get("fraud_saved", 0) + cpc
        
        # Обновление общей статистики фрода
        if is_fraud:
            if "fraud_stats" not in data:
                data["fraud_stats"] = {"total_blocked": 0, "blocked_by_source": {}, "money_saved": 0.0}
            data["fraud_stats"]["total_blocked"] += 1
            data["fraud_stats"]["money_saved"] += cpc
            
            source = click_data.get("source", "unknown")
            if source not in data["fraud_stats"]["blocked_by_source"]:
                data["fraud_stats"]["blocked_by_source"][source] = 0
            data["fraud_stats"]["blocked_by_source"][source] += 1
        
        self._save_data(data)
        return {"success": True, "tracked": True, "is_fraud": is_fraud}
    
    def record_conversion(self, click_id: str, revenue: float = 0.0) -> Dict:
        """Запись конверсии"""
        data = self._load_data()
        
        # Найти атрибуцию клика
        attribution = data.get("click_attribution", {}).get(click_id)
        if not attribution:
            return {"error": "Click not found"}
        
        ad_campaign_id = attribution.get("ad_campaign_id")
        
        # Обновить статистику
        if ad_campaign_id in data.get("ad_campaigns_mapping", {}):
            data["ad_campaigns_mapping"][ad_campaign_id]["conversions"] = \
                data["ad_campaigns_mapping"][ad_campaign_id].get("conversions", 0) + 1
        
        # Записать постбэк
        if "conversion_postbacks" not in data:
            data["conversion_postbacks"] = []
        data["conversion_postbacks"].append({
            "click_id": click_id,
            "ad_campaign_id": ad_campaign_id,
            "revenue": revenue,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_data(data)
        return {"success": True, "conversion_recorded": True}
    
    def get_campaign_stats(self, ad_campaign_id: str) -> Dict:
        """Получить статистику кампании из TDS"""
        data = self._load_data()
        mapping = data.get("ad_campaigns_mapping", {}).get(ad_campaign_id, {})
        
        return {
            "ad_campaign_id": ad_campaign_id,
            "tds_campaign_id": mapping.get("tds_campaign_id"),
            "clicks": mapping.get("clicks", 0),
            "conversions": mapping.get("conversions", 0),
            "blocked_clicks": mapping.get("blocked_clicks", 0),
            "fraud_saved": mapping.get("fraud_saved", 0.0),
            "linked_at": mapping.get("linked_at")
        }
    
    def get_fraud_stats(self) -> Dict:
        """Получить статистику фрода"""
        data = self._load_data()
        return data.get("fraud_stats", {
            "total_blocked": 0,
            "blocked_by_source": {},
            "money_saved": 0.0
        })
    
    def generate_tracking_url(self, landing_url: str, ad_campaign_id: str, 
                              source: str = "ads") -> str:
        """Генерация tracking URL для рекламной кампании"""
        params = {
            "utm_source": source,
            "utm_medium": "cpc",
            "utm_campaign": ad_campaign_id,
            "click_id": "{click_id}",
            "sub1": "{keyword}",
            "sub2": "{creative}",
            "sub3": "{placement}",
            "sub4": "{device}",
            "sub5": "{geo}"
        }
        
        params_str = "&".join([f"{k}={v}" for k, v in params.items()])
        separator = "&" if "?" in landing_url else "?"
        
        return f"{landing_url}{separator}{params_str}"
    
    def should_block_click(self, click_data: Dict) -> tuple:
        """Проверка, нужно ли блокировать клик"""
        # Интеграция с TDS Antifraud
        from services.tds_antifraud import TDSAntifraud
        
        antifraud = TDSAntifraud()
        is_clean, reason, action = antifraud.check_visitor(click_data)
        
        return not is_clean, reason, action


# Глобальный экземпляр
tds_ads_integration = TDSAdsIntegration()
