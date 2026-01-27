"""
SEO Monster - TDS Landings & Offers System
Система управления лендингами и офферами

Лендинг - промежуточная страница перед оффером
Оффер - конечная точка (партнёрская ссылка, продукт)
"""

import os
import json
import hashlib
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict, field

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
LANDINGS_PATH = DATA_DIR / "landings.json"
OFFERS_PATH = DATA_DIR / "offers.json"
GROUPS_PATH = DATA_DIR / "offer_groups.json"


@dataclass
class Landing:
    """Лендинг (прелендинг)"""
    id: str
    name: str
    
    # URL или локальный путь
    url: str
    local_path: str = ""  # Для локально размещённых лендингов
    
    # Тип
    landing_type: str = "url"  # url, local, html
    html_content: str = ""  # Для типа html
    
    # Группа/категория
    group_id: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Настройки
    action_url: str = ""  # URL для кнопки действия (если не указан, берётся из оффера)
    action_text: str = "Получить"  # Текст кнопки
    
    # Параметры для передачи
    pass_params: bool = True
    custom_params: Dict[str, str] = field(default_factory=dict)
    
    # Статус
    status: str = "active"  # active, paused, archived
    
    # Статистика
    clicks: int = 0
    lp_clicks: int = 0  # Клики на кнопку лендинга
    lp_ctr: float = 0  # LP CTR
    conversions: int = 0
    revenue: float = 0
    
    # Время
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class Offer:
    """Оффер (партнёрская ссылка)"""
    id: str
    name: str
    
    # URL оффера
    url: str
    
    # Партнёрская сеть
    affiliate_network: str = ""
    affiliate_network_id: str = ""
    
    # Группа/категория
    group_id: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Гео
    countries: List[str] = field(default_factory=list)  # Разрешённые страны
    
    # Выплаты
    payout: float = 0  # Выплата за конверсию
    payout_type: str = "cpa"  # cpa, cpl, cps, revshare
    payout_currency: str = "USD"
    
    # Кап (лимит конверсий)
    daily_cap: int = 0  # 0 = без лимита
    total_cap: int = 0
    current_daily: int = 0
    current_total: int = 0
    
    # Постбэк URL для получения конверсий
    postback_url: str = ""
    
    # Параметры
    pass_params: bool = True
    custom_params: Dict[str, str] = field(default_factory=dict)
    
    # Статус
    status: str = "active"  # active, paused, capped, archived
    
    # Статистика
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0
    cr: float = 0
    epc: float = 0
    
    # Время
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class OfferGroup:
    """Группа офферов для ротации"""
    id: str
    name: str
    
    # Офферы в группе с весами
    offers: List[Dict] = field(default_factory=list)  # [{"offer_id": "...", "weight": 100}]
    
    # Режим ротации
    rotation_mode: str = "weight"  # weight, priority, random, sequential
    
    # Фолбэк оффер (если основные недоступны)
    fallback_offer_id: str = ""
    
    # Статус
    status: str = "active"
    
    # Статистика
    clicks: int = 0
    conversions: int = 0
    
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class TDSLandings:
    """
    Менеджер лендингов и офферов
    """
    
    def __init__(self):
        self.landings: Dict[str, Landing] = {}
        self.offers: Dict[str, Offer] = {}
        self.offer_groups: Dict[str, OfferGroup] = {}
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных"""
        # Лендинги
        if LANDINGS_PATH.exists():
            try:
                with open(LANDINGS_PATH, 'r') as f:
                    data = json.load(f)
                    for item in data.get("landings", []):
                        if isinstance(item.get("tags"), str):
                            item["tags"] = []
                        if isinstance(item.get("custom_params"), str):
                            item["custom_params"] = {}
                        landing = Landing(**item)
                        self.landings[landing.id] = landing
            except Exception as e:
                print(f"Ошибка загрузки лендингов: {e}")
        
        # Офферы
        if OFFERS_PATH.exists():
            try:
                with open(OFFERS_PATH, 'r') as f:
                    data = json.load(f)
                    for item in data.get("offers", []):
                        if isinstance(item.get("tags"), str):
                            item["tags"] = []
                        if isinstance(item.get("countries"), str):
                            item["countries"] = []
                        if isinstance(item.get("custom_params"), str):
                            item["custom_params"] = {}
                        offer = Offer(**item)
                        self.offers[offer.id] = offer
            except Exception as e:
                print(f"Ошибка загрузки офферов: {e}")
        
        # Группы офферов
        if GROUPS_PATH.exists():
            try:
                with open(GROUPS_PATH, 'r') as f:
                    data = json.load(f)
                    for item in data.get("groups", []):
                        if isinstance(item.get("offers"), str):
                            item["offers"] = []
                        group = OfferGroup(**item)
                        self.offer_groups[group.id] = group
            except Exception as e:
                print(f"Ошибка загрузки групп: {e}")
    
    def _save_landings(self):
        """Сохранение лендингов"""
        data = {"landings": [asdict(l) for l in self.landings.values()]}
        with open(LANDINGS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_offers(self):
        """Сохранение офферов"""
        data = {"offers": [asdict(o) for o in self.offers.values()]}
        with open(OFFERS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_groups(self):
        """Сохранение групп"""
        data = {"groups": [asdict(g) for g in self.offer_groups.values()]}
        with open(GROUPS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # ЛЕНДИНГИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_landing(self, name: str, url: str, **kwargs) -> Dict:
        """Создание лендинга"""
        landing_id = hashlib.md5(f"lp_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        landing = Landing(
            id=landing_id,
            name=name,
            url=url,
            **kwargs
        )
        
        self.landings[landing_id] = landing
        self._save_landings()
        
        return {
            "success": True,
            "landing_id": landing_id,
            "message": f"Лендинг '{name}' создан"
        }
    
    def get_landing(self, landing_id: str) -> Optional[Dict]:
        """Получение лендинга"""
        if landing_id in self.landings:
            return asdict(self.landings[landing_id])
        return None
    
    def get_landings(self, status: str = None, group_id: str = None) -> List[Dict]:
        """Получение списка лендингов"""
        result = []
        for landing in self.landings.values():
            if status and landing.status != status:
                continue
            if group_id and landing.group_id != group_id:
                continue
            result.append(asdict(landing))
        return result
    
    def update_landing(self, landing_id: str, **kwargs) -> Dict:
        """Обновление лендинга"""
        if landing_id not in self.landings:
            return {"success": False, "error": "Лендинг не найден"}
        
        landing = self.landings[landing_id]
        for key, value in kwargs.items():
            if hasattr(landing, key) and key != "id":
                setattr(landing, key, value)
        
        landing.updated_at = datetime.now().isoformat()
        self._save_landings()
        
        return {"success": True, "message": "Лендинг обновлён"}
    
    def delete_landing(self, landing_id: str) -> Dict:
        """Удаление лендинга"""
        if landing_id not in self.landings:
            return {"success": False, "error": "Лендинг не найден"}
        
        del self.landings[landing_id]
        self._save_landings()
        
        return {"success": True, "message": "Лендинг удалён"}
    
    def record_landing_click(self, landing_id: str) -> Dict:
        """Запись клика по лендингу"""
        if landing_id not in self.landings:
            return {"success": False, "error": "Лендинг не найден"}
        
        landing = self.landings[landing_id]
        landing.clicks += 1
        landing.updated_at = datetime.now().isoformat()
        self._save_landings()
        
        return {"success": True}
    
    def record_lp_click(self, landing_id: str) -> Dict:
        """Запись клика на кнопку лендинга (LP Click)"""
        if landing_id not in self.landings:
            return {"success": False, "error": "Лендинг не найден"}
        
        landing = self.landings[landing_id]
        landing.lp_clicks += 1
        
        # Пересчёт LP CTR
        if landing.clicks > 0:
            landing.lp_ctr = (landing.lp_clicks / landing.clicks) * 100
        
        landing.updated_at = datetime.now().isoformat()
        self._save_landings()
        
        return {"success": True}
    
    # ═══════════════════════════════════════════════════════════════
    # ОФФЕРЫ
    # ═══════════════════════════════════════════════════════════════
    
    def create_offer(self, name: str, url: str, **kwargs) -> Dict:
        """Создание оффера"""
        offer_id = hashlib.md5(f"offer_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        offer = Offer(
            id=offer_id,
            name=name,
            url=url,
            **kwargs
        )
        
        self.offers[offer_id] = offer
        self._save_offers()
        
        return {
            "success": True,
            "offer_id": offer_id,
            "message": f"Оффер '{name}' создан"
        }
    
    def get_offer(self, offer_id: str) -> Optional[Dict]:
        """Получение оффера"""
        if offer_id in self.offers:
            return asdict(self.offers[offer_id])
        return None
    
    def get_offers(self, status: str = None, group_id: str = None,
                  affiliate_network: str = None) -> List[Dict]:
        """Получение списка офферов"""
        result = []
        for offer in self.offers.values():
            if status and offer.status != status:
                continue
            if group_id and offer.group_id != group_id:
                continue
            if affiliate_network and offer.affiliate_network != affiliate_network:
                continue
            result.append(asdict(offer))
        return result
    
    def update_offer(self, offer_id: str, **kwargs) -> Dict:
        """Обновление оффера"""
        if offer_id not in self.offers:
            return {"success": False, "error": "Оффер не найден"}
        
        offer = self.offers[offer_id]
        for key, value in kwargs.items():
            if hasattr(offer, key) and key != "id":
                setattr(offer, key, value)
        
        offer.updated_at = datetime.now().isoformat()
        self._save_offers()
        
        return {"success": True, "message": "Оффер обновлён"}
    
    def delete_offer(self, offer_id: str) -> Dict:
        """Удаление оффера"""
        if offer_id not in self.offers:
            return {"success": False, "error": "Оффер не найден"}
        
        del self.offers[offer_id]
        self._save_offers()
        
        return {"success": True, "message": "Оффер удалён"}
    
    def record_offer_click(self, offer_id: str) -> Dict:
        """Запись клика по офферу"""
        if offer_id not in self.offers:
            return {"success": False, "error": "Оффер не найден"}
        
        offer = self.offers[offer_id]
        offer.clicks += 1
        
        # Пересчёт EPC
        if offer.clicks > 0:
            offer.epc = offer.revenue / offer.clicks
        
        offer.updated_at = datetime.now().isoformat()
        self._save_offers()
        
        return {"success": True}
    
    def record_offer_conversion(self, offer_id: str, revenue: float = None) -> Dict:
        """Запись конверсии оффера"""
        if offer_id not in self.offers:
            return {"success": False, "error": "Оффер не найден"}
        
        offer = self.offers[offer_id]
        offer.conversions += 1
        offer.current_daily += 1
        offer.current_total += 1
        
        # Добавление revenue
        if revenue is not None:
            offer.revenue += revenue
        else:
            offer.revenue += offer.payout
        
        # Пересчёт CR и EPC
        if offer.clicks > 0:
            offer.cr = (offer.conversions / offer.clicks) * 100
            offer.epc = offer.revenue / offer.clicks
        
        # Проверка капа
        if offer.daily_cap > 0 and offer.current_daily >= offer.daily_cap:
            offer.status = "capped"
        if offer.total_cap > 0 and offer.current_total >= offer.total_cap:
            offer.status = "capped"
        
        offer.updated_at = datetime.now().isoformat()
        self._save_offers()
        
        return {"success": True}
    
    def check_offer_cap(self, offer_id: str) -> Dict:
        """Проверка капа оффера"""
        if offer_id not in self.offers:
            return {"available": False, "error": "Оффер не найден"}
        
        offer = self.offers[offer_id]
        
        if offer.status != "active":
            return {"available": False, "reason": f"Статус: {offer.status}"}
        
        if offer.daily_cap > 0 and offer.current_daily >= offer.daily_cap:
            return {"available": False, "reason": "Daily cap reached"}
        
        if offer.total_cap > 0 and offer.current_total >= offer.total_cap:
            return {"available": False, "reason": "Total cap reached"}
        
        return {"available": True}
    
    def reset_daily_caps(self):
        """Сброс дневных капов (вызывать ежедневно)"""
        for offer in self.offers.values():
            offer.current_daily = 0
            if offer.status == "capped" and (offer.total_cap == 0 or offer.current_total < offer.total_cap):
                offer.status = "active"
        
        self._save_offers()
    
    def check_offer_geo(self, offer_id: str, country: str) -> bool:
        """Проверка гео оффера"""
        if offer_id not in self.offers:
            return False
        
        offer = self.offers[offer_id]
        
        # Если список стран пуст, оффер доступен везде
        if not offer.countries:
            return True
        
        return country.upper() in [c.upper() for c in offer.countries]
    
    # ═══════════════════════════════════════════════════════════════
    # ГРУППЫ ОФФЕРОВ
    # ═══════════════════════════════════════════════════════════════
    
    def create_offer_group(self, name: str, offer_ids: List[str] = None,
                          rotation_mode: str = "weight") -> Dict:
        """Создание группы офферов"""
        group_id = hashlib.md5(f"group_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        offers = []
        if offer_ids:
            for oid in offer_ids:
                offers.append({"offer_id": oid, "weight": 100})
        
        group = OfferGroup(
            id=group_id,
            name=name,
            offers=offers,
            rotation_mode=rotation_mode
        )
        
        self.offer_groups[group_id] = group
        self._save_groups()
        
        return {
            "success": True,
            "group_id": group_id,
            "message": f"Группа '{name}' создана"
        }
    
    def get_offer_group(self, group_id: str) -> Optional[Dict]:
        """Получение группы"""
        if group_id in self.offer_groups:
            return asdict(self.offer_groups[group_id])
        return None
    
    def get_offer_groups(self) -> List[Dict]:
        """Получение всех групп"""
        return [asdict(g) for g in self.offer_groups.values()]
    
    def add_offer_to_group(self, group_id: str, offer_id: str, weight: int = 100) -> Dict:
        """Добавление оффера в группу"""
        if group_id not in self.offer_groups:
            return {"success": False, "error": "Группа не найдена"}
        
        if offer_id not in self.offers:
            return {"success": False, "error": "Оффер не найден"}
        
        group = self.offer_groups[group_id]
        
        # Проверка, что оффер ещё не в группе
        for item in group.offers:
            if item["offer_id"] == offer_id:
                return {"success": False, "error": "Оффер уже в группе"}
        
        group.offers.append({"offer_id": offer_id, "weight": weight})
        self._save_groups()
        
        return {"success": True, "message": "Оффер добавлен в группу"}
    
    def remove_offer_from_group(self, group_id: str, offer_id: str) -> Dict:
        """Удаление оффера из группы"""
        if group_id not in self.offer_groups:
            return {"success": False, "error": "Группа не найдена"}
        
        group = self.offer_groups[group_id]
        
        for i, item in enumerate(group.offers):
            if item["offer_id"] == offer_id:
                group.offers.pop(i)
                self._save_groups()
                return {"success": True, "message": "Оффер удалён из группы"}
        
        return {"success": False, "error": "Оффер не найден в группе"}
    
    def update_offer_weight(self, group_id: str, offer_id: str, weight: int) -> Dict:
        """Обновление веса оффера в группе"""
        if group_id not in self.offer_groups:
            return {"success": False, "error": "Группа не найдена"}
        
        group = self.offer_groups[group_id]
        
        for item in group.offers:
            if item["offer_id"] == offer_id:
                item["weight"] = weight
                self._save_groups()
                return {"success": True, "message": "Вес обновлён"}
        
        return {"success": False, "error": "Оффер не найден в группе"}
    
    def select_offer_from_group(self, group_id: str, country: str = "") -> Optional[str]:
        """Выбор оффера из группы с учётом ротации и гео"""
        if group_id not in self.offer_groups:
            return None
        
        group = self.offer_groups[group_id]
        
        if not group.offers:
            return group.fallback_offer_id or None
        
        # Фильтрация доступных офферов
        available_offers = []
        for item in group.offers:
            offer_id = item["offer_id"]
            
            # Проверка существования
            if offer_id not in self.offers:
                continue
            
            offer = self.offers[offer_id]
            
            # Проверка статуса
            if offer.status != "active":
                continue
            
            # Проверка капа
            cap_check = self.check_offer_cap(offer_id)
            if not cap_check["available"]:
                continue
            
            # Проверка гео
            if country and not self.check_offer_geo(offer_id, country):
                continue
            
            available_offers.append(item)
        
        if not available_offers:
            return group.fallback_offer_id or None
        
        # Выбор по режиму ротации
        if group.rotation_mode == "random":
            return random.choice(available_offers)["offer_id"]
        
        elif group.rotation_mode == "sequential":
            # Простая последовательная ротация
            group.clicks += 1
            idx = (group.clicks - 1) % len(available_offers)
            self._save_groups()
            return available_offers[idx]["offer_id"]
        
        elif group.rotation_mode == "priority":
            # Первый доступный
            return available_offers[0]["offer_id"]
        
        else:  # weight
            total_weight = sum(item["weight"] for item in available_offers)
            if total_weight == 0:
                return random.choice(available_offers)["offer_id"]
            
            rand = random.randint(1, total_weight)
            current = 0
            
            for item in available_offers:
                current += item["weight"]
                if rand <= current:
                    return item["offer_id"]
            
            return available_offers[-1]["offer_id"]
    
    def delete_offer_group(self, group_id: str) -> Dict:
        """Удаление группы"""
        if group_id not in self.offer_groups:
            return {"success": False, "error": "Группа не найдена"}
        
        del self.offer_groups[group_id]
        self._save_groups()
        
        return {"success": True, "message": "Группа удалена"}
    
    # ═══════════════════════════════════════════════════════════════
    # ПОСТРОЕНИЕ URL
    # ═══════════════════════════════════════════════════════════════
    
    def build_landing_url(self, landing_id: str, visitor_data: Dict = None) -> str:
        """Построение URL лендинга с параметрами"""
        if landing_id not in self.landings:
            return ""
        
        landing = self.landings[landing_id]
        url = landing.url
        
        if not landing.pass_params or not visitor_data:
            return url
        
        # Добавление параметров
        params = []
        
        if visitor_data.get("click_id"):
            params.append(f"click_id={visitor_data['click_id']}")
        if visitor_data.get("sub_id"):
            params.append(f"subid={visitor_data['sub_id']}")
        
        # Кастомные параметры
        for key, value in landing.custom_params.items():
            # Замена макросов
            val = self._apply_macros(value, visitor_data)
            params.append(f"{key}={val}")
        
        if params:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{'&'.join(params)}"
        
        return url
    
    def build_offer_url(self, offer_id: str, visitor_data: Dict = None) -> str:
        """Построение URL оффера с параметрами"""
        if offer_id not in self.offers:
            return ""
        
        offer = self.offers[offer_id]
        url = offer.url
        
        if not offer.pass_params or not visitor_data:
            return url
        
        # Добавление параметров
        params = []
        
        if visitor_data.get("click_id"):
            params.append(f"click_id={visitor_data['click_id']}")
        if visitor_data.get("sub_id"):
            params.append(f"subid={visitor_data['sub_id']}")
        
        # Sub ID 1-5
        for i in range(1, 6):
            key = f"sub_id_{i}"
            if visitor_data.get(key):
                params.append(f"sub{i}={visitor_data[key]}")
        
        # Кастомные параметры
        for key, value in offer.custom_params.items():
            val = self._apply_macros(value, visitor_data)
            params.append(f"{key}={val}")
        
        if params:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{'&'.join(params)}"
        
        return url
    
    def _apply_macros(self, value: str, visitor_data: Dict) -> str:
        """Применение макросов"""
        if not value or not visitor_data:
            return value
        
        macros = {
            "{click_id}": visitor_data.get("click_id", ""),
            "{sub_id}": visitor_data.get("sub_id", ""),
            "{country}": visitor_data.get("country", ""),
            "{city}": visitor_data.get("city", ""),
            "{device}": visitor_data.get("device_type", ""),
            "{os}": visitor_data.get("os", ""),
            "{browser}": visitor_data.get("browser", ""),
            "{ip}": visitor_data.get("ip", "")
        }
        
        result = value
        for macro, val in macros.items():
            result = result.replace(macro, str(val))
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    def get_landings_stats(self) -> Dict:
        """Общая статистика лендингов"""
        total_clicks = sum(l.clicks for l in self.landings.values())
        total_lp_clicks = sum(l.lp_clicks for l in self.landings.values())
        total_conversions = sum(l.conversions for l in self.landings.values())
        
        avg_lp_ctr = 0
        if total_clicks > 0:
            avg_lp_ctr = (total_lp_clicks / total_clicks) * 100
        
        return {
            "total_landings": len(self.landings),
            "active_landings": len([l for l in self.landings.values() if l.status == "active"]),
            "total_clicks": total_clicks,
            "total_lp_clicks": total_lp_clicks,
            "total_conversions": total_conversions,
            "avg_lp_ctr": round(avg_lp_ctr, 2)
        }
    
    def get_offers_stats(self) -> Dict:
        """Общая статистика офферов"""
        total_clicks = sum(o.clicks for o in self.offers.values())
        total_conversions = sum(o.conversions for o in self.offers.values())
        total_revenue = sum(o.revenue for o in self.offers.values())
        
        avg_cr = 0
        avg_epc = 0
        if total_clicks > 0:
            avg_cr = (total_conversions / total_clicks) * 100
            avg_epc = total_revenue / total_clicks
        
        return {
            "total_offers": len(self.offers),
            "active_offers": len([o for o in self.offers.values() if o.status == "active"]),
            "capped_offers": len([o for o in self.offers.values() if o.status == "capped"]),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_revenue": round(total_revenue, 2),
            "avg_cr": round(avg_cr, 2),
            "avg_epc": round(avg_epc, 4)
        }


# Singleton
_tds_landings = None

def get_tds_landings() -> TDSLandings:
    """Получение экземпляра TDS Landings"""
    global _tds_landings
    if _tds_landings is None:
        _tds_landings = TDSLandings()
    return _tds_landings
