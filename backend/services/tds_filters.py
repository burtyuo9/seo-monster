"""
SEO Monster - TDS Filters System
Система фильтров для распределения трафика

Типы фильтров:
- Гео (страна, город, регион)
- Устройство (desktop, mobile, tablet)
- ОС (Windows, macOS, Android, iOS, Linux)
- Браузер (Chrome, Firefox, Safari, Edge)
- ISP / Мобильный оператор
- Язык браузера
- Реферер
- IP диапазоны
- Время (дни недели, часы)
- Лимиты (клики, уники, конверсии)
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
import ipaddress

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
FILTERS_PATH = DATA_DIR / "filters.json"


@dataclass
class Filter:
    """Базовый фильтр"""
    id: str = ""
    name: str = ""
    filter_type: str = ""
    condition: str = "include"  # include, exclude
    values: List[str] = field(default_factory=list)
    enabled: bool = True
    
    def match(self, value: str) -> bool:
        """Проверка соответствия значения фильтру"""
        if not self.enabled:
            return True
        
        value_lower = str(value).lower()
        values_lower = [v.lower() for v in self.values]
        
        matched = value_lower in values_lower
        
        if self.condition == "include":
            return matched
        else:  # exclude
            return not matched


@dataclass
class GeoFilter(Filter):
    """Фильтр по гео"""
    filter_type: str = "geo"
    geo_type: str = "country"  # country, city, region
    
    def match(self, geo_data: Dict) -> bool:
        if not self.enabled:
            return True
        
        value = geo_data.get(self.geo_type, "").lower()
        values_lower = [v.lower() for v in self.values]
        
        matched = value in values_lower
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class DeviceFilter(Filter):
    """Фильтр по устройству"""
    filter_type: str = "device"
    
    def match(self, device_type: str) -> bool:
        if not self.enabled:
            return True
        
        matched = device_type.lower() in [v.lower() for v in self.values]
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class OSFilter(Filter):
    """Фильтр по ОС"""
    filter_type: str = "os"
    include_versions: bool = False
    
    def match(self, os_name: str, os_version: str = "") -> bool:
        if not self.enabled:
            return True
        
        check_value = os_name.lower()
        if self.include_versions and os_version:
            check_value = f"{os_name} {os_version}".lower()
        
        matched = any(v.lower() in check_value for v in self.values)
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class BrowserFilter(Filter):
    """Фильтр по браузеру"""
    filter_type: str = "browser"
    min_version: Optional[int] = None
    
    def match(self, browser: str, browser_version: str = "") -> bool:
        if not self.enabled:
            return True
        
        browser_lower = browser.lower()
        matched = browser_lower in [v.lower() for v in self.values]
        
        # Проверка минимальной версии
        if matched and self.min_version and browser_version:
            try:
                version = int(browser_version.split(".")[0])
                if version < self.min_version:
                    matched = False
            except:
                pass
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class ISPFilter(Filter):
    """Фильтр по ISP/оператору"""
    filter_type: str = "isp"
    
    def match(self, isp: str) -> bool:
        if not self.enabled:
            return True
        
        isp_lower = isp.lower()
        matched = any(v.lower() in isp_lower for v in self.values)
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class LanguageFilter(Filter):
    """Фильтр по языку браузера"""
    filter_type: str = "language"
    
    def match(self, accept_language: str) -> bool:
        if not self.enabled:
            return True
        
        # Парсинг Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8
        languages = []
        for part in accept_language.split(","):
            lang = part.split(";")[0].strip().lower()
            if "-" in lang:
                lang = lang.split("-")[0]
            languages.append(lang)
        
        matched = any(v.lower() in languages for v in self.values)
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class ReferrerFilter(Filter):
    """Фильтр по рефереру"""
    filter_type: str = "referrer"
    match_type: str = "domain"  # domain, url, contains
    
    def match(self, referrer: str, referrer_domain: str = "") -> bool:
        if not self.enabled:
            return True
        
        if self.match_type == "domain":
            check_value = referrer_domain.lower()
        elif self.match_type == "url":
            check_value = referrer.lower()
        else:  # contains
            check_value = referrer.lower()
        
        if self.match_type == "contains":
            matched = any(v.lower() in check_value for v in self.values)
        else:
            matched = check_value in [v.lower() for v in self.values]
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class IPFilter(Filter):
    """Фильтр по IP"""
    filter_type: str = "ip"
    match_type: str = "exact"  # exact, range, subnet
    
    def match(self, ip: str) -> bool:
        if not self.enabled:
            return True
        
        try:
            ip_addr = ipaddress.ip_address(ip)
            
            matched = False
            for value in self.values:
                if self.match_type == "exact":
                    if ip == value:
                        matched = True
                        break
                elif self.match_type == "range":
                    # Формат: 192.168.1.1-192.168.1.255
                    if "-" in value:
                        start, end = value.split("-")
                        start_ip = ipaddress.ip_address(start.strip())
                        end_ip = ipaddress.ip_address(end.strip())
                        if start_ip <= ip_addr <= end_ip:
                            matched = True
                            break
                elif self.match_type == "subnet":
                    # Формат: 192.168.1.0/24
                    network = ipaddress.ip_network(value, strict=False)
                    if ip_addr in network:
                        matched = True
                        break
        except:
            matched = False
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class TimeFilter(Filter):
    """Фильтр по времени"""
    filter_type: str = "time"
    time_type: str = "day_of_week"  # day_of_week, hour, date_range
    timezone: str = "UTC"
    
    def match(self, timestamp: datetime = None) -> bool:
        if not self.enabled:
            return True
        
        if timestamp is None:
            timestamp = datetime.now()
        
        matched = False
        
        if self.time_type == "day_of_week":
            # 0 = Monday, 6 = Sunday
            current_day = str(timestamp.weekday())
            matched = current_day in self.values
        
        elif self.time_type == "hour":
            # Часы в формате "9", "10", "11" или диапазон "9-17"
            current_hour = timestamp.hour
            for value in self.values:
                if "-" in value:
                    start, end = map(int, value.split("-"))
                    if start <= current_hour <= end:
                        matched = True
                        break
                else:
                    if current_hour == int(value):
                        matched = True
                        break
        
        elif self.time_type == "date_range":
            # Формат: "2024-01-01,2024-12-31"
            for value in self.values:
                if "," in value:
                    start_str, end_str = value.split(",")
                    start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
                    end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")
                    if start_date <= timestamp <= end_date:
                        matched = True
                        break
        
        if self.condition == "include":
            return matched
        else:
            return not matched


@dataclass
class LimitFilter:
    """Фильтр по лимитам"""
    id: str
    name: str
    limit_type: str  # clicks, unique_clicks, conversions, revenue
    limit_value: int
    period: str  # total, daily, hourly
    current_value: int = 0
    last_reset: str = ""
    enabled: bool = True
    
    def check_limit(self) -> Tuple[bool, int]:
        """Проверка лимита. Возвращает (достигнут ли лимит, оставшееся количество)"""
        if not self.enabled:
            return False, self.limit_value
        
        # Проверка необходимости сброса
        now = datetime.now()
        
        if self.period == "daily":
            if self.last_reset:
                last = datetime.fromisoformat(self.last_reset)
                if last.date() < now.date():
                    self.current_value = 0
                    self.last_reset = now.isoformat()
            else:
                self.last_reset = now.isoformat()
        
        elif self.period == "hourly":
            if self.last_reset:
                last = datetime.fromisoformat(self.last_reset)
                if (now - last).total_seconds() >= 3600:
                    self.current_value = 0
                    self.last_reset = now.isoformat()
            else:
                self.last_reset = now.isoformat()
        
        remaining = self.limit_value - self.current_value
        limit_reached = self.current_value >= self.limit_value
        
        return limit_reached, max(0, remaining)
    
    def increment(self, value: int = 1):
        """Увеличение счётчика"""
        self.current_value += value


@dataclass
class FilterGroup:
    """Группа фильтров (логическое объединение)"""
    id: str
    name: str
    logic: str  # and, or
    filters: List[str]  # ID фильтров
    enabled: bool = True


class TDSFilters:
    """
    Менеджер фильтров TDS
    """
    
    def __init__(self):
        self.filters: Dict[str, Filter] = {}
        self.limit_filters: Dict[str, LimitFilter] = {}
        self.filter_groups: Dict[str, FilterGroup] = {}
        self._load_filters()
    
    def _load_filters(self):
        """Загрузка фильтров из файла"""
        if FILTERS_PATH.exists():
            try:
                with open(FILTERS_PATH, 'r') as f:
                    data = json.load(f)
                    # Восстановление фильтров из JSON
                    for f_data in data.get("filters", []):
                        self._create_filter_from_dict(f_data)
                    
                    for lf_data in data.get("limit_filters", []):
                        self.limit_filters[lf_data["id"]] = LimitFilter(**lf_data)
                    
                    for fg_data in data.get("filter_groups", []):
                        self.filter_groups[fg_data["id"]] = FilterGroup(**fg_data)
            except Exception as e:
                print(f"Ошибка загрузки фильтров: {e}")
    
    def _save_filters(self):
        """Сохранение фильтров в файл"""
        data = {
            "filters": [asdict(f) for f in self.filters.values()],
            "limit_filters": [asdict(lf) for lf in self.limit_filters.values()],
            "filter_groups": [asdict(fg) for fg in self.filter_groups.values()]
        }
        
        with open(FILTERS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _create_filter_from_dict(self, data: Dict) -> Filter:
        """Создание фильтра из словаря"""
        filter_type = data.get("filter_type", "")
        
        filter_classes = {
            "geo": GeoFilter,
            "device": DeviceFilter,
            "os": OSFilter,
            "browser": BrowserFilter,
            "isp": ISPFilter,
            "language": LanguageFilter,
            "referrer": ReferrerFilter,
            "ip": IPFilter,
            "time": TimeFilter
        }
        
        filter_class = filter_classes.get(filter_type, Filter)
        
        # Удаляем лишние поля
        valid_fields = {f.name for f in filter_class.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        filter_obj = filter_class(**filtered_data)
        self.filters[filter_obj.id] = filter_obj
        
        return filter_obj
    
    # ═══════════════════════════════════════════════════════════════
    # СОЗДАНИЕ ФИЛЬТРОВ
    # ═══════════════════════════════════════════════════════════════
    
    def create_geo_filter(self, name: str, countries: List[str],
                         condition: str = "include",
                         geo_type: str = "country") -> Dict:
        """Создание гео-фильтра"""
        import hashlib
        filter_id = hashlib.md5(f"geo_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        geo_filter = GeoFilter(
            id=filter_id,
            name=name,
            filter_type="geo",
            condition=condition,
            values=countries,
            geo_type=geo_type
        )
        
        self.filters[filter_id] = geo_filter
        self._save_filters()
        
        return {"success": True, "filter_id": filter_id, "filter": asdict(geo_filter)}
    
    def create_device_filter(self, name: str, devices: List[str],
                            condition: str = "include") -> Dict:
        """Создание фильтра по устройствам"""
        import hashlib
        filter_id = hashlib.md5(f"device_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        device_filter = DeviceFilter(
            id=filter_id,
            name=name,
            filter_type="device",
            condition=condition,
            values=devices
        )
        
        self.filters[filter_id] = device_filter
        self._save_filters()
        
        return {"success": True, "filter_id": filter_id, "filter": asdict(device_filter)}
    
    def create_os_filter(self, name: str, os_list: List[str],
                        condition: str = "include",
                        include_versions: bool = False) -> Dict:
        """Создание фильтра по ОС"""
        import hashlib
        filter_id = hashlib.md5(f"os_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        os_filter = OSFilter(
            id=filter_id,
            name=name,
            filter_type="os",
            condition=condition,
            values=os_list,
            include_versions=include_versions
        )
        
        self.filters[filter_id] = os_filter
        self._save_filters()
        
        return {"success": True, "filter_id": filter_id, "filter": asdict(os_filter)}
    
    def create_browser_filter(self, name: str, browsers: List[str],
                             condition: str = "include",
                             min_version: int = None) -> Dict:
        """Создание фильтра по браузерам"""
        import hashlib
        filter_id = hashlib.md5(f"browser_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        browser_filter = BrowserFilter(
            id=filter_id,
            name=name,
            filter_type="browser",
            condition=condition,
            values=browsers,
            min_version=min_version
        )
        
        self.filters[filter_id] = browser_filter
        self._save_filters()
        
        return {"success": True, "filter_id": filter_id, "filter": asdict(browser_filter)}
    
    def create_ip_filter(self, name: str, ips: List[str],
                        condition: str = "exclude",
                        match_type: str = "exact") -> Dict:
        """Создание IP фильтра"""
        import hashlib
        filter_id = hashlib.md5(f"ip_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        ip_filter = IPFilter(
            id=filter_id,
            name=name,
            filter_type="ip",
            condition=condition,
            values=ips,
            match_type=match_type
        )
        
        self.filters[filter_id] = ip_filter
        self._save_filters()
        
        return {"success": True, "filter_id": filter_id, "filter": asdict(ip_filter)}
    
    def create_referrer_filter(self, name: str, referrers: List[str],
                              condition: str = "include",
                              match_type: str = "domain") -> Dict:
        """Создание фильтра по рефереру"""
        import hashlib
        filter_id = hashlib.md5(f"ref_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        ref_filter = ReferrerFilter(
            id=filter_id,
            name=name,
            filter_type="referrer",
            condition=condition,
            values=referrers,
            match_type=match_type
        )
        
        self.filters[filter_id] = ref_filter
        self._save_filters()
        
        return {"success": True, "filter_id": filter_id, "filter": asdict(ref_filter)}
    
    def create_time_filter(self, name: str, values: List[str],
                          condition: str = "include",
                          time_type: str = "day_of_week") -> Dict:
        """Создание временного фильтра"""
        import hashlib
        filter_id = hashlib.md5(f"time_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        time_filter = TimeFilter(
            id=filter_id,
            name=name,
            filter_type="time",
            condition=condition,
            values=values,
            time_type=time_type
        )
        
        self.filters[filter_id] = time_filter
        self._save_filters()
        
        return {"success": True, "filter_id": filter_id, "filter": asdict(time_filter)}
    
    def create_limit_filter(self, name: str, limit_type: str,
                           limit_value: int, period: str = "daily") -> Dict:
        """Создание лимит-фильтра"""
        import hashlib
        filter_id = hashlib.md5(f"limit_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        limit_filter = LimitFilter(
            id=filter_id,
            name=name,
            limit_type=limit_type,
            limit_value=limit_value,
            period=period
        )
        
        self.limit_filters[filter_id] = limit_filter
        self._save_filters()
        
        return {"success": True, "filter_id": filter_id, "filter": asdict(limit_filter)}
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ ФИЛЬТРАМИ
    # ═══════════════════════════════════════════════════════════════
    
    def get_filter(self, filter_id: str) -> Optional[Dict]:
        """Получение фильтра по ID"""
        if filter_id in self.filters:
            return asdict(self.filters[filter_id])
        if filter_id in self.limit_filters:
            return asdict(self.limit_filters[filter_id])
        return None
    
    def get_all_filters(self) -> Dict:
        """Получение всех фильтров"""
        return {
            "filters": [asdict(f) for f in self.filters.values()],
            "limit_filters": [asdict(lf) for lf in self.limit_filters.values()],
            "filter_groups": [asdict(fg) for fg in self.filter_groups.values()]
        }
    
    def update_filter(self, filter_id: str, **kwargs) -> Dict:
        """Обновление фильтра"""
        if filter_id in self.filters:
            filter_obj = self.filters[filter_id]
            for key, value in kwargs.items():
                if hasattr(filter_obj, key):
                    setattr(filter_obj, key, value)
            self._save_filters()
            return {"success": True, "filter": asdict(filter_obj)}
        
        if filter_id in self.limit_filters:
            limit_filter = self.limit_filters[filter_id]
            for key, value in kwargs.items():
                if hasattr(limit_filter, key):
                    setattr(limit_filter, key, value)
            self._save_filters()
            return {"success": True, "filter": asdict(limit_filter)}
        
        return {"success": False, "error": "Фильтр не найден"}
    
    def delete_filter(self, filter_id: str) -> Dict:
        """Удаление фильтра"""
        if filter_id in self.filters:
            del self.filters[filter_id]
            self._save_filters()
            return {"success": True, "message": "Фильтр удалён"}
        
        if filter_id in self.limit_filters:
            del self.limit_filters[filter_id]
            self._save_filters()
            return {"success": True, "message": "Лимит-фильтр удалён"}
        
        return {"success": False, "error": "Фильтр не найден"}
    
    def toggle_filter(self, filter_id: str, enabled: bool) -> Dict:
        """Включение/выключение фильтра"""
        return self.update_filter(filter_id, enabled=enabled)
    
    # ═══════════════════════════════════════════════════════════════
    # ГРУППЫ ФИЛЬТРОВ
    # ═══════════════════════════════════════════════════════════════
    
    def create_filter_group(self, name: str, filter_ids: List[str],
                           logic: str = "and") -> Dict:
        """Создание группы фильтров"""
        import hashlib
        group_id = hashlib.md5(f"group_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        group = FilterGroup(
            id=group_id,
            name=name,
            logic=logic,
            filters=filter_ids
        )
        
        self.filter_groups[group_id] = group
        self._save_filters()
        
        return {"success": True, "group_id": group_id, "group": asdict(group)}
    
    def get_filter_group(self, group_id: str) -> Optional[Dict]:
        """Получение группы фильтров"""
        if group_id in self.filter_groups:
            return asdict(self.filter_groups[group_id])
        return None
    
    def delete_filter_group(self, group_id: str) -> Dict:
        """Удаление группы фильтров"""
        if group_id in self.filter_groups:
            del self.filter_groups[group_id]
            self._save_filters()
            return {"success": True, "message": "Группа удалена"}
        return {"success": False, "error": "Группа не найдена"}
    
    # ═══════════════════════════════════════════════════════════════
    # ПРОВЕРКА ФИЛЬТРОВ
    # ═══════════════════════════════════════════════════════════════
    
    def check_visitor(self, visitor_data: Dict, filter_ids: List[str] = None,
                     group_id: str = None) -> Tuple[bool, str]:
        """
        Проверка посетителя по фильтрам
        
        visitor_data должен содержать:
        - ip: str
        - country: str
        - city: str
        - region: str
        - isp: str
        - device_type: str
        - os: str
        - os_version: str
        - browser: str
        - browser_version: str
        - referrer: str
        - referrer_domain: str
        - accept_language: str
        
        Возвращает: (прошёл ли проверку, причина блокировки)
        """
        
        # Если указана группа, берём фильтры из неё
        if group_id and group_id in self.filter_groups:
            group = self.filter_groups[group_id]
            filter_ids = group.filters
            logic = group.logic
        else:
            logic = "and"
        
        if not filter_ids:
            return True, ""
        
        results = []
        block_reasons = []
        
        for filter_id in filter_ids:
            if filter_id not in self.filters:
                continue
            
            filter_obj = self.filters[filter_id]
            passed = True
            
            if isinstance(filter_obj, GeoFilter):
                geo_data = {
                    "country": visitor_data.get("country", ""),
                    "city": visitor_data.get("city", ""),
                    "region": visitor_data.get("region", "")
                }
                passed = filter_obj.match(geo_data)
                if not passed:
                    block_reasons.append(f"Geo filter: {filter_obj.name}")
            
            elif isinstance(filter_obj, DeviceFilter):
                passed = filter_obj.match(visitor_data.get("device_type", ""))
                if not passed:
                    block_reasons.append(f"Device filter: {filter_obj.name}")
            
            elif isinstance(filter_obj, OSFilter):
                passed = filter_obj.match(
                    visitor_data.get("os", ""),
                    visitor_data.get("os_version", "")
                )
                if not passed:
                    block_reasons.append(f"OS filter: {filter_obj.name}")
            
            elif isinstance(filter_obj, BrowserFilter):
                passed = filter_obj.match(
                    visitor_data.get("browser", ""),
                    visitor_data.get("browser_version", "")
                )
                if not passed:
                    block_reasons.append(f"Browser filter: {filter_obj.name}")
            
            elif isinstance(filter_obj, ISPFilter):
                passed = filter_obj.match(visitor_data.get("isp", ""))
                if not passed:
                    block_reasons.append(f"ISP filter: {filter_obj.name}")
            
            elif isinstance(filter_obj, LanguageFilter):
                passed = filter_obj.match(visitor_data.get("accept_language", ""))
                if not passed:
                    block_reasons.append(f"Language filter: {filter_obj.name}")
            
            elif isinstance(filter_obj, ReferrerFilter):
                passed = filter_obj.match(
                    visitor_data.get("referrer", ""),
                    visitor_data.get("referrer_domain", "")
                )
                if not passed:
                    block_reasons.append(f"Referrer filter: {filter_obj.name}")
            
            elif isinstance(filter_obj, IPFilter):
                passed = filter_obj.match(visitor_data.get("ip", ""))
                if not passed:
                    block_reasons.append(f"IP filter: {filter_obj.name}")
            
            elif isinstance(filter_obj, TimeFilter):
                passed = filter_obj.match()
                if not passed:
                    block_reasons.append(f"Time filter: {filter_obj.name}")
            
            results.append(passed)
        
        # Применение логики
        if logic == "and":
            final_result = all(results) if results else True
        else:  # or
            final_result = any(results) if results else True
        
        block_reason = "; ".join(block_reasons) if not final_result else ""
        
        return final_result, block_reason
    
    def check_limits(self, limit_filter_ids: List[str]) -> Tuple[bool, str]:
        """
        Проверка лимитов
        Возвращает: (лимит достигнут, причина)
        """
        for filter_id in limit_filter_ids:
            if filter_id not in self.limit_filters:
                continue
            
            limit_filter = self.limit_filters[filter_id]
            reached, remaining = limit_filter.check_limit()
            
            if reached:
                return True, f"Limit reached: {limit_filter.name} ({limit_filter.limit_type})"
        
        return False, ""
    
    def increment_limits(self, limit_filter_ids: List[str], 
                        increment_type: str = "clicks", value: int = 1):
        """Увеличение счётчиков лимитов"""
        for filter_id in limit_filter_ids:
            if filter_id not in self.limit_filters:
                continue
            
            limit_filter = self.limit_filters[filter_id]
            if limit_filter.limit_type == increment_type:
                limit_filter.increment(value)
        
        self._save_filters()


# Singleton
_tds_filters = None

def get_tds_filters() -> TDSFilters:
    """Получение экземпляра TDS Filters"""
    global _tds_filters
    if _tds_filters is None:
        _tds_filters = TDSFilters()
    return _tds_filters
