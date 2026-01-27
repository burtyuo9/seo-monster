"""
SEO Monster - Traffic Routing System (Keitaro-style)
Система маршрутизации трафика с правилами и условиями
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
import hashlib
import random

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
ROUTING_PATH = DATA_DIR / "routing.json"
LANDINGS_PATH = DATA_DIR / "landings.json"
OFFERS_PATH = DATA_DIR / "offers.json"


@dataclass
class Landing:
    """Лендинг/прелендинг"""
    id: str
    name: str
    url: str
    landing_type: str = "prelanding"  # prelanding, landing, white
    weight: int = 100
    enabled: bool = True
    clicks: int = 0
    conversions: int = 0
    created_at: str = ""


@dataclass
class Offer:
    """Оффер"""
    id: str
    name: str
    url: str
    payout: float = 0.0
    payout_type: str = "cpa"  # cpa, cpl, cps, revshare
    currency: str = "USD"
    countries: List[str] = field(default_factory=list)
    weight: int = 100
    enabled: bool = True
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    created_at: str = ""


@dataclass
class RoutingRule:
    """Правило маршрутизации"""
    id: str
    name: str
    priority: int = 0
    conditions: List[Dict] = field(default_factory=list)
    action: str = "redirect"  # redirect, landing, offer, block, split
    landing_ids: List[str] = field(default_factory=list)
    offer_ids: List[str] = field(default_factory=list
)
    redirect_url: str = ""
    split_test: bool = False
    enabled: bool = True
    hits: int = 0
    created_at: str = ""


class TrafficRouter:
    """Система маршрутизации трафика"""
    
    def __init__(self):
        self.landings: Dict[str, Landing] = {}
        self.offers: Dict[str, Offer] = {}
        self.rules: Dict[str, RoutingRule] = {}
        self.click_log: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True
)
        
        if LANDINGS_PATH.exists():
            try:
                with open(LANDINGS_PATH, 'r') as f:
                    data = json.load(f)
                    for l_data in data.get("landings", []):
                        landing = Landing(**l_data)
                        self.landings[landing.id] = landing
            except Exception as e:
                print(f"Error loading landings: {e}")
        
        if OFFERS_PATH.exists():
            try:
                with open(OFFERS_PATH, 'r') as f:
                    data = json.load(f)
                    for o_data in data.get("offers", []):
                        offer = Offer(**o_data)
                        self.offers[offer.id] = offer
            except Exception as e:
                print(f"Error loading offers: {e}")
        
        if ROUTING_PATH.exists():
            try:
                with open(ROUTING_PATH, 'r') as f:
                    data = json.load(f)
                    for r_data in data.get("rules", []):
                        rule = RoutingRule(**r_data)
                        self.rules[rule.id] = rule
            except Exception as e:
                print(f"Error loading routing rules: {e}")
    
    def _save_landings(self):
        data = {"landings": [asdict(l) for l in self.landings.values()]}
        with open(LANDINGS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_offers(self):
        data = {"offers": [asdict(o) for o in self.offers.values()]}
        with open(OFFERS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_rules(self):
        data = {"rules": [asdict(r) for r in self.rules.values()]}
        with open(ROUTING_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # ЛЕНДИНГИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_landing(self, name: str, url: str, **kwargs) -> Landing:
        landing_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        landing = Landing(
            id=landing_id,
            name=name,
            url=url,
            landing_type=kwargs.get("landing_type", "prelanding"),
            weight=kwargs.get("weight", 100),
            enabled=kwargs.get("enabled", True),
            created_at=datetime.now().isoformat()
        )
        
        self.landings[landing_id] = landing
        self._save_landings()
        return landing
    
    def get_landings(self) -> List[Dict]:
        return [asdict(l) for l in self.landings.values()]
    
    def update_landing(self, landing_id: str, **kwargs) -> Optional[Landing]:
        if landing_id not in self.landings:
            return None
        landing = self.landings[landing_id]
        for key, value in kwargs.items():
            if hasattr(landing, key):
                setattr(landing, key, value)
        self._save_landings()
        return landing
    
    def delete_landing(self, landing_id: str) -> bool:
        if landing_id in self.landings:
            del self.landings[landing_id]
            self._save_landings()
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════
    # ОФФЕРЫ
    # ═══════════════════════════════════════════════════════════════
    
    def create_offer(self, name: str, url: str, **kwargs) -> Offer:
        offer_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        offer = Offer(
            id=offer_id,
            name=name,
            url=url,
            payout=kwargs.get("payout", 0.0),
            payout_type=kwargs.get("payout_type", "cpa"),
            currency=kwargs.get("currency", "USD"),
            countries=kwargs.get("countries", []),
            weight=kwargs.get("weight", 100),
            enabled=kwargs.get("enabled", True),
            created_at=datetime.now().isoformat()
        )
        
        self.offers[offer_id] = offer
        self._save_offers()
        return offer
    
    def get_offers(self) -> List[Dict]:
        return [asdict(o) for o in self.offers.values()]
    
    def update_offer(self, offer_id: str, **kwargs) -> Optional[Offer]:
        if offer_id not in self.offers:
            return None
        offer = self.offers[offer_id]
        for key, value in kwargs.items():
            if hasattr(offer, key):
                setattr(offer, key, value)
        self._save_offers()
        return offer
    
    def delete_offer(self, offer_id: str) -> bool:
        if offer_id in self.offers:
            del self.offers[offer_id]
            self._save_offers()
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════
    # ПРАВИЛА МАРШРУТИЗАЦИИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_rule(self, name: str, conditions: List[Dict], action: str, **kwargs) -> RoutingRule:
        rule_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        rule = RoutingRule(
            id=rule_id,
            name=name,
            priority=kwargs.get("priority", 0),
            conditions=conditions,
            action=action,
            landing_ids=kwargs.get("landing_ids", []),
            offer_ids=kwargs.get("offer_ids", []),
            redirect_url=kwargs.get("redirect_url", ""),
            split_test=kwargs.get("split_test", False),
            enabled=kwargs.get("enabled", True),
            created_at=datetime.now().isoformat()
        )
        
        self.rules[rule_id] = rule
        self._save_rules()
        return rule
    
    def get_rules(self) -> List[Dict]:
        return [asdict(r) for r in self.rules.values()]
    
    def update_rule(self, rule_id: str, **kwargs) -> Optional[RoutingRule]:
        if rule_id not in self.rules:
            return None
        rule = self.rules[rule_id]
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        self._save_rules()
        return rule
    
    def delete_rule(self, rule_id: str) -> bool:
        if rule_id in self.rules:
            del self.rules[rule_id]
            self._save_rules()
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════
    # МАРШРУТИЗАЦИЯ
    # ═══════════════════════════════════════════════════════════════
    
    def route_visitor(self, visitor_data: Dict) -> Dict:
        """
        Маршрутизация посетителя на основе правил
        """
        result = {
            "action": "default",
            "destination": "",
            "landing": None,
            "offer": None,
            "rule_id": "",
            "click_id": hashlib.md5(f"{visitor_data.get('ip', '')}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        }
        
        # Проверяем правила в порядке приоритета
        sorted_rules = sorted(
            [r for r in self.rules.values() if r.enabled],
            key=lambda x: x.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            if self._match_rule(rule, visitor_data):
                rule.hits += 1
                result["rule_id"] = rule.id
                
                if rule.action == "block":
                    result["action"] = "block"
                    break
                
                elif rule.action == "redirect":
                    result["action"] = "redirect"
                    result["destination"] = rule.redirect_url
                    break
                
                elif rule.action == "landing":
                    landing = self._select_landing(rule.landing_ids)
                    if landing:
                        result["action"] = "landing"
                        result["landing"] = asdict(landing)
                        result["destination"] = landing.url
                        landing.clicks += 1
                    break
                
                elif rule.action == "offer":
                    offer = self._select_offer(rule.offer_ids, visitor_data)
                    if offer:
                        result["action"] = "offer"
                        result["offer"] = asdict(offer)
                        result["destination"] = self._build_offer_url(offer, result["click_id"])
                        offer.clicks += 1
                    break
                
                elif rule.action == "split":
                    # A/B тест между лендингами и офферами
                    if random.random() < 0.5 and rule.landing_ids:
                        landing = self._select_landing(rule.landing_ids)
                        if landing:
                            result["action"] = "landing"
                            result["landing"] = asdict(landing)
                            result["destination"] = landing.url
                            landing.clicks += 1
                    elif rule.offer_ids:
                        offer = self._select_offer(rule.offer_ids, visitor_data)
                        if offer:
                            result["action"] = "offer"
                            result["offer"] = asdict(offer)
                            result["destination"] = self._build_offer_url(offer, result["click_id"])
                            offer.clicks += 1
                    break
        
        # Логирование клика
        self._log_click(visitor_data, result)
        
        self._save_landings()
        self._save_offers()
        self._save_rules()
        
        return result
    
    def _match_rule(self, rule: RoutingRule, visitor_data: Dict) -> bool:
        """Проверка соответствия правилу"""
        for condition in rule.conditions:
            field = condition.get("field", "")
            operator = condition.get("operator", "is")
            values = condition.get("values", [])
            
            visitor_value = visitor_data.get(field, "")
            if isinstance(visitor_value, str):
                visitor_value = visitor_value.lower()
            
            values_lower = [v.lower() if isinstance(v, str) else v for v in values]
            
            if operator == "is":
                if visitor_value not in values_lower:
                    return False
            elif operator == "is_not":
                if visitor_value in values_lower:
                    return False
            elif operator == "contains":
                if not any(v in str(visitor_value) for v in values_lower):
                    return False
            elif operator == "not_contains":
                if any(v in str(visitor_value) for v in values_lower):
                    return False
            elif operator == "regex":
                if not any(re.match(v, str(visitor_value), re.IGNORECASE) for v in values):
                    return False
        
        return True
    
    def _select_landing(self, landing_ids: List[str]) -> Optional[Landing]:
        """Выбор лендинга с учётом весов"""
        available = [self.landings[lid] for lid in landing_ids 
                    if lid in self.landings and self.landings[lid].enabled]
        
        if not available:
            return None
        
        total_weight = sum(l.weight for l in available)
        if total_weight == 0:
            return random.choice(available)
        
        r = random.randint(1, total_weight)
        cumulative = 0
        for landing in available:
            cumulative += landing.weight
            if r <= cumulative:
                return landing
        
        return available[0]
    
    def _select_offer(self, offer_ids: List[str], visitor_data: Dict) -> Optional[Offer]:
        """Выбор оффера с учётом весов и гео"""
        country = visitor_data.get("country", "").upper()
        
        available = []
        for oid in offer_ids:
            if oid in self.offers:
                offer = self.offers[oid]
                if offer.enabled:
                    # Проверка гео
                    if not offer.countries or country in offer.countries:
                        available.append(offer)
        
        if not available:
            return None
        
        total_weight = sum(o.weight for o in available)
        if total_weight == 0:
            return random.choice(available)
        
        r = random.randint(1, total_weight)
        cumulative = 0
        for offer in available:
            cumulative += offer.weight
            if r <= cumulative:
                return offer
        
        return available[0]
    
    def _build_offer_url(self, offer: Offer, click_id: str) -> str:
        """Построение URL оффера с параметрами"""
        url = offer.url
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}click_id={click_id}"
    
    def _log_click(self, visitor_data: Dict, result: Dict):
        """Логирование клика"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "click_id": result.get("click_id", ""),
            "ip": visitor_data.get("ip", ""),
            "country": visitor_data.get("country", ""),
            "action": result.get("action", ""),
            "rule_id": result.get("rule_id", ""),
            "destination": result.get("destination", "")
        }
        self.click_log.append(log_entry)
        
        # Ограничиваем размер лога
        if len(self.click_log) > 10000:
            self.click_log = self.click_log[-5000:]
    
    def record_conversion(self, click_id: str, revenue: float = 0.0) -> bool:
        """Запись конверсии"""
        # Ищем клик в логе
        for log in reversed(self.click_log):
            if log.get("click_id") == click_id:
                # Обновляем статистику оффера
                for offer in self.offers.values():
                    if offer.url in log.get("destination", ""):
                        offer.conversions += 1
                        offer.revenue += revenue if revenue > 0 else offer.payout
                        self._save_offers()
                        return True
        return False
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        total_clicks = sum(l.clicks for l in self.landings.values()) + sum(o.clicks for o in self.offers.values())
        total_conversions = sum(o.conversions for o in self.offers.values())
        total_revenue = sum(o.revenue for o in self.offers.values())
        
        return {
            "total_landings": len(self.landings),
            "total_offers": len(self.offers),
            "total_rules": len(self.rules),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_revenue": total_revenue,
            "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
            "epc": (total_revenue / total_clicks) if total_clicks > 0 else 0
        }


# Глобальный экземпляр
traffic_router = TrafficRouter()
