#!/usr/bin/env python3
"""
SEO Monster - Priority System
Система приоритетов для задач, источников, агентов и ресурсов
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import heapq
from collections import defaultdict


class PriorityLevel(Enum):
    """Уровни приоритета"""
    CRITICAL = 1  # Критический - выполнить немедленно
    HIGH = 2      # Высокий - выполнить в первую очередь
    MEDIUM = 3    # Средний - стандартный приоритет
    LOW = 4       # Низкий - выполнить когда есть время
    BACKGROUND = 5  # Фоновый - выполнить в свободное время


class TaskType(Enum):
    """Типы задач"""
    KEYWORD_RESEARCH = "keyword_research"
    CONTENT_GENERATION = "content_generation"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TECHNICAL_AUDIT = "technical_audit"
    INDEXING = "indexing"
    BACKLINK_ANALYSIS = "backlink_analysis"
    RANK_TRACKING = "rank_tracking"
    IMAGE_SEARCH = "image_search"
    CONTENT_OPTIMIZATION = "content_optimization"
    SOCIAL_SIGNALS = "social_signals"


class ResourceType(Enum):
    """Типы ресурсов"""
    AI_PROVIDER = "ai_provider"
    IMAGE_PROVIDER = "image_provider"
    SEARCH_API = "search_api"
    INDEXING_API = "indexing_api"
    ANALYTICS_API = "analytics_api"


@dataclass
class PriorityTask:
    """Задача с приоритетом"""
    id: str
    type: TaskType
    priority: PriorityLevel
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    status: str = "pending"
    retries: int = 0
    max_retries: int = 3
    estimated_duration: int = 60  # секунды
    actual_duration: Optional[int] = None
    result: Optional[Any] = None
    
    def __lt__(self, other):
        """Для сравнения в heap"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


@dataclass
class AgentPriority:
    """Приоритет агента"""
    agent_id: str
    name: str
    specialization: List[TaskType]
    priority: int = 5  # 1-10
    performance_score: float = 0.5  # 0-1
    current_load: int = 0
    max_load: int = 5
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    enabled: bool = True


@dataclass
class ResourcePriority:
    """Приоритет ресурса"""
    resource_id: str
    type: ResourceType
    name: str
    priority: int = 5  # 1-10
    rate_limit: int = 100
    current_usage: int = 0
    cost_per_request: float = 0.0
    reliability_score: float = 1.0
    enabled: bool = True


class PriorityQueue:
    """Очередь задач с приоритетами"""
    
    def __init__(self):
        self._queue: List[PriorityTask] = []
        self._task_map: Dict[str, PriorityTask] = {}
        self._completed: List[PriorityTask] = []
    
    def push(self, task: PriorityTask):
        """Добавление задачи в очередь"""
        heapq.heappush(self._queue, task)
        self._task_map[task.id] = task
    
    def pop(self) -> Optional[PriorityTask]:
        """Извлечение задачи с наивысшим приоритетом"""
        while self._queue:
            task = heapq.heappop(self._queue)
            if task.id in self._task_map:
                del self._task_map[task.id]
                return task
        return None
    
    def peek(self) -> Optional[PriorityTask]:
        """Просмотр задачи без извлечения"""
        return self._queue[0] if self._queue else None
    
    def update_priority(self, task_id: str, new_priority: PriorityLevel):
        """Обновление приоритета задачи"""
        if task_id in self._task_map:
            task = self._task_map[task_id]
            task.priority = new_priority
            # Перестраиваем heap
            heapq.heapify(self._queue)
    
    def remove(self, task_id: str) -> bool:
        """Удаление задачи из очереди"""
        if task_id in self._task_map:
            del self._task_map[task_id]
            return True
        return False
    
    def complete(self, task: PriorityTask):
        """Отметка задачи как выполненной"""
        task.status = "completed"
        self._completed.append(task)
    
    def get_pending(self) -> List[PriorityTask]:
        """Получение всех ожидающих задач"""
        return list(self._task_map.values())
    
    def get_by_type(self, task_type: TaskType) -> List[PriorityTask]:
        """Получение задач по типу"""
        return [t for t in self._task_map.values() if t.type == task_type]
    
    def __len__(self):
        return len(self._task_map)


