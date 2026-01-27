"""
SEO Monster - Traffic Filter & Flow System (Keitaro-style)
Система фильтрации трафика и управления потоками
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
FLOWS_PATH = DATA_DIR / "flows.json"
FILTERS_PATH = DATA_DIR / "filters.json"


class FilterType(str, Enum):
    COUNTRY = "country"
    CITY = "city"
    REGION = "region"
    LANGUAGE = "language"
    BROWSER = "browser"
    OS = "os"
    DEVICE = "device"
    ISP = "isp"
    CONNECTION = "connection"
    REFERRER = "referrer"
    KEYWORD = "keyword"
    SUB_ID = "sub_id"
    IP = "ip"
    IP_RANGE = "ip_range"
    USER_AGENT = "user_agent"
    TIME = "time"
    DAY_OF_WEEK = "day_of_week"
    UNIQUE = "unique"
    PROXY = "proxy"
    BOT = "bot"
    CUSTOM = "custom"


class FilterAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    REDIRECT = "redirect"
    SHOW_OFFER = "show_offer"
    SHOW_LANDING = "show_landing"


class FlowType(str, Enum):
    MAIN = "main"
    DEFAULT = "default"
    BOT = "bot"
    MODERATOR = "moderator"


@dataclass
class Filter:
    """Фильтр трафика"""
    id: str
    name: str
    filter_type: str
    condition: str  # is, is_not, contains, not_contains, starts_with, regex
    values: List[str]
    action: str = "allow"
    redirect_url: str = ""
    priority: int = 0
    enabled: bool = True
    created_at: str = ""
    hits: int = 0


@dataclass
class Flow:
    """Поток трафика"""
    id: str
    name: str
    flow_type: str
    filters: List[str]  # IDs фильтров
    action: str  # redirect, landing, offer, block
    destination_url: str = ""
    landing_id: str = ""
    offer_id: str = ""
    weight: int = 100  # Для A/B тестирования
    enabled: bool = True
    created_at: str = ""
    clicks: int = 0
    conversions: int = 0


@dataclass
class Campaign:
    """Рекламная кампания с потоками"""
    id: str
    name: str
    domain: str
    flows: List[str]  # IDs потоков
    default_flow_id: str = ""
    bot_flow_id: str = ""
    moderator_flow_id: str = ""
    enabled: bool = True
    created_at: str = ""
    total_clicks: int = 0
    unique_clicks: int = 0
    conversions: int = 0


class TrafficFilter:
    """
    Система фильтрации трафика как в Keitaro
    """
    
    def __init__(self):
        self.filters: Dict[str, Filter] = {}
        self.flows: Dict[str, Flow] = {}
        self.campaigns: Dict[str, Campaign] = {}
        self._load_data()
    
    def _load_data(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if FILTERS_PATH.exists():
            try:
                with open(FILTERS_PATH, 'r') as f:
                    data = json.load(f)
                    for f_data in data.get("filters", []):
                        flt = Filter(**f_data)
                        self.filters[flt.id] = flt
            except Exception as e:
                print(f"Error loading filters: {e}")
        
        if FLOWS_PATH.exists():
            try:
                with open(FLOWS_PATH, 'r') as f:
                    data = json.load(f)
                    for fl_data in data.get("flows", []):
                        flow = Flow(**fl_data)
                        self.flows[flow.id] = flow
                    for c_data in data.get("campaigns", []):
                        camp = Campaign(**c_data)
                        self.campaigns[camp.id] = camp
            except Exception as e:
                print(f"Error loading flows: {e}")
    
    def _save_filters(self):
        data = {"filters": [asdict(f) for f in self.filters.values()]}
        with open(FILTERS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_flows(self):
        data = {
            "flows": [asdict(f) for f in self.flows.values()],
            "campaigns": [asdict(c) for c in self.campaigns.values()]
        }
        with open(FLOWS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # ФИЛЬТРЫ
    # ═══════════════════════════════════════════════════════════════
    
    def create_filter(self, name: str, filter_type: str, condition: str,
                     values: List[str], action: str = "allow", **kwargs) -> Filter:
        filter_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        flt = Filter(
            id=filter_id,
            name=name,
            filter_type=filter_type,
            condition=condition,
            values=values,
            action=action,
            redirect_url=kwargs.get("redirect_url", ""),
            priority=kwargs.get("priority", 0),
            enabled=kwargs.get("enabled", True),
            created_at=datetime.now().isoformat()
        )
        
        self.filters[filter_id] = flt
        self._save_filters()
        return flt
    
    def get_filters(self) -> List[Dict]:
        return [asdict(f) for f in self.filters.values()]
    
    def update_filter(self, filter_id: str, **kwargs) -> Optional[Filter]:
        if filter_id not in self.filters:
            return None
        
        flt = self.filters[filter_id]
        for key, value in kwargs.items():
            if hasattr(flt, key):
                setattr(flt, key, value)
        
        self._save_filters()
        return flt
    
    def delete_filter(self, filter_id: str) -> bool:
        if filter_id in self.filters:
            del self.filters[filter_id]
            self._save_filters()
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════
    # ПОТОКИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_flow(self, name: str, flow_type: str, action: str, **kwargs) -> Flow:
        flow_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        flow = Flow(
            id=flow_id,
            name=name,
            flow_type=flow_type,
            filters=kwargs.get("filters", []),
            action=action,
            destination_url=kwargs.get("destination_url", ""),
            landing_id=kwargs.get("landing_id", ""),
            offer_id=kwargs.get("offer_id", ""),
            weight=kwargs.get("weight", 100),
            enabled=kwargs.get("enabled", True),
            created_at=datetime.now().isoformat()
        )
        
        self.flows[flow_id] = flow
        self._save_flows()
        return flow
    
    def get_flows(self) -> List[Dict]:
        return [asdict(f) for f in self.flows.values()]
    
    def update_flow(self, flow_id: str, **kwargs) -> Optional[Flow]:
        if flow_id not in self.flows:
            return None
        
        flow = self.flows[flow_id]
        for key, value in kwargs.items():
            if hasattr(flow, key):
                setattr(flow, key, value)
        
        self._save_flows()
        return flow
    
    def delete_flow(self, flow_id: str) -> bool:
        if flow_id in self.flows:
            del self.flows[flow_id]
            self._save_flows()
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════
    # КАМПАНИИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_campaign(self, name: str, domain: str, **kwargs) -> Campaign:
        camp_id = hashlib.md5(f"{name}_{domain}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        campaign = Campaign(
            id=camp_id,
            name=name,
            domain=domain,
            flows=kwargs.get("flows", []),
            default_flow_id=kwargs.get("default_flow_id", ""),
            bot_flow_id=kwargs.get("bot_flow_id", ""),
            moderator_flow_id=kwargs.get("moderator_flow_id", ""),
            enabled=kwargs.get("enabled", True),
            created_at=datetime.now().isoformat()
        )
        
        self.campaigns[camp_id] = campaign
        self._save_flows()
        return campaign
    
    def get_campaigns(self) -> List[Dict]:
        return [asdict(c) for c in self.campaigns.values()]
    
    # ═══════════════════════════════════════════════════════════════
    # ПРОВЕРКА ТРАФИКА
    # ═══════════════════════════════════════════════════════════════
    
    def check_visitor(self, visitor_data: Dict, campaign_id: str = "") -> Dict:
        """
        Проверка посетителя через все фильтры
        Возвращает решение: какой поток использовать
        """
        result = {
            "allowed": True,
            "flow_id": "",
            "action": "allow",
            "destination": "",
            "matched_filters": [],
            "reason": ""
        }
        
        # Получаем кампанию
        campaign = self.campaigns.get(campaign_id)
        if not campaign or not campaign.enabled:
            result["action"] = "default"
            return result
        
        # Проверяем фильтры в порядке приоритета
        sorted_filters = sorted(
            [f for f in self.filters.values() if f.enabled],
            key=lambda x: x.priority,
            reverse=True
        )
        
        for flt in sorted_filters:
            if self._match_filter(flt, visitor_data):
                result["matched_filters"].append(flt.id)
                flt.hits += 1
                
                if flt.action == "block":
                    result["allowed"] = False
                    result["action"] = "block"
                    result["reason"] = f"Blocked by filter: {flt.name}"
                    break
                elif flt.action == "redirect":
                    result["action"] = "redirect"
                    result["destination"] = flt.redirect_url
                    break
        
        # Если не заблокирован, определяем поток
        if result["allowed"]:
            flow = self._select_flow(campaign, visitor_data)
            if flow:
                result["flow_id"] = flow.id
                result["action"] = flow.action
                result["destination"] = flow.destination_url
                flow.clicks += 1
        
        self._save_filters()
        self._save_flows()
        return result
    
    def _match_filter(self, flt: Filter, visitor_data: Dict) -> bool:
        """Проверка соответствия фильтру"""
        value = ""
        
        # Получаем значение для проверки
        if flt.filter_type == FilterType.COUNTRY:
            value = visitor_data.get("country", "").upper()
        elif flt.filter_type == FilterType.LANGUAGE:
            value = visitor_data.get("language", "").lower()
        elif flt.filter_type == FilterType.BROWSER:
            value = visitor_data.get("browser", "").lower()
        elif flt.filter_type == FilterType.OS:
            value = visitor_data.get("os", "").lower()
        elif flt.filter_type == FilterType.DEVICE:
            value = visitor_data.get("device", "").lower()
        elif flt.filter_type == FilterType.REFERRER:
            value = visitor_data.get("referrer", "").lower()
        elif flt.filter_type == FilterType.IP:
            value = visitor_data.get("ip", "")
        elif flt.filter_type == FilterType.USER_AGENT:
            value = visitor_data.get("user_agent", "").lower()
        elif flt.filter_type == FilterType.BOT:
            value = "bot" if visitor_data.get("is_bot", False) else "human"
        elif flt.filter_type == FilterType.PROXY:
            value = "proxy" if visitor_data.get("is_proxy", False) else "direct"
        else:
            return False
        
        # Применяем условие
        filter_values = [v.lower() if isinstance(v, str) else v for v in flt.values]
        
        if flt.condition == "is":
            return value.lower() in filter_values if isinstance(value, str) else value in filter_values
        elif flt.condition == "is_not":
            return value.lower() not in filter_values if isinstance(value, str) else value not in filter_values
        elif flt.condition == "contains":
            return any(fv in value for fv in filter_values)
        elif flt.condition == "not_contains":
            return not any(fv in value for fv in filter_values)
        elif flt.condition == "starts_with":
            return any(value.startswith(fv) for fv in filter_values)
        elif flt.condition == "regex":
            return any(re.match(fv, value, re.IGNORECASE) for fv in flt.values)
        
        return False
    
    def _select_flow(self, campaign: Campaign, visitor_data: Dict) -> Optional[Flow]:
        """Выбор потока для посетителя"""
        # Проверка на бота
        if visitor_data.get("is_bot", False) and campaign.bot_flow_id:
            return self.flows.get(campaign.bot_flow_id)
        
        # Проверка на модератора
        if visitor_data.get("is_moderator", False) and campaign.moderator_flow_id:
            return self.flows.get(campaign.moderator_flow_id)
        
        # Проверяем потоки кампании
        for flow_id in campaign.flows:
            flow = self.flows.get(flow_id)
            if flow and flow.enabled:
                # Проверяем фильтры потока
                all_match = True
                for filter_id in flow.filters:
                    flt = self.filters.get(filter_id)
                    if flt and not self._match_filter(flt, visitor_data):
                        all_match = False
                        break
                
                if all_match:
                    return flow
        
        # Дефолтный поток
        if campaign.default_flow_id:
            return self.flows.get(campaign.default_flow_id)
        
        return None
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        total_clicks = sum(f.clicks for f in self.flows.values())
        total_conversions = sum(f.conversions for f in self.flows.values())
        
        return {
            "total_filters": len(self.filters),
            "total_flows": len(self.flows),
            "total_campaigns": len(self.campaigns),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
            "filter_hits": sum(f.hits for f in self.filters.values())
        }


# Глобальный экземпляр
traffic_filter = TrafficFilter()
