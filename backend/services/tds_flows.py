"""
SEO Monster - TDS Flows System
Система потоков для распределения трафика

Поток (Flow) - это набор правил, определяющих куда направить посетителя:
- Схема потока (последовательность действий)
- Правила фильтрации
- Лендинги и офферы
- Веса для A/B тестирования
"""

import os
import json
import hashlib
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/tds")
FLOWS_PATH = DATA_DIR / "flows.json"


class FlowAction(Enum):
    """Действия в потоке"""
    REDIRECT = "redirect"  # Редирект на URL
    LANDING = "landing"    # Показать лендинг
    OFFER = "offer"        # Редирект на оффер
    SHOW_HTML = "show_html"  # Показать HTML
    SHOW_404 = "show_404"  # Показать 404
    BLOCK = "block"        # Заблокировать
    NEXT_FLOW = "next_flow"  # Перейти к другому потоку


class RedirectType(Enum):
    """Типы редиректов"""
    HTTP_301 = "301"
    HTTP_302 = "302"
    HTTP_303 = "303"
    HTTP_307 = "307"
    META_REFRESH = "meta"
    JAVASCRIPT = "js"
    DOUBLE_META = "double_meta"
    CURL = "curl"


@dataclass
class FlowPath:
    """Путь в потоке (landing -> offer или direct)"""
    id: str
    name: str
    
    # Действие
    action: str  # redirect, landing, offer, show_html, show_404, block
    
    # Для redirect
    redirect_url: str = ""
    redirect_type: str = "302"
    
    # Для landing/offer
    landing_id: str = ""
    offer_id: str = ""
    
    # Для show_html
    html_content: str = ""
    
    # Вес для распределения (0-100)
    weight: int = 100
    
    # Фильтры (ID фильтров)
    filter_ids: List[str] = field(default_factory=list)
    filter_group_id: str = ""
    
    # Лимиты
    limit_filter_ids: List[str] = field(default_factory=list)
    
    # Статус
    enabled: bool = True
    
    # Статистика
    clicks: int = 0
    conversions: int = 0