class PriorityManager:
    """Главный менеджер приоритетов"""
    
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.agents: Dict[str, AgentPriority] = {}
        self.resources: Dict[str, ResourcePriority] = {}
        
        # Настройки приоритетов по умолчанию
        self.task_priorities: Dict[TaskType, PriorityLevel] = {
            TaskType.KEYWORD_RESEARCH: PriorityLevel.HIGH,
            TaskType.CONTENT_GENERATION: PriorityLevel.HIGH,
            TaskType.COMPETITOR_ANALYSIS: PriorityLevel.MEDIUM,
            TaskType.TECHNICAL_AUDIT: PriorityLevel.MEDIUM,
            TaskType.INDEXING: PriorityLevel.HIGH,
            TaskType.BACKLINK_ANALYSIS: PriorityLevel.LOW,
            TaskType.RANK_TRACKING: PriorityLevel.MEDIUM,
            TaskType.IMAGE_SEARCH: PriorityLevel.MEDIUM,
            TaskType.CONTENT_OPTIMIZATION: PriorityLevel.MEDIUM,
            TaskType.SOCIAL_SIGNALS: PriorityLevel.LOW,
        }
        
        # Веса для расчёта приоритета агента
        self.agent_weights = {
            "performance_score": 0.3,
            "success_rate": 0.3,
            "load_factor": 0.2,
            "response_time": 0.2
        }
        
        # Веса для расчёта приоритета ресурса
        self.resource_weights = {
            "reliability": 0.4,
            "cost": 0.2,
            "availability": 0.4
        }
        
        # История для обучения
        self.task_history: List[Dict] = []
        self.learning_enabled = True
    
    # ==================== УПРАВЛЕНИЕ ЗАДАЧАМИ ====================
    
    def create_task(
        self,
        task_type: TaskType,
        data: Dict[str, Any],
        priority: Optional[PriorityLevel] = None,
        deadline: Optional[datetime] = None,
        dependencies: Optional[List[str]] = None
    ) -> PriorityTask:
        """Создание новой задачи"""
        
        task_id = f"{task_type.value}_{datetime.now().timestamp()}"
        
        # Определяем приоритет
        if priority is None:
            priority = self._calculate_task_priority(task_type, data, deadline)
        
        task = PriorityTask(
            id=task_id,
            type=task_type,
            priority=priority,
            data=data,
            deadline=deadline,
            dependencies=dependencies or []
        )
        
        self.task_queue.push(task)
        return task
    
    def _calculate_task_priority(
        self,
        task_type: TaskType,
        data: Dict[str, Any],
        deadline: Optional[datetime]
    ) -> PriorityLevel:
        """Расчёт приоритета задачи на основе различных факторов"""
        
        base_priority = self.task_priorities.get(task_type, PriorityLevel.MEDIUM)
        
        # Повышаем приоритет если есть дедлайн
        if deadline:
            time_until_deadline = (deadline - datetime.now()).total_seconds()
            if time_until_deadline < 3600:  # Менее часа
                return PriorityLevel.CRITICAL
            elif time_until_deadline < 86400:  # Менее суток
                if base_priority.value > PriorityLevel.HIGH.value:
                    return PriorityLevel.HIGH
        
        # Учитываем важность ключевого слова
        if "keyword" in data:
            keyword_volume = data.get("search_volume", 0)
            if keyword_volume > 10000:
                if base_priority.value > PriorityLevel.HIGH.value:
                    return PriorityLevel.HIGH
        
        return base_priority
    
    def get_next_task(self) -> Optional[PriorityTask]:
        """Получение следующей задачи для выполнения"""
        
        # Проверяем зависимости
        while True:
            task = self.task_queue.peek()
            if task is None:
                return None
            
            # Проверяем, выполнены ли все зависимости
            if self._check_dependencies(task):
                return self.task_queue.pop()
            else:
                # Понижаем приоритет задачи с невыполненными зависимостями
                self.task_queue.pop()
                task.priority = PriorityLevel(min(task.priority.value + 1, 5))
                self.task_queue.push(task)
    
    def _check_dependencies(self, task: PriorityTask) -> bool:
        """Проверка выполнения зависимостей"""
        for dep_id in task.dependencies:
            if dep_id in self.task_queue._task_map:
                return False
        return True
    
    def complete_task(self, task: PriorityTask, result: Any, duration: int):
        """Завершение задачи"""
        task.result = result
        task.actual_duration = duration
        task.status = "completed"
        
        self.task_queue.complete(task)
        
        # Сохраняем в историю для обучения
        if self.learning_enabled:
            self.task_history.append({
                "task_id": task.id,
                "type": task.type.value,
                "priority": task.priority.value,
                "duration": duration,
                "estimated_duration": task.estimated_duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            # Обучаемся на результатах
            self._learn_from_task(task)
    
    def fail_task(self, task: PriorityTask, error: str):
        """Обработка неудачной задачи"""
        task.retries += 1
        
        if task.retries < task.max_retries:
            # Повторяем с повышенным приоритетом
            task.priority = PriorityLevel(max(task.priority.value - 1, 1))
            self.task_queue.push(task)
        else:
            task.status = "failed"
            self.task_history.append({
                "task_id": task.id,
                "type": task.type.value,
                "priority": task.priority.value,
                "success": False,
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
    
    # ==================== УПРАВЛЕНИЕ АГЕНТАМИ ====================
    
    def register_agent(self, agent: AgentPriority):
        """Регистрация агента"""
        self.agents[agent.agent_id] = agent
    
    def get_best_agent(self, task_type: TaskType) -> Optional[AgentPriority]:
        """Получение лучшего агента для задачи"""
        
        suitable_agents = [
            a for a in self.agents.values()
            if a.enabled and task_type in a.specialization and a.current_load < a.max_load
        ]
        
        if not suitable_agents:
            return None
        
        # Рассчитываем score для каждого агента
        scored_agents = []
        for agent in suitable_agents:
            score = self._calculate_agent_score(agent)
            scored_agents.append((score, agent))
        
        # Возвращаем агента с наивысшим score
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        return scored_agents[0][1]
    
    def _calculate_agent_score(self, agent: AgentPriority) -> float:
        """Расчёт score агента"""
        
        # Нормализуем load factor (чем меньше загрузка, тем лучше)
        load_factor = 1 - (agent.current_load / agent.max_load)
        
        # Нормализуем время ответа (предполагаем макс 10 секунд)
        response_factor = 1 - min(agent.avg_response_time / 10, 1)
        
        score = (
            self.agent_weights["performance_score"] * agent.performance_score +
            self.agent_weights["success_rate"] * agent.success_rate +
            self.agent_weights["load_factor"] * load_factor +
            self.agent_weights["response_time"] * response_factor
        )
        
        # Учитываем базовый приоритет
        score *= (agent.priority / 10)
        
        return score
    
    def update_agent_stats(
        self,
        agent_id: str,
        success: bool,
        response_time: float
    ):
        """Обновление статистики агента"""
        
        if agent_id not in self.agents:
            return
        
        agent = self.agents[agent_id]
        
        # Обновляем success rate (скользящее среднее)
        alpha = 0.1
        agent.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * agent.success_rate
        
        # Обновляем среднее время ответа
        agent.avg_response_time = alpha * response_time + (1 - alpha) * agent.avg_response_time
        
        # Обновляем performance score
        agent.performance_score = (agent.success_rate + (1 - min(agent.avg_response_time / 10, 1))) / 2
    
    def set_agent_priority(self, agent_id: str, priority: int):
        """Установка приоритета агента"""
        if agent_id in self.agents:
            self.agents[agent_id].priority = max(1, min(10, priority))
    
    # ==================== УПРАВЛЕНИЕ РЕСУРСАМИ ====================
    
    def register_resource(self, resource: ResourcePriority):
        """Регистрация ресурса"""
        self.resources[resource.resource_id] = resource
    
    def get_best_resource(self, resource_type: ResourceType) -> Optional[ResourcePriority]:
        """Получение лучшего ресурса по типу"""
        
        suitable_resources = [
            r for r in self.resources.values()
            if r.enabled and r.type == resource_type and r.current_usage < r.rate_limit
        ]
        
        if not suitable_resources:
            return None
        
        # Рассчитываем score для каждого ресурса
        scored_resources = []
        for resource in suitable_resources:
            score = self._calculate_resource_score(resource)
            scored_resources.append((score, resource))
        
        scored_resources.sort(key=lambda x: x[0], reverse=True)
        return scored_resources[0][1]
    
    def _calculate_resource_score(self, resource: ResourcePriority) -> float:
        """Расчёт score ресурса"""
        
        # Нормализуем доступность
        availability = 1 - (resource.current_usage / resource.rate_limit)
        
        # Нормализуем стоимость (предполагаем макс $0.01 за запрос)
        cost_factor = 1 - min(resource.cost_per_request / 0.01, 1)
        
        score = (
            self.resource_weights["reliability"] * resource.reliability_score +
            self.resource_weights["cost"] * cost_factor +
            self.resource_weights["availability"] * availability
        )
        
        # Учитываем базовый приоритет
        score *= (resource.priority / 10)
        
        return score
    
    def use_resource(self, resource_id: str):
        """Отметка использования ресурса"""
        if resource_id in self.resources:
            self.resources[resource_id].current_usage += 1
    
    def reset_resource_usage(self):
        """Сброс счётчиков использования (вызывать периодически)"""
        for resource in self.resources.values():
            resource.current_usage = 0
    
    # ==================== ОБУЧЕНИЕ И ОПТИМИЗАЦИЯ ====================
    
    def _learn_from_task(self, task: PriorityTask):
        """Обучение на основе выполненной задачи"""
        
        if task.actual_duration and task.estimated_duration:
            # Корректируем оценку времени для данного типа задач
            ratio = task.actual_duration / task.estimated_duration
            
            # Если задача выполнялась дольше ожидаемого, повышаем приоритет
            if ratio > 1.5 and task.type in self.task_priorities:
                current = self.task_priorities[task.type]
                if current.value > 1:
                    self.task_priorities[task.type] = PriorityLevel(current.value - 1)
    
    def optimize_priorities(self):
        """Оптимизация приоритетов на основе истории"""
        
        if len(self.task_history) < 100:
            return
        
        # Анализируем последние 100 задач
        recent = self.task_history[-100:]
        
        # Группируем по типу
        by_type = defaultdict(list)
        for record in recent:
            by_type[record["type"]].append(record)
        
        # Корректируем приоритеты
        for task_type_str, records in by_type.items():
            task_type = TaskType(task_type_str)
            
            success_rate = sum(1 for r in records if r["success"]) / len(records)
            avg_duration = sum(r.get("duration", 0) for r in records) / len(records)
            
            # Если много неудач, повышаем приоритет
            if success_rate < 0.7:
                current = self.task_priorities.get(task_type, PriorityLevel.MEDIUM)
                if current.value > 1:
                    self.task_priorities[task_type] = PriorityLevel(current.value - 1)
    
    # ==================== СТАТИСТИКА И ОТЧЁТЫ ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики системы приоритетов"""
        
        return {
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.task_queue._completed),
            "active_agents": sum(1 for a in self.agents.values() if a.enabled),
            "total_agents": len(self.agents),
            "active_resources": sum(1 for r in self.resources.values() if r.enabled),
            "total_resources": len(self.resources),
            "task_priorities": {t.value: p.value for t, p in self.task_priorities.items()},
            "history_size": len(self.task_history)
        }
    
    def get_task_distribution(self) -> Dict[str, int]:
        """Распределение задач по приоритетам"""
        
        distribution = defaultdict(int)
        for task in self.task_queue.get_pending():
            distribution[task.priority.name] += 1
        return dict(distribution)
    
    def export_config(self) -> Dict[str, Any]:
        """Экспорт конфигурации приоритетов"""
        
        return {
            "task_priorities": {t.value: p.value for t, p in self.task_priorities.items()},
            "agent_weights": self.agent_weights,
            "resource_weights": self.resource_weights,
            "agents": [
                {
                    "id": a.agent_id,
                    "name": a.name,
                    "priority": a.priority,
                    "enabled": a.enabled
                }
                for a in self.agents.values()
            ],
            "resources": [
                {
                    "id": r.resource_id,
                    "name": r.name,
                    "type": r.type.value,
                    "priority": r.priority,
                    "enabled": r.enabled
                }
                for r in self.resources.values()
            ]
        }
    
    def import_config(self, config: Dict[str, Any]):
        """Импорт конфигурации приоритетов"""
        
        if "task_priorities" in config:
            for task_type_str, priority_value in config["task_priorities"].items():
                try:
                    task_type = TaskType(task_type_str)
                    self.task_priorities[task_type] = PriorityLevel(priority_value)
                except ValueError:
                    pass
        
        if "agent_weights" in config:
            self.agent_weights.update(config["agent_weights"])
        
        if "resource_weights" in config:
            self.resource_weights.update(config["resource_weights"])


# Глобальный экземпляр
priority_manager = PriorityManager()
