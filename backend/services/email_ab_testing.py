"""
Email A/B Testing Module with Auto-Optimization
Модуль A/B тестирования контента писем с автоматической оптимизацией по открываемости
"""

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random
import math
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


class TestStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    WINNER_SELECTED = "winner_selected"


class OptimizationMetric(str, Enum):
    OPEN_RATE = "open_rate"
    CLICK_RATE = "click_rate"
    CONVERSION_RATE = "conversion_rate"


class VariantType(str, Enum):
    SUBJECT = "subject"
    CONTENT = "content"
    PREHEADER = "preheader"
    SENDER_NAME = "sender_name"
    SEND_TIME = "send_time"


@dataclass
class EmailVariant:
    """Вариант письма для A/B теста"""
    id: str
    name: str
    variant_type: VariantType
    subject: str
    preheader: str
    content_id: str
    sender_name: str
    send_time: Optional[str] = None
    
    # Статистика
    sent_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    converted_count: int = 0

    bounced_count: int = 0
    unsubscribed_count: int = 0
    
    @property
    def open_rate(self) -> float:
        if self.delivered_count == 0:
            return 0.0
        return (self.opened_count / self.delivered_count) * 100
    
    @property
    def click_rate(self) -> float:
        if self.delivered_count == 0:
            return 0.0
        return (self.clicked_count / self.delivered_count) * 100
    
    @property
    def conversion_rate(self) -> float:
        if self.delivered_count == 0:
            return 0.0
        return (self.converted_count / self.delivered_count) * 100
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "open_rate": round(self.open_rate, 2),
            "click_rate": round(self.click_rate, 2),
            "conversion_rate": round(self.conversion_rate, 2)
        }


@dataclass
class ABTest:
    """A/B тест для email кампании"""
    id: str
    name: str
    description: str
    campaign_id: str
    variants: List[EmailVariant]
    status: TestStatus
    optimization_metric: OptimizationMetric
    
    # Настройки теста
    test_size_percent: float = 20.0  # % аудитории для теста
    auto_select_winner: bool = True
    min_sample_size: int = 100

    confidence_level: float = 95.0  # Уровень доверия для статистической значимости
    max_test_duration_hours: int = 24
    
    # Результаты
    winner_variant_id: Optional[str] = None
    statistical_significance: float = 0.0
    
    # Временные метки
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self
) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "campaign_id": self.campaign_id,
            "variants": [v.to_dict() if hasattr(v, 'to_dict') else asdict(v) for v in self.variants],
            "status": self.status.value if isinstance(self.status, TestStatus) else self.status,
            "optimization_metric": self.optimization_metric.value if isinstance(self.optimization_metric, OptimizationMetric) else self.optimization_metric,
            "test_size_percent": self.test_size_percent,
            "auto_select_winner": self.auto_select_winner,
            "min_sample_size": self.min_sample_size,
            "confidence_level": self.confidence_level,
            "max_test_duration_hours": self.max_test_duration_hours,
            "winner_variant_id": self.winner_variant_id,
            "statistical_significance": self.statistical_significance,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