@dataclass
class Flow:
    """Поток распределения трафика"""
    id: str
    name: str
    campaign_id: str
    
    # Схема потока
    schema: str  # "landing_offer", "direct", "multi_landing", "split_test"
    
    # Пути в потоке
    paths: List[FlowPath] = field(default_factory=list)
    
    # Действие по умолчанию (если ни один путь не подошёл)
    default_action: str = "show_404"
    default_url: str = ""
    
    # Глобальные фильтры потока
    filter_ids: List[str] = field(default_factory=list)
    filter_group_id: str = ""
    
    # Глобальные лимиты
    limit_filter_ids: List[str] = field(default_factory=list)
    
    # Настройки редиректа
    default_redirect_type: str = "302"
    pass_referrer: bool = True
    pass_query_params: bool = True
    
    # Макросы для URL
    # {click_id}, {sub_id}, {country}, {city}, {device}, {os}, {browser}
    url_macros_enabled: bool = True
    
    # Статус
    status: str = "active"  # active, paused, archived
    
    # Приоритет (для выбора между потоками)
    priority: int = 0
    
    # Статистика
    total_clicks: int = 0
    unique_clicks: int = 0
    conversions: int = 0
    
    # Время
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class TDSFlows:
    """
    Менеджер потоков TDS
    """
    
    def __init__(self):
        self.flows: Dict[str, Flow] = {}
        self._load_flows()
    
    def _load_flows(self):
        """Загрузка потоков из файла"""
        if FLOWS_PATH.exists():
            try:
                with open(FLOWS_PATH, 'r') as f:
                    data = json.load(f)
                    for flow_data in data.get("flows", []):
                        # Восстановление путей
                        paths = []
                        for path_data in flow_data.get("paths", []):
                            # Преобразование списков
                            if isinstance(path_data.get("filter_ids"), str):
                                path_data["filter_ids"] = []
                            if isinstance(path_data.get("limit_filter_ids"), str):
                                path_data["limit_filter_ids"] = []
                            paths.append(FlowPath(**path_data))
                        
                        flow_data["paths"] = paths
                        
                        # Преобразование списков в Flow
                        if isinstance(flow_data.get("filter_ids"), str):
                            flow_data["filter_ids"] = []
                        if isinstance(flow_data.get("limit_filter_ids"), str):
                            flow_data["limit_filter_ids"] = []
                        
                        flow = Flow(**flow_data)
                        self.flows[flow.id] = flow
            except Exception as e:
                print(f"Ошибка загрузки потоков: {e}")
    
    def _save_flows(self):
        """Сохранение потоков в файл"""
        data = {
            "flows": []
        }
        
        for flow in self.flows.values():
            flow_dict = asdict(flow)
            # Конвертация путей
            flow_dict["paths"] = [asdict(p) for p in flow.paths]
            data["flows"].append(flow_dict)
        
        with open(FLOWS_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # СОЗДАНИЕ И УПРАВЛЕНИЕ ПОТОКАМИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_flow(self, name: str, campaign_id: str,
                   schema: str = "direct", **kwargs) -> Dict:
        """Создание потока"""
        flow_id = hashlib.md5(f"flow_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        flow = Flow(
            id=flow_id,
            name=name,
            campaign_id=campaign_id,
            schema=schema,
            **kwargs
        )
        
        self.flows[flow_id] = flow
        self._save_flows()
        
        return {
            "success": True,
            "flow_id": flow_id,
            "message": f"Поток '{name}' создан"
        }
    
    def get_flow(self, flow_id: str) -> Optional[Dict]:
        """Получение потока по ID"""
        if flow_id in self.flows:
            flow = self.flows[flow_id]
            flow_dict = asdict(flow)
            flow_dict["paths"] = [asdict(p) for p in flow.paths]
            return flow_dict
        return None
    
    def get_flows(self, campaign_id: str = None, status: str = None) -> List[Dict]:
        """Получение списка потоков"""
        result = []
        
        for flow in self.flows.values():
            if campaign_id and flow.campaign_id != campaign_id:
                continue
            if status and flow.status != status:
                continue
            
            flow_dict = asdict(flow)
            flow_dict["paths"] = [asdict(p) for p in flow.paths]
            result.append(flow_dict)
        
        # Сортировка по приоритету
        result.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        return result
    
    def update_flow(self, flow_id: str, **kwargs) -> Dict:
        """Обновление потока"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Поток не найден"}
        
        flow = self.flows[flow_id]
        
        for key, value in kwargs.items():
            if hasattr(flow, key) and key != "id":
                setattr(flow, key, value)
        
        flow.updated_at = datetime.now().isoformat()
        self._save_flows()
        
        return {"success": True, "message": "Поток обновлён"}
    
    def delete_flow(self, flow_id: str) -> Dict:
        """Удаление потока"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Поток не найден"}
        
        del self.flows[flow_id]
        self._save_flows()
        
        return {"success": True, "message": "Поток удалён"}
    
    def duplicate_flow(self, flow_id: str, new_name: str = None) -> Dict:
        """Дублирование потока"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Поток не найден"}
        
        original = self.flows[flow_id]
        
        new_id = hashlib.md5(f"flow_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Копирование потока
        new_flow = Flow(
            id=new_id,
            name=new_name or f"{original.name} (копия)",
            campaign_id=original.campaign_id,
            schema=original.schema,
            default_action=original.default_action,
            default_url=original.default_url,
            filter_ids=original.filter_ids.copy(),
            filter_group_id=original.filter_group_id,
            limit_filter_ids=original.limit_filter_ids.copy(),
            default_redirect_type=original.default_redirect_type,
            pass_referrer=original.pass_referrer,
            pass_query_params=original.pass_query_params,
            url_macros_enabled=original.url_macros_enabled,
            priority=original.priority
        )
        
        # Копирование путей
        for path in original.paths:
            new_path_id = hashlib.md5(f"path_{datetime.now().isoformat()}{random.random()}".encode()).hexdigest()[:10]
            new_path = FlowPath(
                id=new_path_id,
                name=path.name,
                action=path.action,
                redirect_url=path.redirect_url,
                redirect_type=path.redirect_type,
                landing_id=path.landing_id,
                offer_id=path.offer_id,
                html_content=path.html_content,
                weight=path.weight,
                filter_ids=path.filter_ids.copy(),
                filter_group_id=path.filter_group_id,
                limit_filter_ids=path.limit_filter_ids.copy()
            )
            new_flow.paths.append(new_path)
        
        self.flows[new_id] = new_flow
        self._save_flows()
        
        return {"success": True, "flow_id": new_id, "message": "Поток скопирован"}
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ ПУТЯМИ
    # ═══════════════════════════════════════════════════════════════
    
    def add_path(self, flow_id: str, name: str, action: str, **kwargs) -> Dict:
        """Добавление пути в поток"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Поток не найден"}
        
        path_id = hashlib.md5(f"path_{name}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        path = FlowPath(
            id=path_id,
            name=name,
            action=action,
            **kwargs
        )
        
        self.flows[flow_id].paths.append(path)
        self.flows[flow_id].updated_at = datetime.now().isoformat()
        self._save_flows()
        
        return {"success": True, "path_id": path_id, "message": "Путь добавлен"}
    
    def update_path(self, flow_id: str, path_id: str, **kwargs) -> Dict:
        """Обновление пути"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Поток не найден"}
        
        flow = self.flows[flow_id]
        
        for i, path in enumerate(flow.paths):
            if path.id == path_id:
                for key, value in kwargs.items():
                    if hasattr(path, key) and key != "id":
                        setattr(path, key, value)
                
                flow.updated_at = datetime.now().isoformat()
                self._save_flows()
                return {"success": True, "message": "Путь обновлён"}
        
        return {"success": False, "error": "Путь не найден"}
    
    def delete_path(self, flow_id: str, path_id: str) -> Dict:
        """Удаление пути"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Поток не найден"}
        
        flow = self.flows[flow_id]
        
        for i, path in enumerate(flow.paths):
            if path.id == path_id:
                flow.paths.pop(i)
                flow.updated_at = datetime.now().isoformat()
                self._save_flows()
                return {"success": True, "message": "Путь удалён"}
        
        return {"success": False, "error": "Путь не найден"}
    
    def reorder_paths(self, flow_id: str, path_ids: List[str]) -> Dict:
        """Изменение порядка путей"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Поток не найден"}
        
        flow = self.flows[flow_id]
        
        # Создание карты путей
        path_map = {p.id: p for p in flow.paths}
        
        # Новый порядок
        new_paths = []
        for pid in path_ids:
            if pid in path_map:
                new_paths.append(path_map[pid])
        
        # Добавление оставшихся путей
        for path in flow.paths:
            if path.id not in path_ids:
                new_paths.append(path)
        
        flow.paths = new_paths
        flow.updated_at = datetime.now().isoformat()
        self._save_flows()
        
        return {"success": True, "message": "Порядок путей изменён"}
    
    # ═══════════════════════════════════════════════════════════════
    # РАСПРЕДЕЛЕНИЕ ТРАФИКА
    # ═══════════════════════════════════════════════════════════════
    
    def process_click(self, flow_id: str, visitor_data: Dict,
                     filters_manager=None) -> Dict:
        """
        Обработка клика и определение назначения
        
        visitor_data должен содержать:
        - ip, country, city, device_type, os, browser, referrer и т.д.
        - click_id, sub_id для макросов
        
        Возвращает:
        - action: тип действия
        - url: URL для редиректа (если применимо)
        - redirect_type: тип редиректа
        - landing_id: ID лендинга
        - offer_id: ID оффера
        - html: HTML контент
        - path_id: ID выбранного пути
        """
        if flow_id not in self.flows:
            return {
                "action": "show_404",
                "error": "Поток не найден"
            }
        
        flow = self.flows[flow_id]
        
        if flow.status != "active":
            return {
                "action": "show_404",
                "error": "Поток не активен"
            }
        
        # Проверка глобальных фильтров потока
        if filters_manager and flow.filter_ids:
            passed, reason = filters_manager.check_visitor(visitor_data, flow.filter_ids)
            if not passed:
                return {
                    "action": "block",
                    "reason": reason
                }
        
        if filters_manager and flow.filter_group_id:
            passed, reason = filters_manager.check_visitor(
                visitor_data, group_id=flow.filter_group_id
            )
            if not passed:
                return {
                    "action": "block",
                    "reason": reason
                }
        
        # Проверка глобальных лимитов
        if filters_manager and flow.limit_filter_ids:
            reached, reason = filters_manager.check_limits(flow.limit_filter_ids)
            if reached:
                return {
                    "action": flow.default_action,
                    "url": flow.default_url,
                    "reason": reason
                }
        
        # Выбор пути
        eligible_paths = []
        
        for path in flow.paths:
            if not path.enabled:
                continue
            
            # Проверка фильтров пути
            if filters_manager and path.filter_ids:
                passed, _ = filters_manager.check_visitor(visitor_data, path.filter_ids)
                if not passed:
                    continue
            
            if filters_manager and path.filter_group_id:
                passed, _ = filters_manager.check_visitor(
                    visitor_data, group_id=path.filter_group_id
                )
                if not passed:
                    continue
            
            # Проверка лимитов пути
            if filters_manager and path.limit_filter_ids:
                reached, _ = filters_manager.check_limits(path.limit_filter_ids)
                if reached:
                    continue
            
            eligible_paths.append(path)
        
        if not eligible_paths:
            # Нет подходящих путей - действие по умолчанию
            return {
                "action": flow.default_action,
                "url": self._apply_macros(flow.default_url, visitor_data) if flow.default_url else "",
                "redirect_type": flow.default_redirect_type
            }
        
        # Выбор пути по весам
        selected_path = self._select_path_by_weight(eligible_paths)
        
        # Обновление статистики
        selected_path.clicks += 1
        flow.total_clicks += 1
        self._save_flows()
        
        # Инкремент лимитов
        if filters_manager:
            if flow.limit_filter_ids:
                filters_manager.increment_limits(flow.limit_filter_ids, "clicks")
            if selected_path.limit_filter_ids:
                filters_manager.increment_limits(selected_path.limit_filter_ids, "clicks")
        
        # Формирование результата
        result = {
            "action": selected_path.action,
            "path_id": selected_path.id,
            "path_name": selected_path.name,
            "redirect_type": selected_path.redirect_type or flow.default_redirect_type
        }
        
        if selected_path.action == "redirect":
            result["url"] = self._apply_macros(selected_path.redirect_url, visitor_data)
        
        elif selected_path.action == "landing":
            result["landing_id"] = selected_path.landing_id
        
        elif selected_path.action == "offer":
            result["offer_id"] = selected_path.offer_id
        
        elif selected_path.action == "show_html":
            result["html"] = selected_path.html_content
        
        return result
    
    def _select_path_by_weight(self, paths: List[FlowPath]) -> FlowPath:
        """Выбор пути по весам"""
        if len(paths) == 1:
            return paths[0]
        
        total_weight = sum(p.weight for p in paths)
        
        if total_weight == 0:
            return random.choice(paths)
        
        rand = random.randint(1, total_weight)
        current = 0
        
        for path in paths:
            current += path.weight
            if rand <= current:
                return path
        
        return paths[-1]
    
    def _apply_macros(self, url: str, visitor_data: Dict) -> str:
        """Применение макросов к URL"""
        if not url:
            return url
        
        macros = {
            "{click_id}": visitor_data.get("click_id", ""),
            "{sub_id}": visitor_data.get("sub_id", ""),
            "{subid}": visitor_data.get("sub_id", ""),
            "{country}": visitor_data.get("country", ""),
            "{city}": visitor_data.get("city", ""),
            "{region}": visitor_data.get("region", ""),
            "{device}": visitor_data.get("device_type", ""),
            "{os}": visitor_data.get("os", ""),
            "{browser}": visitor_data.get("browser", ""),
            "{ip}": visitor_data.get("ip", ""),
            "{referrer}": visitor_data.get("referrer", ""),
            "{sub1}": visitor_data.get("sub_id_1", ""),
            "{sub2}": visitor_data.get("sub_id_2", ""),
            "{sub3}": visitor_data.get("sub_id_3", ""),
            "{sub4}": visitor_data.get("sub_id_4", ""),
            "{sub5}": visitor_data.get("sub_id_5", ""),
            "{timestamp}": str(int(datetime.now().timestamp())),
            "{random}": str(random.randint(1000000, 9999999))
        }
        
        result = url
        for macro, value in macros.items():
            result = result.replace(macro, str(value))
        
        return result
    
    def get_flow_for_campaign(self, campaign_id: str, visitor_data: Dict = None,
                             filters_manager=None) -> Optional[str]:
        """Получение подходящего потока для кампании"""
        flows = self.get_flows(campaign_id=campaign_id, status="active")
        
        if not flows:
            return None
        
        # Сортировка по приоритету
        flows.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        # Если нет данных посетителя, возвращаем первый поток
        if not visitor_data:
            return flows[0]["id"]
        
        # Проверка фильтров каждого потока
        for flow_dict in flows:
            flow_id = flow_dict["id"]
            flow = self.flows[flow_id]
            
            # Проверка фильтров
            if filters_manager and flow.filter_ids:
                passed, _ = filters_manager.check_visitor(visitor_data, flow.filter_ids)
                if not passed:
                    continue
            
            if filters_manager and flow.filter_group_id:
                passed, _ = filters_manager.check_visitor(
                    visitor_data, group_id=flow.filter_group_id
                )
                if not passed:
                    continue
            
            return flow_id
        
        # Возвращаем первый поток, если ни один не подошёл
        return flows[0]["id"] if flows else None
    
    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    def get_flow_stats(self, flow_id: str) -> Dict:
        """Получение статистики потока"""
        if flow_id not in self.flows:
            return {"error": "Поток не найден"}
        
        flow = self.flows[flow_id]
        
        paths_stats = []
        for path in flow.paths:
            cr = 0
            if path.clicks > 0:
                cr = (path.conversions / path.clicks) * 100
            
            paths_stats.append({
                "id": path.id,
                "name": path.name,
                "action": path.action,
                "weight": path.weight,
                "clicks": path.clicks,
                "conversions": path.conversions,
                "cr": round(cr, 2),
                "enabled": path.enabled
            })
        
        total_cr = 0
        if flow.total_clicks > 0:
            total_cr = (flow.conversions / flow.total_clicks) * 100
        
        return {
            "flow_id": flow_id,
            "name": flow.name,
            "status": flow.status,
            "total_clicks": flow.total_clicks,
            "unique_clicks": flow.unique_clicks,
            "conversions": flow.conversions,
            "cr": round(total_cr, 2),
            "paths": paths_stats
        }
    
    def reset_flow_stats(self, flow_id: str) -> Dict:
        """Сброс статистики потока"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Поток не найден"}
        
        flow = self.flows[flow_id]
        flow.total_clicks = 0
        flow.unique_clicks = 0
        flow.conversions = 0
        
        for path in flow.paths:
            path.clicks = 0
            path.conversions = 0
        
        self._save_flows()
        
        return {"success": True, "message": "Статистика сброшена"}


# Singleton
_tds_flows = None

def get_tds_flows() -> TDSFlows:
    """Получение экземпляра TDS Flows"""
    global _tds_flows
    if _tds_flows is None:
        _tds_flows = TDSFlows()
    return _tds_flows