class EmailABTestingService:
    """Сервис A/B тестирования email с автооптимизацией"""
    
    def __init__(self):
        self.tests: Dict[str, ABTest] = {}
        self.tracking_pixels: Dict[str, Dict] = {}
        self.click_tracking: Dict[str, Dict] = {}
        self.auto_optimization_enabled = True
        self.optimization_check_interval = 300
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных из файла"""
        try:
            filepath = os.path.join(DATA_DIR, 'ab_tests.json')
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for test_data in data.get('tests', []):
                        variants = []
                        for v in test_data.get('variants', []):
                            variants.append(EmailVariant(
                                id=v['id'],
                                name=v['name'],
                                variant_type=VariantType(v['variant_type']),
                                subject=v['subject'],
                                preheader=v['preheader'],
                                content_id=v['content_id'],
                                sender_name=v['sender_name'],
                                send_time=v.get('send_time'),
                                sent_count=v.get('sent_count', 0),
                                delivered_count=v.get('delivered_count', 0),
                                opened_count=v.get('opened_count', 0),
                                clicked_count=v.get('clicked_count', 0),
                                converted_count=v.get('converted_count', 0),
                                bounced_count=v.get('bounced_count', 0),
                                unsubscribed_count=v.get('unsubscribed_count', 0)
                            ))
                        
                        test = ABTest(
                            id=test_data['id'],
                            name=test_data['name'],
                            description=test_data.get('description', ''),
                            campaign_id=test_data['campaign_id'],
                            variants=variants,
                            status=TestStatus(test_data['status']),
                            optimization_metric=OptimizationMetric(test_data['optimization_metric']),
                            test_size_percent=test_data.get('test_size_percent', 20.0),
                            auto_select_winner=test_data.get('auto_select_winner', True),
                            min_sample_size=test_data.get('min_sample_size', 100),
                            confidence_level=test_data.get('confidence_level', 95.0),
                            max_test_duration_hours=test_data.get('max_test_duration_hours', 24),
                            winner_variant_id=test_data.get('winner_variant_id'),
                            statistical_significance=test_data.get('statistical_significance', 0.0),
                            created_at=test_data.get('created_at', ''),
                            started_at=test_data.get('started_at'),
                            completed_at=test_data.get('completed_at')
                        )
                        self.tests[test.id] = test
                    
                    self.tracking_pixels = data.get('tracking_pixels', {})
                    self.click_tracking = data.get('click_tracking', {})
        except Exception as e:
            print(f"Error loading AB tests data: {e}")
    
    def _save_data(self):
        """Сохранение данных в файл"""
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            filepath = os.path.join(DATA_DIR, 'ab_tests.json')
            data = {
                'tests': [t.to_dict() for t in self.tests.values()],
                'tracking_pixels': self.tracking_pixels,
                'click_tracking': self.click_tracking
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving AB tests data: {e}")
    
    async def create_test(
        self,
        name: str,
        campaign_id: str,
        variants_config: List[Dict],
        optimization_metric: str = "open_rate",
        test_size_percent: float = 20.0,
        auto_select_winner: bool = True,
        min_sample_size: int = 100,
        confidence_level: float = 95.0,
        max_test_duration_hours: int = 24,
        description: str = ""
    ) -> ABTest:
        """Создание нового A/B теста"""
        
        test_id = str(uuid.uuid4())[:8]
        
        variants = []
        for i, config in enumerate(variants_config):
            variant = EmailVariant(
                id=str(uuid.uuid4())[:8],
                name=config.get('name', f'Variant {chr(65 + i)}'),
                variant_type=VariantType(config.get('variant_type', 'subject')),
                subject=config.get('subject', ''),
                preheader=config.get('preheader', ''),
                content_id=config.get('content_id', ''),
                sender_name=config.get('sender_name', ''),
                send_time=config.get('send_time')
            )
            variants.append(variant)
        
        test = ABTest(
            id=test_id,
            name=name,
            description=description,
            campaign_id=campaign_id,
            variants=variants,
            status=TestStatus.DRAFT,
            optimization_metric=OptimizationMetric(optimization_metric),
            test_size_percent=test_size_percent,
            auto_select_winner=auto_select_winner,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
            max_test_duration_hours=max_test_duration_hours
        )
        
        self.tests[test_id] = test
        self._save_data()
        
        return test
    
    async def start_test(self, test_id: str) -> Dict:
        """Запуск A/B теста"""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        
        if test.status == TestStatus.RUNNING:
            return {"success": False, "error": "Test is already running"}
        
        test.status = TestStatus.RUNNING
        test.started_at = datetime.now().isoformat()
        
        self._save_data()
        
        # Запуск фоновой задачи автооптимизации
        if test.auto_select_winner:
            asyncio.create_task(self._auto_optimization_loop(test_id))
        
        return {"success": True, "test": test.to_dict()}
    
    async def pause_test(self, test_id: str) -> Dict:
        """Приостановка теста"""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        test.status = TestStatus.PAUSED
        self._save_data()
        
        return {"success": True, "test": test.to_dict()}
    
    async def complete_test(self, test_id: str, winner_variant_id: Optional[str] = None) -> Dict:
        """Завершение теста и выбор победителя"""
        if test_id not in self.tests:
            return {"success": False, "error": "Test not found"}
        
        test = self.tests[test_id]
        
        # Если победитель не указан, выбираем автоматически
        if not winner_variant_id:
            winner = self._select_winner(test)
            if winner:
                winner_variant_id = winner.id
        
        test.status = TestStatus.WINNER_SELECTED
        test.winner_variant_id = winner_variant_id
        test.completed_at = datetime.now().isoformat()
        
        self._save_data()
        
        return {
            "success": True,
            "test": test.to_dict(),
            "winner": self._get_variant_by_id(test, winner_variant_id).to_dict() if winner_variant_id else None
        }
    
    def _select_winner(self, test: ABTest) -> Optional[EmailVariant]:
        """Выбор победителя на основе метрики оптимизации"""
        if not test.variants:
            return None
        
        metric = test.optimization_metric
        
        best_variant = None
        best_value = -1
        
        for variant in test.variants:
            if metric == OptimizationMetric.OPEN_RATE:
                value = variant.open_rate
            elif metric == OptimizationMetric.CLICK_RATE:
                value = variant.click_rate
            elif metric == OptimizationMetric.CONVERSION_RATE:
                value = variant.conversion_rate
            else:
                value = variant.open_rate
            
            if value > best_value:
                best_value = value
                best_variant = variant
        
        return best_variant
    
    def _get_variant_by_id(self, test: ABTest, variant_id: str) -> Optional[EmailVariant]:
        """Получение варианта по ID"""
        for variant in test.variants:
            if variant.id == variant_id:
                return variant
        return None
    
    async def _auto_optimization_loop(self, test_id: str):
        """Фоновый цикл автоматической оптимизации"""
        while True:
            await asyncio.sleep(self.optimization_check_interval)
            
            if test_id not in self.tests:
                break
            
            test = self.tests[test_id]
            
            if test.status != TestStatus.RUNNING:
                break
            
            # Проверка условий завершения теста
            should_complete, reason = self._check_completion_conditions(test)
            
            if should_complete:
                await self.complete_test(test_id)
                print(f"A/B Test {test_id} auto-completed: {reason}")
                break
    
    def _check_completion_conditions(self, test: ABTest) -> tuple:
        """Проверка условий для автоматического завершения теста"""
        
        # 1. Проверка времени
        if test.started_at:
            started = datetime.fromisoformat(test.started_at)
            elapsed_hours = (datetime.now() - started).total_seconds() / 3600
            if elapsed_hours >= test.max_test_duration_hours:
                return True, "max_duration_reached"
        
        # 2. Проверка минимального размера выборки
        total_delivered = sum(v.delivered_count for v in test.variants)
        if total_delivered < test.min_sample_size * len(test.variants):
            return False, "insufficient_sample"
        
        # 3. Проверка статистической значимости
        significance = self._calculate_statistical_significance(test)
        test.statistical_significance = significance
        self._save_data()
        
        if significance >= test.confidence_level:
            return True, f"statistical_significance_{significance:.1f}%"
        
        return False, "test_in_progress"
    
    def _calculate_statistical_significance(self, test: ABTest) -> float:
        """Расчет статистической значимости между вариантами (Z-test)"""
        if len(test.variants) < 2:
            return 0.0
        
        # Берем два лучших варианта для сравнения
        sorted_variants = sorted(
            test.variants,
            key=lambda v: v.open_rate if test.optimization_metric == OptimizationMetric.OPEN_RATE else v.click_rate,
            reverse=True
        )
        
        v1 = sorted_variants[0]
        v2 = sorted_variants[1]
        
        n1 = v1.delivered_count
        n2 = v2.delivered_count
        
        if n1 == 0 or n2 == 0:
            return 0.0
        
        # Получаем метрики
        if test.optimization_metric == OptimizationMetric.OPEN_RATE:
            p1 = v1.opened_count / n1
            p2 = v2.opened_count / n2
        elif test.optimization_metric == OptimizationMetric.CLICK_RATE:
            p1 = v1.clicked_count / n1
            p2 = v2.clicked_count / n2
        else:
            p1 = v1.converted_count / n1
            p2 = v2.converted_count / n2
        
        # Pooled proportion
        p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
        
        if p_pool == 0 or p_pool == 1:
            return 0.0
        
        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        if se == 0:
            return 0.0
        
        # Z-score
        z = abs(p1 - p2) / se
        
        # Конвертация Z-score в уровень доверия (приблизительно)
        # Z=1.645 -> 90%, Z=1.96 -> 95%, Z=2.576 -> 99%
        if z >= 2.576:
            return 99.0
        elif z >= 1.96:
            return 95.0 + (z - 1.96) / (2.576 - 1.96) * 4
        elif z >= 1.645:
            return 90.0 + (z - 1.645) / (1.96 - 1.645) * 5
        elif z >= 1.28:
            return 80.0 + (z - 1.28) / (1.645 - 1.28) * 10
        else:
            return min(z / 1.28 * 80, 80)
    
    def generate_tracking_pixel(self, test_id: str, variant_id: str, recipient_email: str) -> str:
        """Генерация tracking pixel для отслеживания открытий"""
        pixel_id = str(uuid.uuid4())
        
        self.tracking_pixels[pixel_id] = {
            "test_id": test_id,
            "variant_id": variant_id,
            "recipient": recipient_email,
            "created_at": datetime.now().isoformat(),
            "opened": False,
            "opened_at": None
        }
        
        self._save_data()
        
        return pixel_id
    
    def generate_click_tracking_url(self, test_id: str, variant_id: str, recipient_email: str, original_url: str) -> str:
        """Генерация URL для отслеживания кликов"""
        click_id = str(uuid.uuid4())
        
        self.click_tracking[click_id] = {
            "test_id": test_id,
            "variant_id": variant_id,
            "recipient": recipient_email,
            "original_url": original_url,
            "created_at": datetime.now().isoformat(),
            "clicked": False,
            "clicked_at": None
        }
        
        self._save_data()
        
        return click_id
    
    async def track_open(self, pixel_id: str) -> bool:
        """Регистрация открытия письма"""
        if pixel_id not in self.tracking_pixels:
            return False
        
        pixel = self.tracking_pixels[pixel_id]
        
        if pixel["opened"]:
            return True  # Уже зарегистрировано
        
        pixel["opened"] = True
        pixel["opened_at"] = datetime.now().isoformat()
        
        # Обновляем статистику варианта
        test_id = pixel["test_id"]
        variant_id = pixel["variant_id"]
        
        if test_id in self.tests:
            test = self.tests[test_id]
            variant = self._get_variant_by_id(test, variant_id)
            if variant:
                variant.opened_count += 1
        
        self._save_data()
        return True
    
    async def track_click(self, click_id: str) -> Optional[str]:
        """Регистрация клика и возврат оригинального URL"""
        if click_id not in self.click_tracking:
            return None
        
        click = self.click_tracking[click_id]
        
        if not click["clicked"]:
            click["clicked"] = True
            click["clicked_at"] = datetime.now().isoformat()
            
            # Обновляем статистику варианта
            test_id = click["test_id"]
            variant_id = click["variant_id"]
            
            if test_id in self.tests:
                test = self.tests[test_id]
                variant = self._get_variant_by_id(test, variant_id)
                if variant:
                    variant.clicked_count += 1
            
            self._save_data()
        
        return click["original_url"]
    
    async def track_conversion(self, test_id: str, variant_id: str, recipient_email: str) -> bool:
        """Регистрация конверсии"""
        if test_id not in self.tests:
            return False
        
        test = self.tests[test_id]
        variant = self._get_variant_by_id(test, variant_id)
        
        if variant:
            variant.converted_count += 1
            self._save_data()
            return True
        
        return False
    
    async def record_send(self, test_id: str, variant_id: str, count: int = 1) -> bool:
        """Регистрация отправки писем"""
        if test_id not in self.tests:
            return False
        
        test = self.tests[test_id]
        variant = self._get_variant_by_id(test, variant_id)
        
        if variant:
            variant.sent_count += count
            variant.delivered_count += count  # Упрощение, в реальности нужен webhook
            self._save_data()
            return True
        
        return False
    
    async def get_test(self, test_id: str) -> Optional[Dict]:
        """Получение информации о тесте"""
        if test_id not in self.tests:
            return None
        return self.tests[test_id].to_dict()
    
    async def get_all_tests(self) -> List[Dict]:
        """Получение всех тестов"""
        return [t.to_dict() for t in self.tests.values()]
    
    async def get_test_results(self, test_id: str) -> Dict:
        """Получение результатов теста с аналитикой"""
        if test_id not in self.tests:
            return {"error": "Test not found"}
        
        test = self.tests[test_id]
        
        # Сортируем варианты по метрике оптимизации
        metric = test.optimization_metric
        sorted_variants = sorted(
            test.variants,
            key=lambda v: getattr(v, metric.value.replace('_rate', '_rate')) if hasattr(v, metric.value) else v.open_rate,
            reverse=True
        )
        
        # Рассчитываем улучшение
        if len(sorted_variants) >= 2:
            best = sorted_variants[0]
            baseline = sorted_variants[-1]
            
            if metric == OptimizationMetric.OPEN_RATE:
                best_rate = best.open_rate
                baseline_rate = baseline.open_rate
            elif metric == OptimizationMetric.CLICK_RATE:
                best_rate = best.click_rate
                baseline_rate = baseline.click_rate
            else:
                best_rate = best.conversion_rate
                baseline_rate = baseline.conversion_rate
            
            improvement = ((best_rate - baseline_rate) / baseline_rate * 100) if baseline_rate > 0 else 0
        else:
            improvement = 0
        
        return {
            "test": test.to_dict(),
            "variants_ranked": [v.to_dict() for v in sorted_variants],
            "statistical_significance": test.statistical_significance,
            "improvement_percent": round(improvement, 2),
            "winner": self._get_variant_by_id(test, test.winner_variant_id).to_dict() if test.winner_variant_id else None,
            "recommendation": self._generate_recommendation(test)
        }
    
    def _generate_recommendation(self, test: ABTest) -> str:
        """Генерация рекомендации на основе результатов"""
        if test.status == TestStatus.DRAFT:
            return "Тест еще не запущен. Запустите тест для сбора данных."
        
        if test.status == TestStatus.RUNNING:
            total_delivered = sum(v.delivered_count for v in test.variants)
            if total_delivered < test.min_sample_size:
                return f"Недостаточно данных. Отправлено {total_delivered} из {test.min_sample_size} минимально необходимых."
            
            if test.statistical_significance < test.confidence_level:
                return f"Статистическая значимость {test.statistical_significance:.1f}% ниже требуемого уровня {test.confidence_level}%. Продолжайте тест."
            
            return "Достигнута статистическая значимость. Можно выбрать победителя."
        
        if test.status == TestStatus.WINNER_SELECTED and test.winner_variant_id:
            winner = self._get_variant_by_id(test, test.winner_variant_id)
            if winner:
                return f"Победитель: {winner.name} с {winner.open_rate:.1f}% открываемостью. Используйте этот вариант для основной рассылки."
        
        return "Тест завершен."
    
    async def delete_test(self, test_id: str) -> bool:
        """Удаление теста"""
        if test_id in self.tests:
            del self.tests[test_id]
            self._save_data()
            return True
        return False
    
    async def get_stats(self) -> Dict:
        """Получение общей статистики A/B тестов"""
        total_tests = len(self.tests)
        running_tests = sum(1 for t in self.tests.values() if t.status == TestStatus.RUNNING)
        completed_tests = sum(1 for t in self.tests.values() if t.status in [TestStatus.COMPLETED, TestStatus.WINNER_SELECTED])
        
        total_variants = sum(len(t.variants) for t in self.tests.values())
        total_opens = sum(v.opened_count for t in self.tests.values() for v in t.variants)
        total_clicks = sum(v.clicked_count for t in self.tests.values() for v in t.variants)
        
        return {
            "total_tests": total_tests,
            "running_tests": running_tests,
            "completed_tests": completed_tests,
            "draft_tests": total_tests - running_tests - completed_tests,
            "total_variants": total_variants,
            "total_opens_tracked": total_opens,
            "total_clicks_tracked": total_clicks,
            "auto_optimization_enabled": self.auto_optimization_enabled
        }


# Глобальный экземпляр сервиса
ab_testing_service = EmailABTestingService()
