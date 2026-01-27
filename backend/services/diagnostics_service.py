"""
SEO Monster - Comprehensive Diagnostics & Auto-Fix Service
Расширенный модуль диагностики и автоматического исправления ошибок
Версия 2.0 - Полная проверка всех компонентов системы
"""

import asyncio
import json
import os
import sys
import traceback
import importlib
import subprocess
import socket
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiagnosticStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FIXED = "fixed"
    PENDING = "pending"
    SKIPPED = "skipped"


class DiagnosticCategory(str, Enum):
    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    SERVICES = "services"
    CONFIGURATION = "configuration"
    DEPENDENCIES = "dependencies"
    PERFORMANCE = "performance"
    SECURITY = "security"
    EMAIL = "email"
    AI = "ai"
    TDS = "tds"
    INTEGRATIONS = "integrations"
    NETWORK = "network"


class DiagnosticSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DiagnosticResult:
    """Результат диагностики"""
    check_id: str
    category: DiagnosticCategory
    name: str
    status: DiagnosticStatus
    message: str
    details: Optional[Dict] = None
    fix_available: bool = False
    fix_applied: bool = False
    severity: DiagnosticSeverity = DiagnosticSeverity.MEDIUM
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = None
    duration_ms: float = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class FixResult:
    """Результат исправления"""
    check_id: str
    success: bool
    message: str
    before_status: DiagnosticStatus
    after_status: DiagnosticStatus
    actions_taken: List[str] = field(default_factory=list)
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class SystemHealthReport:
    """Отчет о здоровье системы"""
    overall_status: DiagnosticStatus
    health_score: int  # 0-100
    total_checks: int
    passed_checks: int
    warning_checks: int
    error_checks: int
    critical_checks: int
    fixed_checks: int
    categories_summary: Dict[str, Dict]
    top_issues: List[Dict]
    recommendations: List[str]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class DiagnosticsService:
    """Расширенный сервис диагностики и автоисправления"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "/home/ubuntu/seo_monster/backend/data/diagnostics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы данных
        self.config_file = self.data_dir / "diagnostics_config.json"
        self.history_file = self.data_dir / "diagnostics_history.json"
        self.fixes_file = self.data_dir / "fixes_history.json"
        self.reports_file = self.data_dir / "health_reports.json"
        
        # Загружаем конфигурацию
        self.config = self._load_config()
        self.history: List[Dict] = self._load_json(self.history_file, [])
        self.fixes_history: List[Dict] = self._load_json(self.fixes_file, [])
        self.health_reports: List[Dict] = self._load_json(self.reports_file, [])
        
        # Состояние автоматического режима
        self.auto_mode_enabled = self.config.get("auto_mode_enabled", False)
        self.auto_fix_enabled = self.config.get("auto_fix_enabled", False)
        self.check_interval = self.config.get("check_interval", 300)
        
        # Фоновый поток для автоматической диагностики
        self._auto_thread: Optional[threading.Thread] = None
        self._stop_auto = threading.Event()
        
        # Регистрация проверок и исправлений
        self.checks: Dict[str, Dict] = {}
        self.fixes: Dict[str, Callable] = {}
        self._register_all_checks()
        
        # Кэш последних результатов
        self._last_results: Dict[str, DiagnosticResult] = {}
        self._last_full_check: Optional[datetime] = None
        
        # Запуск автоматического режима если включен
        if self.auto_mode_enabled:
            self.start_auto_mode()
    
    def _load_config(self) -> Dict:
        """Загрузка конфигурации"""
        default_config = {
            "auto_mode_enabled": False,
            "auto_fix_enabled": False,
            "check_interval": 300,
            "notify_on_error": True,
            "notify_on_critical": True,
            "max_history_size": 1000,
            "max_reports_size": 100,
            "enabled_checks": ["all"],
            "disabled_checks": [],
            "quick_check_ids": [
                "api_health", "disk_space", "memory_usage", 
                "database_connection", "critical_services"
            ],
            "severity_thresholds": {
                "health_score_warning": 70,
                "health_score_critical": 50
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except:
                pass
        
        self._save_json(self.config_file, default_config)
        return default_config
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Загрузка JSON файла"""
        if path.exists():
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, path: Path, data: Any):
        """Сохранение JSON файла"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _save_config(self):
        """Сохранение конфигурации"""
        self._save_json(self.config_file, self.config)
    
    def _register_all_checks(self):
        """Регистрация всех проверок системы"""
        
        # ==================== API ПРОВЕРКИ ====================
        self.register_check("api_health", self._check_api_health, 
                          DiagnosticCategory.API, DiagnosticSeverity.CRITICAL)
        self.register_check("api_endpoints", self._check_api_endpoints, 
                          DiagnosticCategory.API, DiagnosticSeverity.HIGH)
        self.register_check("api_response_time", self._check_api_response_time,
                          DiagnosticCategory.API, DiagnosticSeverity.MEDIUM)
        
        # ==================== ФАЙЛОВАЯ СИСТЕМА ====================
        self.register_check("data_directories", self._check_data_directories, 
                          DiagnosticCategory.FILE_SYSTEM, DiagnosticSeverity.HIGH)
        self.register_check("json_files_integrity", self._check_json_files, 
                          DiagnosticCategory.FILE_SYSTEM, DiagnosticSeverity.HIGH)
        self.register_check("disk_space", self._check_disk_space, 
                          DiagnosticCategory.FILE_SYSTEM, DiagnosticSeverity.CRITICAL)
        self.register_check("log_files", self._check_log_files,
                          DiagnosticCategory.FILE_SYSTEM, DiagnosticSeverity.LOW)
        self.register_check("temp_files", self._check_temp_files,
                          DiagnosticCategory.FILE_SYSTEM, DiagnosticSeverity.LOW)
        
        # ==================== ОСНОВНЫЕ СЕРВИСЫ ====================
        self.register_check("indexing_service", self._check_indexing_service, 
                          DiagnosticCategory.SERVICES, DiagnosticSeverity.HIGH)
        self.register_check("sessions_service", self._check_sessions_service, 
                          DiagnosticCategory.SERVICES, DiagnosticSeverity.HIGH)
        self.register_check("autopilot_service", self._check_autopilot_service,
                          DiagnosticCategory.SERVICES, DiagnosticSeverity.HIGH)
        self.register_check("position_tracker", self._check_position_tracker,
                          DiagnosticCategory.SERVICES, DiagnosticSeverity.MEDIUM)
        
        # ==================== AI СЕРВИСЫ ====================
        self.register_check("ai_providers", self._check_ai_providers,
                          DiagnosticCategory.AI, DiagnosticSeverity.HIGH)
        self.register_check("ai_agent_core", self._check_ai_agent_core,
                          DiagnosticCategory.AI, DiagnosticSeverity.HIGH)
        self.register_check("ai_learning", self._check_ai_learning,
                          DiagnosticCategory.AI, DiagnosticSeverity.MEDIUM)
        self.register_check("ai_seo_integration", self._check_ai_seo_integration,
                          DiagnosticCategory.AI, DiagnosticSeverity.MEDIUM)
        
        # ==================== EMAIL/SES СЕРВИСЫ ====================
        self.register_check("ses_service", self._check_ses_service,
                          DiagnosticCategory.EMAIL, DiagnosticSeverity.HIGH)
        self.register_check("ses_warmup", self._check_ses_warmup,
                          DiagnosticCategory.EMAIL, DiagnosticSeverity.MEDIUM)
        self.register_check("email_ab_testing", self._check_email_ab_testing,
                          DiagnosticCategory.EMAIL, DiagnosticSeverity.LOW)
        self.register_check("recipient_manager", self._check_recipient_manager,
                          DiagnosticCategory.EMAIL, DiagnosticSeverity.MEDIUM)
        
        # ==================== TDS СЕРВИСЫ ====================
        self.register_check("tds_core", self._check_tds_core,
                          DiagnosticCategory.TDS, DiagnosticSeverity.HIGH)
        self.register_check("tds_routing", self._check_tds_routing,
                          DiagnosticCategory.TDS, DiagnosticSeverity.HIGH)
        self.register_check("tds_antifraud", self._check_tds_antifraud,
                          DiagnosticCategory.TDS, DiagnosticSeverity.MEDIUM)
        self.register_check("tds_statistics", self._check_tds_statistics,
                          DiagnosticCategory.TDS, DiagnosticSeverity.LOW)
        self.register_check("cloaking_system", self._check_cloaking_system,
                          DiagnosticCategory.TDS, DiagnosticSeverity.MEDIUM)
        
        # ==================== ИНТЕГРАЦИИ ====================
        self.register_check("ads_integration", self._check_ads_integration,
                          DiagnosticCategory.INTEGRATIONS, DiagnosticSeverity.MEDIUM)
        self.register_check("ad_campaigns", self._check_ad_campaigns,
                          DiagnosticCategory.INTEGRATIONS, DiagnosticSeverity.MEDIUM)
        self.register_check("image_providers", self._check_image_providers,
                          DiagnosticCategory.INTEGRATIONS, DiagnosticSeverity.LOW)
        self.register_check("wordpress_manager", self._check_wordpress_manager,
                          DiagnosticCategory.INTEGRATIONS, DiagnosticSeverity.MEDIUM)
        self.register_check("cpanel_manager", self._check_cpanel_manager,
                          DiagnosticCategory.INTEGRATIONS, DiagnosticSeverity.MEDIUM)
        
        # ==================== КОНФИГУРАЦИЯ ====================
        self.register_check("config_files", self._check_config_files, 
                          DiagnosticCategory.CONFIGURATION, DiagnosticSeverity.HIGH)
        self.register_check("environment_vars", self._check_environment_vars, 
                          DiagnosticCategory.CONFIGURATION, DiagnosticSeverity.HIGH)
        self.register_check("api_keys", self._check_api_keys,
                          DiagnosticCategory.CONFIGURATION, DiagnosticSeverity.CRITICAL)
        
        # ==================== ЗАВИСИМОСТИ ====================
        self.register_check("python_packages", self._check_python_packages, 
                          DiagnosticCategory.DEPENDENCIES, DiagnosticSeverity.HIGH)
        self.register_check("frontend_build", self._check_frontend_build,
                          DiagnosticCategory.DEPENDENCIES, DiagnosticSeverity.MEDIUM)
        
        # ==================== ПРОИЗВОДИТЕЛЬНОСТЬ ====================
        self.register_check("memory_usage", self._check_memory_usage, 
                          DiagnosticCategory.PERFORMANCE, DiagnosticSeverity.HIGH)
        self.register_check("cpu_usage", self._check_cpu_usage,
                          DiagnosticCategory.PERFORMANCE, DiagnosticSeverity.MEDIUM)
        self.register_check("process_count", self._check_process_count,
                          DiagnosticCategory.PERFORMANCE, DiagnosticSeverity.LOW)
        
        # ==================== СЕТЬ ====================
        self.register_check("network_connectivity", self._check_network_connectivity,
                          DiagnosticCategory.NETWORK, DiagnosticSeverity.CRITICAL)
        self.register_check("port_availability", self._check_port_availability,
                          DiagnosticCategory.NETWORK, DiagnosticSeverity.HIGH)
        self.register_check("external_apis", self._check_external_apis,
                          DiagnosticCategory.NETWORK, DiagnosticSeverity.MEDIUM)
        
        # ==================== БЕЗОПАСНОСТЬ ====================
        self.register_check("file_permissions", self._check_file_permissions,
                          DiagnosticCategory.SECURITY, DiagnosticSeverity.MEDIUM)
        self.register_check("sensitive_data", self._check_sensitive_data,
                          DiagnosticCategory.SECURITY, DiagnosticSeverity.HIGH)
        
        # ==================== РЕГИСТРАЦИЯ ИСПРАВЛЕНИЙ ====================
        self.register_fix("data_directories", self._fix_data_directories)
        self.register_fix("json_files_integrity", self._fix_json_files)
        self.register_fix("config_files", self._fix_config_files)
        self.register_fix("temp_files", self._fix_temp_files)
        self.register_fix("log_files", self._fix_log_files)
        self.register_fix("file_permissions", self._fix_file_permissions)
        self.register_fix("frontend_build", self._fix_frontend_build)
    
    def register_check(self, check_id: str, check_func: Callable, 
                      category: DiagnosticCategory, severity: DiagnosticSeverity):
        """Регистрация проверки"""
        self.checks[check_id] = {
            "func": check_func,
            "category": category,
            "severity": severity
        }
    
    def register_fix(self, check_id: str, fix_func: Callable):
        """Регистрация исправления"""
        self.fixes[check_id] = fix_func
    
    # ==================== API ПРОВЕРКИ ====================
    
    async def _check_api_health(self) -> DiagnosticResult:
        """Проверка здоровья API"""
        start_time = time.time()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health", timeout=5) as resp:
                    duration = (time.time() - start_time) * 1000
                    if resp.status == 200:
                        data = await resp.json()
                        return DiagnosticResult(
                            check_id="api_health",
                            category=DiagnosticCategory.API,
                            name="API Health Check",
                            status=DiagnosticStatus.OK,
                            message="API is healthy and responding",
                            details={"response": data, "response_time_ms": duration},
                            severity=DiagnosticSeverity.CRITICAL,
                            duration_ms=duration
                        )
                    else:
                        return DiagnosticResult(
                            check_id="api_health",
                            category=DiagnosticCategory.API,
                            name="API Health Check",
                            status=DiagnosticStatus.ERROR,
                            message=f"API returned status {resp.status}",
                            severity=DiagnosticSeverity.CRITICAL,
                            recommendations=["Check backend logs", "Restart backend service"],
                            duration_ms=duration
                        )
        except Exception as e:
            return DiagnosticResult(
                check_id="api_health",
                category=DiagnosticCategory.API,
                name="API Health Check",
                status=DiagnosticStatus.CRITICAL,
                message=f"API is not responding: {str(e)}",
                severity=DiagnosticSeverity.CRITICAL,
                recommendations=[
                    "Check if backend is running: ps aux | grep uvicorn",
                    "Start backend: cd /home/ubuntu/seo_monster/backend && uvicorn main:app --host 0.0.0.0 --port 8000",
                    "Check port 8000 availability"
                ],
                duration_ms=(time.time() - start_time) * 1000
            )
    
    async def _check_api_endpoints(self) -> DiagnosticResult:
        """Проверка всех API endpoints"""
        # Критические endpoints - обязательные для работы системы
        critical_endpoints = [
            ("/api/sites/", "Sites API"),
            ("/api/platforms/", "Platforms API"),
            ("/api/content/", "Content API"),
            ("/api/tasks/", "Tasks API"),
            ("/api/indexing/stats", "Indexing Stats"),
            ("/api/sessions/stats", "Sessions Stats"),
            ("/api/agent/status", "Agent Status"),
            ("/api/diagnostics/status", "Diagnostics Status")
        ]
        
        # Опциональные endpoints - не влияют на Health Score
        optional_endpoints = [
            ("/api/ses/keys", "SES Keys"),
            ("/api/ses/warmup/stats", "Warmup Stats"),
            ("/api/tds/stats", "TDS Stats"),
            ("/api/ads/campaigns", "Ad Campaigns"),
            ("/api/tracker/stats", "Tracker Stats")
        ]
        
        endpoints = critical_endpoints + optional_endpoints
        
        start_time = time.time()
        errors = []
        warnings = []  # Критические warnings
        info_items = []  # Опциональные - только информация
        checked = 0
        
        critical_paths = [e[0] for e in critical_endpoints]
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                for endpoint, name in endpoints:
                    is_critical = endpoint in critical_paths
                    try:
                        async with session.get(f"http://localhost:8000{endpoint}", timeout=5) as resp:
                            checked += 1
                            if resp.status == 404:
                                if is_critical:
                                    warnings.append(f"{name} ({endpoint}): not found")
                                else:
                                    info_items.append(f"{name} ({endpoint}): not configured (optional)")
                            elif resp.status >= 500:
                                if is_critical:
                                    errors.append(f"{name} ({endpoint}): server error {resp.status}")
                                else:
                                    warnings.append(f"{name} ({endpoint}): server error {resp.status}")
                            elif resp.status >= 400:
                                if is_critical:
                                    warnings.append(f"{name} ({endpoint}): client error {resp.status}")
                                else:
                                    info_items.append(f"{name} ({endpoint}): {resp.status} (optional)")
                    except asyncio.TimeoutError:
                        if is_critical:
                            errors.append(f"{name} ({endpoint}): timeout")
                        else:
                            info_items.append(f"{name} ({endpoint}): timeout (optional)")
                    except Exception as e:
                        if is_critical:
                            errors.append(f"{name} ({endpoint}): {str(e)}")
                        else:
                            info_items.append(f"{name} ({endpoint}): {str(e)} (optional)")
            
            duration = (time.time() - start_time) * 1000
            
            if errors:
                return DiagnosticResult(
                    check_id="api_endpoints",
                    category=DiagnosticCategory.API,
                    name="API Endpoints Check",
                    status=DiagnosticStatus.ERROR,
                    message=f"{len(errors)} critical endpoints have errors",
                    details={"errors": errors, "warnings": warnings, "info": info_items, "checked": checked},
                    severity=DiagnosticSeverity.HIGH,
                    recommendations=["Check backend logs for errors", "Verify route registrations"],
                    duration_ms=duration
                )
            elif warnings:
                return DiagnosticResult(
                    check_id="api_endpoints",
                    category=DiagnosticCategory.API,
                    name="API Endpoints Check",
                    status=DiagnosticStatus.WARNING,
                    message=f"{len(warnings)} critical endpoints have warnings",
                    details={"warnings": warnings, "info": info_items, "checked": checked},
                    severity=DiagnosticSeverity.MEDIUM,
                    duration_ms=duration
                )
            else:
                # Все критические endpoints работают, опциональные - информация
                message = f"All {len(critical_endpoints)} critical endpoints working"
                if info_items:
                    message += f" ({len(info_items)} optional not configured)"
                return DiagnosticResult(
                    check_id="api_endpoints",
                    category=DiagnosticCategory.API,
                    name="API Endpoints Check",
                    status=DiagnosticStatus.OK,
                    message=message,
                    details={"checked": checked, "info": info_items} if info_items else {"checked": checked},
                    severity=DiagnosticSeverity.HIGH,
                    duration_ms=duration
                )
        except Exception as e:
            return DiagnosticResult(
                check_id="api_endpoints",
                category=DiagnosticCategory.API,
                name="API Endpoints Check",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to check endpoints: {str(e)}",
                severity=DiagnosticSeverity.HIGH,
                duration_ms=(time.time() - start_time) * 1000
            )
    
    async def _check_api_response_time(self) -> DiagnosticResult:
        """Проверка времени отклика API"""
        start_time = time.time()
        response_times = []
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                for _ in range(5):
                    req_start = time.time()
                    async with session.get("http://localhost:8000/health", timeout=10) as resp:
                        response_times.append((time.time() - req_start) * 1000)
            
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            if avg_time > 1000:
                status = DiagnosticStatus.ERROR
                message = f"API response time is too slow: {avg_time:.0f}ms avg"
            elif avg_time > 500:
                status = DiagnosticStatus.WARNING
                message = f"API response time is slow: {avg_time:.0f}ms avg"
            else:
                status = DiagnosticStatus.OK
                message = f"API response time is good: {avg_time:.0f}ms avg"
            
            return DiagnosticResult(
                check_id="api_response_time",
                category=DiagnosticCategory.API,
                name="API Response Time",
                status=status,
                message=message,
                details={
                    "avg_ms": avg_time,
                    "max_ms": max_time,
                    "samples": len(response_times)
                },
                severity=DiagnosticSeverity.MEDIUM,
                duration_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="api_response_time",
                category=DiagnosticCategory.API,
                name="API Response Time",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to measure response time: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM,
                duration_ms=(time.time() - start_time) * 1000
            )
    
    # ==================== ФАЙЛОВАЯ СИСТЕМА ====================
    
    async def _check_data_directories(self) -> DiagnosticResult:
        """Проверка директорий данных"""
        required_dirs = [
            "/home/ubuntu/seo_monster/backend/data",
            "/home/ubuntu/seo_monster/backend/data/indexing",
            "/home/ubuntu/seo_monster/backend/data/sessions",
            "/home/ubuntu/seo_monster/backend/data/autopilot",
            "/home/ubuntu/seo_monster/backend/data/knowledge",
            "/home/ubuntu/seo_monster/backend/data/positions",
            "/home/ubuntu/seo_monster/backend/data/diagnostics",
            "/home/ubuntu/seo_monster/backend/data/ses",
            "/home/ubuntu/seo_monster/backend/data/tds",
            "/home/ubuntu/seo_monster/backend/data/ads",
            "/home/ubuntu/seo_monster/backend/data/tracker"
        ]
        
        missing = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing.append(dir_path)
        
        if not missing:
            return DiagnosticResult(
                check_id="data_directories",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Data Directories Check",
                status=DiagnosticStatus.OK,
                message=f"All {len(required_dirs)} required directories exist",
                details={"checked_dirs": len(required_dirs)},
                severity=DiagnosticSeverity.HIGH
            )
        else:
            return DiagnosticResult(
                check_id="data_directories",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Data Directories Check",
                status=DiagnosticStatus.WARNING,
                message=f"{len(missing)} directories are missing",
                details={"missing": missing},
                fix_available=True,
                severity=DiagnosticSeverity.HIGH,
                recommendations=["Run auto-fix to create missing directories"]
            )
    
    async def _check_json_files(self) -> DiagnosticResult:
        """Проверка целостности JSON файлов"""
        data_dir = Path("/home/ubuntu/seo_monster/backend/data")
        corrupted = []
        checked = 0
        
        for json_file in data_dir.rglob("*.json"):
            checked += 1
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                corrupted.append({
                    "file": str(json_file),
                    "error": str(e)
                })
            except Exception as e:
                corrupted.append({
                    "file": str(json_file),
                    "error": str(e)
                })
        
        if not corrupted:
            return DiagnosticResult(
                check_id="json_files_integrity",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="JSON Files Integrity",
                status=DiagnosticStatus.OK,
                message=f"All {checked} JSON files are valid",
                details={"checked_files": checked},
                severity=DiagnosticSeverity.HIGH
            )
        else:
            return DiagnosticResult(
                check_id="json_files_integrity",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="JSON Files Integrity",
                status=DiagnosticStatus.ERROR,
                message=f"{len(corrupted)} JSON files are corrupted",
                details={"corrupted": corrupted, "checked": checked},
                fix_available=True,
                severity=DiagnosticSeverity.HIGH,
                recommendations=["Backup and reset corrupted files", "Check for disk errors"]
            )
    
    async def _check_disk_space(self) -> DiagnosticResult:
        """Проверка свободного места на диске"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/home/ubuntu")
            free_gb = free / (1024 ** 3)
            used_percent = (used / total) * 100
            
            if free_gb < 1:
                status = DiagnosticStatus.CRITICAL
                message = f"Critical: Only {free_gb:.2f} GB free"
                recommendations = ["Immediately free up disk space", "Delete old logs and temp files"]
            elif free_gb < 5:
                status = DiagnosticStatus.WARNING
                message = f"Warning: Only {free_gb:.2f} GB free"
                recommendations = ["Consider cleaning up disk space"]
            else:
                status = DiagnosticStatus.OK
                message = f"Disk space OK: {free_gb:.2f} GB free ({100-used_percent:.1f}%)"
                recommendations = []
            
            return DiagnosticResult(
                check_id="disk_space",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Disk Space Check",
                status=status,
                message=message,
                details={
                    "total_gb": round(total / (1024 ** 3), 2),
                    "used_gb": round(used / (1024 ** 3), 2),
                    "free_gb": round(free_gb, 2),
                    "used_percent": round(used_percent, 1)
                },
                severity=DiagnosticSeverity.CRITICAL,
                recommendations=recommendations
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="disk_space",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Disk Space Check",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to check disk space: {str(e)}",
                severity=DiagnosticSeverity.CRITICAL
            )
    
    async def _check_log_files(self) -> DiagnosticResult:
        """Проверка лог-файлов"""
        log_dirs = [
            "/home/ubuntu/seo_monster/backend/logs",
            "/tmp"
        ]
        
        total_size = 0
        large_files = []
        
        for log_dir in log_dirs:
            log_path = Path(log_dir)
            if log_path.exists():
                for log_file in log_path.glob("*.log"):
                    size = log_file.stat().st_size
                    total_size += size
                    if size > 100 * 1024 * 1024:  # > 100MB
                        large_files.append({
                            "file": str(log_file),
                            "size_mb": round(size / (1024 * 1024), 2)
                        })
        
        total_mb = total_size / (1024 * 1024)
        
        if large_files:
            return DiagnosticResult(
                check_id="log_files",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Log Files Check",
                status=DiagnosticStatus.WARNING,
                message=f"Found {len(large_files)} large log files ({total_mb:.1f} MB total)",
                details={"large_files": large_files, "total_mb": total_mb},
                fix_available=True,
                severity=DiagnosticSeverity.LOW,
                recommendations=["Rotate or truncate large log files"]
            )
        else:
            return DiagnosticResult(
                check_id="log_files",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Log Files Check",
                status=DiagnosticStatus.OK,
                message=f"Log files OK ({total_mb:.1f} MB total)",
                details={"total_mb": total_mb},
                severity=DiagnosticSeverity.LOW
            )
    
    async def _check_temp_files(self) -> DiagnosticResult:
        """Проверка временных файлов"""
        temp_dirs = ["/tmp", "/home/ubuntu/seo_monster/backend/temp"]
        total_size = 0
        old_files = []
        cutoff = datetime.now() - timedelta(days=7)
        
        for temp_dir in temp_dirs:
            temp_path = Path(temp_dir)
            if temp_path.exists():
                for temp_file in temp_path.glob("*"):
                    if temp_file.is_file():
                        stat = temp_file.stat()
                        total_size += stat.st_size
                        mtime = datetime.fromtimestamp(stat.st_mtime)
                        if mtime < cutoff:
                            old_files.append(str(temp_file))
        
        total_mb = total_size / (1024 * 1024)
        
        if old_files or total_mb > 500:
            return DiagnosticResult(
                check_id="temp_files",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Temp Files Check",
                status=DiagnosticStatus.WARNING,
                message=f"Found {len(old_files)} old temp files ({total_mb:.1f} MB total)",
                details={"old_files_count": len(old_files), "total_mb": total_mb},
                fix_available=True,
                severity=DiagnosticSeverity.LOW,
                recommendations=["Clean up old temporary files"]
            )
        else:
            return DiagnosticResult(
                check_id="temp_files",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Temp Files Check",
                status=DiagnosticStatus.OK,
                message=f"Temp files OK ({total_mb:.1f} MB)",
                severity=DiagnosticSeverity.LOW
            )
    
    # ==================== СЕРВИСЫ ====================
    
    async def _check_indexing_service(self) -> DiagnosticResult:
        """Проверка сервиса индексации"""
        try:
            from services.indexing_service import IndexingService
            service = IndexingService()
            stats = service.get_stats()
            
            return DiagnosticResult(
                check_id="indexing_service",
                category=DiagnosticCategory.SERVICES,
                name="Indexing Service Check",
                status=DiagnosticStatus.OK,
                message="Indexing service is working",
                details=stats,
                severity=DiagnosticSeverity.HIGH
            )
        except ImportError as e:
            return DiagnosticResult(
                check_id="indexing_service",
                category=DiagnosticCategory.SERVICES,
                name="Indexing Service Check",
                status=DiagnosticStatus.ERROR,
                message=f"Cannot import indexing service: {str(e)}",
                severity=DiagnosticSeverity.HIGH,
                recommendations=["Check if indexing_service.py exists", "Verify imports"]
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="indexing_service",
                category=DiagnosticCategory.SERVICES,
                name="Indexing Service Check",
                status=DiagnosticStatus.ERROR,
                message=f"Indexing service error: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_sessions_service(self) -> DiagnosticResult:
        """Проверка сервиса сессий"""
        try:
            from services.session_manager import SessionManager
            manager = SessionManager()
            stats = manager.get_stats()
            
            return DiagnosticResult(
                check_id="sessions_service",
                category=DiagnosticCategory.SERVICES,
                name="Sessions Service Check",
                status=DiagnosticStatus.OK,
                message="Sessions service is working",
                details=stats,
                severity=DiagnosticSeverity.HIGH
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="sessions_service",
                category=DiagnosticCategory.SERVICES,
                name="Sessions Service Check",
                status=DiagnosticStatus.ERROR,
                message=f"Sessions service error: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_autopilot_service(self) -> DiagnosticResult:
        """Проверка сервиса автопилота"""
        try:
            from services.autopilot_engine import AutopilotEngine
            engine = AutopilotEngine()
            stats = engine.get_stats()
            
            return DiagnosticResult(
                check_id="autopilot_service",
                category=DiagnosticCategory.SERVICES,
                name="Autopilot Service Check",
                status=DiagnosticStatus.OK,
                message="Autopilot service is working",
                details=stats,
                severity=DiagnosticSeverity.HIGH
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="autopilot_service",
                category=DiagnosticCategory.SERVICES,
                name="Autopilot Service Check",
                status=DiagnosticStatus.ERROR,
                message=f"Autopilot service error: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_position_tracker(self) -> DiagnosticResult:
        """Проверка трекера позиций"""
        try:
            from services.position_tracker import PositionTracker
            tracker = PositionTracker()
            
            return DiagnosticResult(
                check_id="position_tracker",
                category=DiagnosticCategory.SERVICES,
                name="Position Tracker Check",
                status=DiagnosticStatus.OK,
                message="Position tracker is working",
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="position_tracker",
                category=DiagnosticCategory.SERVICES,
                name="Position Tracker Check",
                status=DiagnosticStatus.ERROR,
                message=f"Position tracker error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    # ==================== AI СЕРВИСЫ ====================
    
    async def _check_ai_providers(self) -> DiagnosticResult:
        """Проверка AI провайдеров"""
        try:
            from services.ai_providers import AIProviderManager
            manager = AIProviderManager()
            providers = manager.get_available_providers()
            
            if providers:
                return DiagnosticResult(
                    check_id="ai_providers",
                    category=DiagnosticCategory.AI,
                    name="AI Providers Check",
                    status=DiagnosticStatus.OK,
                    message=f"{len(providers)} AI providers available",
                    details={"providers": providers},
                    severity=DiagnosticSeverity.HIGH
                )
            else:
                return DiagnosticResult(
                    check_id="ai_providers",
                    category=DiagnosticCategory.AI,
                    name="AI Providers Check",
                    status=DiagnosticStatus.WARNING,
                    message="No AI providers configured",
                    severity=DiagnosticSeverity.HIGH,
                    recommendations=["Configure OPENAI_API_KEY environment variable"]
                )
        except Exception as e:
            return DiagnosticResult(
                check_id="ai_providers",
                category=DiagnosticCategory.AI,
                name="AI Providers Check",
                status=DiagnosticStatus.ERROR,
                message=f"AI providers error: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_ai_agent_core(self) -> DiagnosticResult:
        """Проверка ядра AI агента"""
        try:
            from services.ai_agent_core import AIAgentCore
            agent = AIAgentCore()
            status = agent.get_status()
            
            return DiagnosticResult(
                check_id="ai_agent_core",
                category=DiagnosticCategory.AI,
                name="AI Agent Core Check",
                status=DiagnosticStatus.OK,
                message="AI Agent Core is working",
                details=status,
                severity=DiagnosticSeverity.HIGH
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="ai_agent_core",
                category=DiagnosticCategory.AI,
                name="AI Agent Core Check",
                status=DiagnosticStatus.ERROR,
                message=f"AI Agent Core error: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_ai_learning(self) -> DiagnosticResult:
        """Проверка системы обучения AI"""
        try:
            from services.agent_self_learning import AgentSelfLearning
            learning = AgentSelfLearning()
            stats = learning.get_stats()
            
            return DiagnosticResult(
                check_id="ai_learning",
                category=DiagnosticCategory.AI,
                name="AI Learning System Check",
                status=DiagnosticStatus.OK,
                message="AI Learning system is working",
                details=stats,
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="ai_learning",
                category=DiagnosticCategory.AI,
                name="AI Learning System Check",
                status=DiagnosticStatus.ERROR,
                message=f"AI Learning error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    async def _check_ai_seo_integration(self) -> DiagnosticResult:
        """Проверка интеграции AI с SEO"""
        try:
            from services.ai_seo_integration import AISEOIntegration
            integration = AISEOIntegration()
            
            return DiagnosticResult(
                check_id="ai_seo_integration",
                category=DiagnosticCategory.AI,
                name="AI SEO Integration Check",
                status=DiagnosticStatus.OK,
                message="AI SEO Integration is working",
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="ai_seo_integration",
                category=DiagnosticCategory.AI,
                name="AI SEO Integration Check",
                status=DiagnosticStatus.ERROR,
                message=f"AI SEO Integration error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    # ==================== EMAIL/SES СЕРВИСЫ ====================
    
    async def _check_ses_service(self) -> DiagnosticResult:
        """Проверка AWS SES сервиса"""
        try:
            from services.aws_ses_service import AWSSESService
            service = AWSSESService()
            keys = service.get_all_keys()
            
            active_keys = [k for k in keys if k.get("status") == "active"]
            
            if not keys:
                # Отсутствие SES ключей - это опциональная функция, не ошибка
                return DiagnosticResult(
                    check_id="ses_service",
                    category=DiagnosticCategory.EMAIL,
                    name="AWS SES Service Check",
                    status=DiagnosticStatus.OK,
                    message="AWS SES not configured (optional feature)",
                    severity=DiagnosticSeverity.LOW,
                    details={"configured": False, "note": "Add AWS SES keys to enable email functionality"},
                    recommendations=["Add AWS SES credentials in Email SES module to enable email sending"]
                )
            elif not active_keys:
                return DiagnosticResult(
                    check_id="ses_service",
                    category=DiagnosticCategory.EMAIL,
                    name="AWS SES Service Check",
                    status=DiagnosticStatus.WARNING,
                    message=f"{len(keys)} keys configured but none active",
                    details={"total_keys": len(keys)},
                    severity=DiagnosticSeverity.HIGH
                )
            else:
                return DiagnosticResult(
                    check_id="ses_service",
                    category=DiagnosticCategory.EMAIL,
                    name="AWS SES Service Check",
                    status=DiagnosticStatus.OK,
                    message=f"{len(active_keys)} active SES keys",
                    details={"total_keys": len(keys), "active_keys": len(active_keys)},
                    severity=DiagnosticSeverity.HIGH
                )
        except Exception as e:
            return DiagnosticResult(
                check_id="ses_service",
                category=DiagnosticCategory.EMAIL,
                name="AWS SES Service Check",
                status=DiagnosticStatus.ERROR,
                message=f"SES service error: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_ses_warmup(self) -> DiagnosticResult:
        """Проверка системы прогрева SES"""
        try:
            from services.ses_warmup import SESWarmupService
            service = SESWarmupService()
            stats = service.get_stats()
            
            in_progress = stats.get("in_progress", 0)
            paused = stats.get("paused", 0)
            
            if paused > 0:
                return DiagnosticResult(
                    check_id="ses_warmup",
                    category=DiagnosticCategory.EMAIL,
                    name="SES Warmup Check",
                    status=DiagnosticStatus.WARNING,
                    message=f"{paused} warmup plans are paused",
                    details=stats,
                    severity=DiagnosticSeverity.MEDIUM,
                    recommendations=["Check paused warmup plans for issues"]
                )
            else:
                return DiagnosticResult(
                    check_id="ses_warmup",
                    category=DiagnosticCategory.EMAIL,
                    name="SES Warmup Check",
                    status=DiagnosticStatus.OK,
                    message=f"Warmup system OK ({in_progress} in progress)",
                    details=stats,
                    severity=DiagnosticSeverity.MEDIUM
                )
        except Exception as e:
            return DiagnosticResult(
                check_id="ses_warmup",
                category=DiagnosticCategory.EMAIL,
                name="SES Warmup Check",
                status=DiagnosticStatus.ERROR,
                message=f"SES Warmup error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    async def _check_email_ab_testing(self) -> DiagnosticResult:
        """Проверка A/B тестирования email"""
        try:
            from services.email_ab_testing import EmailABTestingService
            service = EmailABTestingService()
            # Проверяем, является ли метод async
            import inspect
            if inspect.iscoroutinefunction(service.get_stats):
                stats = await service.get_stats()
            else:
                stats = service.get_stats()
            
            return DiagnosticResult(
                check_id="email_ab_testing",
                category=DiagnosticCategory.EMAIL,
                name="Email A/B Testing Check",
                status=DiagnosticStatus.OK,
                message="A/B Testing service is working",
                details=stats,
                severity=DiagnosticSeverity.LOW
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="email_ab_testing",
                category=DiagnosticCategory.EMAIL,
                name="Email A/B Testing Check",
                status=DiagnosticStatus.ERROR,
                message=f"A/B Testing error: {str(e)}",
                severity=DiagnosticSeverity.LOW
            )
    
    async def _check_recipient_manager(self) -> DiagnosticResult:
        """Проверка менеджера получателей"""
        try:
            from services.recipient_manager import RecipientManager
            manager = RecipientManager()
            lists = manager.get_all_lists()
            
            total_recipients = sum(l.get("count", 0) for l in lists)
            
            return DiagnosticResult(
                check_id="recipient_manager",
                category=DiagnosticCategory.EMAIL,
                name="Recipient Manager Check",
                status=DiagnosticStatus.OK,
                message=f"{len(lists)} lists with {total_recipients} recipients",
                details={"lists_count": len(lists), "total_recipients": total_recipients},
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="recipient_manager",
                category=DiagnosticCategory.EMAIL,
                name="Recipient Manager Check",
                status=DiagnosticStatus.ERROR,
                message=f"Recipient manager error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    # ==================== TDS СЕРВИСЫ ====================
    
    async def _check_tds_core(self) -> DiagnosticResult:
        """Проверка ядра TDS"""
        try:
            from services.tds_core import TDSCore
            tds = TDSCore()
            stats = tds.get_stats()
            
            return DiagnosticResult(
                check_id="tds_core",
                category=DiagnosticCategory.TDS,
                name="TDS Core Check",
                status=DiagnosticStatus.OK,
                message="TDS Core is working",
                details=stats,
                severity=DiagnosticSeverity.HIGH
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="tds_core",
                category=DiagnosticCategory.TDS,
                name="TDS Core Check",
                status=DiagnosticStatus.ERROR,
                message=f"TDS Core error: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_tds_routing(self) -> DiagnosticResult:
        """Проверка маршрутизации TDS"""
        try:
            from services.tds_routing import TDSRouting
            routing = TDSRouting()
            
            return DiagnosticResult(
                check_id="tds_routing",
                category=DiagnosticCategory.TDS,
                name="TDS Routing Check",
                status=DiagnosticStatus.OK,
                message="TDS Routing is working",
                severity=DiagnosticSeverity.HIGH
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="tds_routing",
                category=DiagnosticCategory.TDS,
                name="TDS Routing Check",
                status=DiagnosticStatus.ERROR,
                message=f"TDS Routing error: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_tds_antifraud(self) -> DiagnosticResult:
        """Проверка антифрода TDS"""
        try:
            from services.tds_antifraud import TDSAntifraud
            antifraud = TDSAntifraud()
            
            return DiagnosticResult(
                check_id="tds_antifraud",
                category=DiagnosticCategory.TDS,
                name="TDS Antifraud Check",
                status=DiagnosticStatus.OK,
                message="TDS Antifraud is working",
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="tds_antifraud",
                category=DiagnosticCategory.TDS,
                name="TDS Antifraud Check",
                status=DiagnosticStatus.ERROR,
                message=f"TDS Antifraud error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    async def _check_tds_statistics(self) -> DiagnosticResult:
        """Проверка статистики TDS"""
        try:
            from services.tds_statistics import TDSStatistics
            stats_service = TDSStatistics()
            
            return DiagnosticResult(
                check_id="tds_statistics",
                category=DiagnosticCategory.TDS,
                name="TDS Statistics Check",
                status=DiagnosticStatus.OK,
                message="TDS Statistics is working",
                severity=DiagnosticSeverity.LOW
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="tds_statistics",
                category=DiagnosticCategory.TDS,
                name="TDS Statistics Check",
                status=DiagnosticStatus.ERROR,
                message=f"TDS Statistics error: {str(e)}",
                severity=DiagnosticSeverity.LOW
            )
    
    async def _check_cloaking_system(self) -> DiagnosticResult:
        """Проверка системы клоакинга"""
        try:
            from services.cloaking_system import CloakingSystem
            cloaking = CloakingSystem()
            
            return DiagnosticResult(
                check_id="cloaking_system",
                category=DiagnosticCategory.TDS,
                name="Cloaking System Check",
                status=DiagnosticStatus.OK,
                message="Cloaking system is working",
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="cloaking_system",
                category=DiagnosticCategory.TDS,
                name="Cloaking System Check",
                status=DiagnosticStatus.ERROR,
                message=f"Cloaking system error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    # ==================== ИНТЕГРАЦИИ ====================
    
    async def _check_ads_integration(self) -> DiagnosticResult:
        """Проверка интеграции с рекламными системами"""
        try:
            from services.ads_tracker_integration import AdsTrackerIntegration
            integration = AdsTrackerIntegration()
            stats = integration.get_stats()
            
            return DiagnosticResult(
                check_id="ads_integration",
                category=DiagnosticCategory.INTEGRATIONS,
                name="Ads Integration Check",
                status=DiagnosticStatus.OK,
                message="Ads integration is working",
                details=stats,
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="ads_integration",
                category=DiagnosticCategory.INTEGRATIONS,
                name="Ads Integration Check",
                status=DiagnosticStatus.ERROR,
                message=f"Ads integration error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    async def _check_ad_campaigns(self) -> DiagnosticResult:
        """Проверка рекламных кампаний"""
        try:
            from services.ad_campaigns_service import AdCampaignsService
            service = AdCampaignsService()
            # Проверяем, является ли метод async
            import inspect
            if inspect.iscoroutinefunction(service.get_stats):
                stats = await service.get_stats()
            else:
                stats = service.get_stats()
            
            return DiagnosticResult(
                check_id="ad_campaigns",
                category=DiagnosticCategory.INTEGRATIONS,
                name="Ad Campaigns Check",
                status=DiagnosticStatus.OK,
                message="Ad campaigns service is working",
                details=stats,
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="ad_campaigns",
                category=DiagnosticCategory.INTEGRATIONS,
                name="Ad Campaigns Check",
                status=DiagnosticStatus.ERROR,
                message=f"Ad campaigns error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    async def _check_image_providers(self) -> DiagnosticResult:
        """Проверка провайдеров изображений"""
        try:
            from services.image_providers import ImageProviderManager
            manager = ImageProviderManager()
            providers = manager.get_available_providers()
            
            return DiagnosticResult(
                check_id="image_providers",
                category=DiagnosticCategory.INTEGRATIONS,
                name="Image Providers Check",
                status=DiagnosticStatus.OK,
                message=f"{len(providers)} image providers available",
                details={"providers": providers},
                severity=DiagnosticSeverity.LOW
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="image_providers",
                category=DiagnosticCategory.INTEGRATIONS,
                name="Image Providers Check",
                status=DiagnosticStatus.WARNING,
                message=f"Image providers error: {str(e)}",
                severity=DiagnosticSeverity.LOW
            )
    
    async def _check_wordpress_manager(self) -> DiagnosticResult:
        """Проверка менеджера WordPress"""
        try:
            from services.wordpress_manager import WordPressManager
            manager = WordPressManager()
            
            return DiagnosticResult(
                check_id="wordpress_manager",
                category=DiagnosticCategory.INTEGRATIONS,
                name="WordPress Manager Check",
                status=DiagnosticStatus.OK,
                message="WordPress manager is working",
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="wordpress_manager",
                category=DiagnosticCategory.INTEGRATIONS,
                name="WordPress Manager Check",
                status=DiagnosticStatus.ERROR,
                message=f"WordPress manager error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    async def _check_cpanel_manager(self) -> DiagnosticResult:
        """Проверка менеджера cPanel"""
        try:
            from services.cpanel_manager import CpanelManager
            manager = CpanelManager()
            
            return DiagnosticResult(
                check_id="cpanel_manager",
                category=DiagnosticCategory.INTEGRATIONS,
                name="cPanel Manager Check",
                status=DiagnosticStatus.OK,
                message="cPanel manager is working",
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="cpanel_manager",
                category=DiagnosticCategory.INTEGRATIONS,
                name="cPanel Manager Check",
                status=DiagnosticStatus.ERROR,
                message=f"cPanel manager error: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    # ==================== КОНФИГУРАЦИЯ ====================
    
    async def _check_config_files(self) -> DiagnosticResult:
        """Проверка конфигурационных файлов"""
        config_files = {
            "/home/ubuntu/seo_monster/backend/data/diagnostics/diagnostics_config.json": {},
            "/home/ubuntu/seo_monster/backend/data/autopilot/campaigns.json": [],
            "/home/ubuntu/seo_monster/backend/data/ses/keys.json": [],
            "/home/ubuntu/seo_monster/backend/data/tds/config.json": {}
        }
        
        missing = []
        for config_path in config_files.keys():
            if not Path(config_path).exists():
                missing.append(config_path)
        
        if not missing:
            return DiagnosticResult(
                check_id="config_files",
                category=DiagnosticCategory.CONFIGURATION,
                name="Config Files Check",
                status=DiagnosticStatus.OK,
                message=f"All {len(config_files)} config files exist",
                severity=DiagnosticSeverity.HIGH
            )
        else:
            return DiagnosticResult(
                check_id="config_files",
                category=DiagnosticCategory.CONFIGURATION,
                name="Config Files Check",
                status=DiagnosticStatus.WARNING,
                message=f"{len(missing)} config files missing",
                details={"missing": missing},
                fix_available=True,
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_environment_vars(self) -> DiagnosticResult:
        """Проверка переменных окружения"""
        required_vars = {
            "OPENAI_API_KEY": "Required for AI functionality"
        }
        optional_vars = {
            "AWS_ACCESS_KEY_ID": "For AWS SES",
            "AWS_SECRET_ACCESS_KEY": "For AWS SES",
            "TELEGRAM_BOT_TOKEN": "For Telegram notifications"
        }
        
        missing_required = []
        missing_optional = []
        
        for var, desc in required_vars.items():
            if not os.environ.get(var):
                missing_required.append({"var": var, "description": desc})
        
        for var, desc in optional_vars.items():
            if not os.environ.get(var):
                missing_optional.append({"var": var, "description": desc})
        
        if missing_required:
            return DiagnosticResult(
                check_id="environment_vars",
                category=DiagnosticCategory.CONFIGURATION,
                name="Environment Variables Check",
                status=DiagnosticStatus.ERROR,
                message=f"{len(missing_required)} required variables missing",
                details={"missing_required": missing_required, "missing_optional": missing_optional},
                severity=DiagnosticSeverity.HIGH,
                recommendations=[f"Set {v['var']}: {v['description']}" for v in missing_required]
            )
        elif missing_optional:
            # Опциональные переменные не влияют на Health Score
            return DiagnosticResult(
                check_id="environment_vars",
                category=DiagnosticCategory.CONFIGURATION,
                name="Environment Variables Check",
                status=DiagnosticStatus.OK,
                message=f"All required vars set ({len(missing_optional)} optional available)",
                details={"optional_features": missing_optional, "note": "Optional variables enable additional features"},
                severity=DiagnosticSeverity.LOW
            )
        else:
            return DiagnosticResult(
                check_id="environment_vars",
                category=DiagnosticCategory.CONFIGURATION,
                name="Environment Variables Check",
                status=DiagnosticStatus.OK,
                message="All environment variables are set",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_api_keys(self) -> DiagnosticResult:
        """Проверка API ключей"""
        api_key = os.environ.get("OPENAI_API_KEY", "")
        
        if not api_key:
            return DiagnosticResult(
                check_id="api_keys",
                category=DiagnosticCategory.CONFIGURATION,
                name="API Keys Check",
                status=DiagnosticStatus.CRITICAL,
                message="OPENAI_API_KEY is not set",
                severity=DiagnosticSeverity.CRITICAL,
                recommendations=["Set OPENAI_API_KEY environment variable"]
            )
        
        # Проверяем формат ключа
        if api_key.startswith("sk-") and len(api_key) > 20:
            return DiagnosticResult(
                check_id="api_keys",
                category=DiagnosticCategory.CONFIGURATION,
                name="API Keys Check",
                status=DiagnosticStatus.OK,
                message="API keys are configured",
                severity=DiagnosticSeverity.CRITICAL
            )
        else:
            return DiagnosticResult(
                check_id="api_keys",
                category=DiagnosticCategory.CONFIGURATION,
                name="API Keys Check",
                status=DiagnosticStatus.WARNING,
                message="API key format may be invalid",
                severity=DiagnosticSeverity.CRITICAL
            )
    
    # ==================== ЗАВИСИМОСТИ ====================
    
    async def _check_python_packages(self) -> DiagnosticResult:
        """Проверка Python пакетов"""
        required_packages = [
            "fastapi", "uvicorn", "aiohttp", "openai", "pydantic",
            "requests", "boto3", "pillow", "beautifulsoup4"
        ]
        
        missing = []
        installed = []
        
        # Маппинг пакетов к именам модулей
        package_modules = {
            "fastapi": "fastapi",
            "uvicorn": "uvicorn",
            "aiohttp": "aiohttp",
            "openai": "openai",
            "pydantic": "pydantic",
            "requests": "requests",
            "boto3": "boto3",
            "pillow": "PIL",
            "beautifulsoup4": "bs4"
        }
        
        for package in required_packages:
            try:
                module_name = package_modules.get(package, package.replace("-", "_"))
                importlib.import_module(module_name)
                installed.append(package)
            except ImportError:
                missing.append(package)
        
        if not missing:
            return DiagnosticResult(
                check_id="python_packages",
                category=DiagnosticCategory.DEPENDENCIES,
                name="Python Packages Check",
                status=DiagnosticStatus.OK,
                message=f"All {len(required_packages)} required packages installed",
                details={"installed": installed},
                severity=DiagnosticSeverity.HIGH
            )
        else:
            return DiagnosticResult(
                check_id="python_packages",
                category=DiagnosticCategory.DEPENDENCIES,
                name="Python Packages Check",
                status=DiagnosticStatus.ERROR,
                message=f"{len(missing)} packages are missing",
                details={"missing": missing, "installed": installed},
                severity=DiagnosticSeverity.HIGH,
                recommendations=[f"Install missing packages: pip install {' '.join(missing)}"]
            )
    
    async def _check_frontend_build(self) -> DiagnosticResult:
        """Проверка сборки frontend"""
        dist_dir = Path("/home/ubuntu/seo_monster/frontend/dist")
        
        if not dist_dir.exists():
            return DiagnosticResult(
                check_id="frontend_build",
                category=DiagnosticCategory.DEPENDENCIES,
                name="Frontend Build Check",
                status=DiagnosticStatus.ERROR,
                message="Frontend dist directory not found",
                fix_available=True,
                severity=DiagnosticSeverity.MEDIUM,
                recommendations=["Run: cd frontend && pnpm run build"]
            )
        
        index_html = dist_dir / "index.html"
        assets_dir = dist_dir / "assets"
        
        if not index_html.exists():
            return DiagnosticResult(
                check_id="frontend_build",
                category=DiagnosticCategory.DEPENDENCIES,
                name="Frontend Build Check",
                status=DiagnosticStatus.ERROR,
                message="Frontend index.html not found",
                fix_available=True,
                severity=DiagnosticSeverity.MEDIUM
            )
        
        if not assets_dir.exists() or not list(assets_dir.glob("*.js")):
            return DiagnosticResult(
                check_id="frontend_build",
                category=DiagnosticCategory.DEPENDENCIES,
                name="Frontend Build Check",
                status=DiagnosticStatus.ERROR,
                message="Frontend assets not found",
                fix_available=True,
                severity=DiagnosticSeverity.MEDIUM
            )
        
        return DiagnosticResult(
            check_id="frontend_build",
            category=DiagnosticCategory.DEPENDENCIES,
            name="Frontend Build Check",
            status=DiagnosticStatus.OK,
            message="Frontend build is valid",
            severity=DiagnosticSeverity.MEDIUM
        )
    
    # ==================== ПРОИЗВОДИТЕЛЬНОСТЬ ====================
    
    async def _check_memory_usage(self) -> DiagnosticResult:
        """Проверка использования памяти"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = DiagnosticStatus.CRITICAL
                message = f"Critical: Memory usage at {memory.percent}%"
                recommendations = ["Restart services to free memory", "Check for memory leaks"]
            elif memory.percent > 75:
                status = DiagnosticStatus.WARNING
                message = f"Warning: Memory usage at {memory.percent}%"
                recommendations = ["Monitor memory usage"]
            else:
                status = DiagnosticStatus.OK
                message = f"Memory usage OK: {memory.percent}%"
                recommendations = []
            
            return DiagnosticResult(
                check_id="memory_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="Memory Usage Check",
                status=status,
                message=message,
                details={
                    "total_gb": round(memory.total / (1024 ** 3), 2),
                    "available_gb": round(memory.available / (1024 ** 3), 2),
                    "percent_used": memory.percent
                },
                severity=DiagnosticSeverity.HIGH,
                recommendations=recommendations
            )
        except ImportError:
            return DiagnosticResult(
                check_id="memory_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="Memory Usage Check",
                status=DiagnosticStatus.WARNING,
                message="psutil not installed, cannot check memory",
                severity=DiagnosticSeverity.HIGH
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="memory_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="Memory Usage Check",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to check memory: {str(e)}",
                severity=DiagnosticSeverity.HIGH
            )
    
    async def _check_cpu_usage(self) -> DiagnosticResult:
        """Проверка использования CPU"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 90:
                status = DiagnosticStatus.WARNING
                message = f"High CPU usage: {cpu_percent}%"
            else:
                status = DiagnosticStatus.OK
                message = f"CPU usage OK: {cpu_percent}%"
            
            return DiagnosticResult(
                check_id="cpu_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="CPU Usage Check",
                status=status,
                message=message,
                details={"cpu_percent": cpu_percent, "cpu_count": psutil.cpu_count()},
                severity=DiagnosticSeverity.MEDIUM
            )
        except ImportError:
            return DiagnosticResult(
                check_id="cpu_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="CPU Usage Check",
                status=DiagnosticStatus.SKIPPED,
                message="psutil not installed",
                severity=DiagnosticSeverity.MEDIUM
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="cpu_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="CPU Usage Check",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to check CPU: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    async def _check_process_count(self) -> DiagnosticResult:
        """Проверка количества процессов"""
        try:
            import psutil
            processes = len(psutil.pids())
            
            python_procs = len([p for p in psutil.process_iter(['name']) 
                              if 'python' in p.info['name'].lower()])
            
            return DiagnosticResult(
                check_id="process_count",
                category=DiagnosticCategory.PERFORMANCE,
                name="Process Count Check",
                status=DiagnosticStatus.OK,
                message=f"{processes} total processes, {python_procs} Python",
                details={"total": processes, "python": python_procs},
                severity=DiagnosticSeverity.LOW
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="process_count",
                category=DiagnosticCategory.PERFORMANCE,
                name="Process Count Check",
                status=DiagnosticStatus.SKIPPED,
                message=f"Cannot check processes: {str(e)}",
                severity=DiagnosticSeverity.LOW
            )
    
    # ==================== СЕТЬ ====================
    
    async def _check_network_connectivity(self) -> DiagnosticResult:
        """Проверка сетевого подключения"""
        hosts = [
            ("8.8.8.8", 53, "Google DNS"),
            ("1.1.1.1", 53, "Cloudflare DNS")
        ]
        
        connected = []
        failed = []
        
        for host, port, name in hosts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    connected.append(name)
                else:
                    failed.append(name)
            except:
                failed.append(name)
        
        if connected:
            return DiagnosticResult(
                check_id="network_connectivity",
                category=DiagnosticCategory.NETWORK,
                name="Network Connectivity Check",
                status=DiagnosticStatus.OK,
                message="Internet connection is working",
                details={"connected_to": connected},
                severity=DiagnosticSeverity.CRITICAL
            )
        else:
            return DiagnosticResult(
                check_id="network_connectivity",
                category=DiagnosticCategory.NETWORK,
                name="Network Connectivity Check",
                status=DiagnosticStatus.CRITICAL,
                message="No internet connection",
                details={"failed": failed},
                severity=DiagnosticSeverity.CRITICAL,
                recommendations=["Check network configuration", "Verify DNS settings"]
            )
    
    async def _check_port_availability(self) -> DiagnosticResult:
        """Проверка доступности портов"""
        ports = [
            (8000, "Backend API"),
            (5173, "Frontend Dev"),
            (5200, "Frontend Alt")
        ]
        
        in_use = []
        available = []
        
        for port, name in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                in_use.append({"port": port, "name": name})
            else:
                available.append({"port": port, "name": name})
        
        # Backend должен быть запущен
        backend_running = any(p["port"] == 8000 for p in in_use)
        
        if backend_running:
            return DiagnosticResult(
                check_id="port_availability",
                category=DiagnosticCategory.NETWORK,
                name="Port Availability Check",
                status=DiagnosticStatus.OK,
                message=f"Backend running, {len(in_use)} services active",
                details={"in_use": in_use, "available": available},
                severity=DiagnosticSeverity.HIGH
            )
        else:
            return DiagnosticResult(
                check_id="port_availability",
                category=DiagnosticCategory.NETWORK,
                name="Port Availability Check",
                status=DiagnosticStatus.WARNING,
                message="Backend API not detected on port 8000",
                details={"in_use": in_use, "available": available},
                severity=DiagnosticSeverity.HIGH,
                recommendations=["Start backend: uvicorn main:app --port 8000"]
            )
    
    async def _check_external_apis(self) -> DiagnosticResult:
        """Проверка внешних API"""
        apis = [
            ("https://api.openai.com", "OpenAI API"),
            ("https://www.google.com", "Google"),
            ("https://api.github.com", "GitHub API")
        ]
        
        reachable = []
        unreachable = []
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                for url, name in apis:
                    try:
                        async with session.head(url, timeout=5) as resp:
                            if resp.status < 500:
                                reachable.append(name)
                            else:
                                unreachable.append(name)
                    except:
                        unreachable.append(name)
            
            if unreachable:
                return DiagnosticResult(
                    check_id="external_apis",
                    category=DiagnosticCategory.NETWORK,
                    name="External APIs Check",
                    status=DiagnosticStatus.WARNING,
                    message=f"{len(unreachable)} external APIs unreachable",
                    details={"reachable": reachable, "unreachable": unreachable},
                    severity=DiagnosticSeverity.MEDIUM
                )
            else:
                return DiagnosticResult(
                    check_id="external_apis",
                    category=DiagnosticCategory.NETWORK,
                    name="External APIs Check",
                    status=DiagnosticStatus.OK,
                    message=f"All {len(reachable)} external APIs reachable",
                    details={"reachable": reachable},
                    severity=DiagnosticSeverity.MEDIUM
                )
        except Exception as e:
            return DiagnosticResult(
                check_id="external_apis",
                category=DiagnosticCategory.NETWORK,
                name="External APIs Check",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to check external APIs: {str(e)}",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    # ==================== БЕЗОПАСНОСТЬ ====================
    
    async def _check_file_permissions(self) -> DiagnosticResult:
        """Проверка прав доступа к файлам"""
        sensitive_paths = [
            "/home/ubuntu/seo_monster/backend/data",
            "/home/ubuntu/seo_monster/backend/services"
        ]
        
        issues = []
        for path_str in sensitive_paths:
            path = Path(path_str)
            if path.exists():
                mode = path.stat().st_mode
                # Проверяем, что нет world-writable
                if mode & 0o002:
                    issues.append(f"{path_str} is world-writable")
        
        if issues:
            return DiagnosticResult(
                check_id="file_permissions",
                category=DiagnosticCategory.SECURITY,
                name="File Permissions Check",
                status=DiagnosticStatus.WARNING,
                message=f"{len(issues)} permission issues found",
                details={"issues": issues},
                fix_available=True,
                severity=DiagnosticSeverity.MEDIUM,
                recommendations=["Fix file permissions"]
            )
        else:
            return DiagnosticResult(
                check_id="file_permissions",
                category=DiagnosticCategory.SECURITY,
                name="File Permissions Check",
                status=DiagnosticStatus.OK,
                message="File permissions are secure",
                severity=DiagnosticSeverity.MEDIUM
            )
    
    async def _check_sensitive_data(self) -> DiagnosticResult:
        """Проверка на утечку чувствительных данных"""
        sensitive_patterns = [
            r'sk-[a-zA-Z0-9]{20,}',  # OpenAI API key
            r'AKIA[A-Z0-9]{16}',  # AWS Access Key
        ]
        
        data_dir = Path("/home/ubuntu/seo_monster/backend/data")
        found_in_files = []
        
        for json_file in data_dir.rglob("*.json"):
            try:
                content = json_file.read_text()
                for pattern in sensitive_patterns:
                    if re.search(pattern, content):
                        found_in_files.append(str(json_file))
                        break
            except:
                pass
        
        if found_in_files:
            return DiagnosticResult(
                check_id="sensitive_data",
                category=DiagnosticCategory.SECURITY,
                name="Sensitive Data Check",
                status=DiagnosticStatus.WARNING,
                message=f"Potential sensitive data in {len(found_in_files)} files",
                details={"files": found_in_files[:5]},  # Показываем только первые 5
                severity=DiagnosticSeverity.HIGH,
                recommendations=["Review files for sensitive data exposure"]
            )
        else:
            return DiagnosticResult(
                check_id="sensitive_data",
                category=DiagnosticCategory.SECURITY,
                name="Sensitive Data Check",
                status=DiagnosticStatus.OK,
                message="No sensitive data patterns found in data files",
                severity=DiagnosticSeverity.HIGH
            )
    
    # ==================== ИСПРАВЛЕНИЯ ====================
    
    async def _fix_data_directories(self) -> FixResult:
        """Создание отсутствующих директорий"""
        required_dirs = [
            "/home/ubuntu/seo_monster/backend/data",
            "/home/ubuntu/seo_monster/backend/data/indexing",
            "/home/ubuntu/seo_monster/backend/data/sessions",
            "/home/ubuntu/seo_monster/backend/data/autopilot",
            "/home/ubuntu/seo_monster/backend/data/knowledge",
            "/home/ubuntu/seo_monster/backend/data/positions",
            "/home/ubuntu/seo_monster/backend/data/diagnostics",
            "/home/ubuntu/seo_monster/backend/data/ses",
            "/home/ubuntu/seo_monster/backend/data/tds",
            "/home/ubuntu/seo_monster/backend/data/ads",
            "/home/ubuntu/seo_monster/backend/data/tracker"
        ]
        
        created = []
        try:
            for dir_path in required_dirs:
                path = Path(dir_path)
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                    created.append(dir_path)
            
            return FixResult(
                check_id="data_directories",
                success=True,
                message=f"Created {len(created)} directories",
                before_status=DiagnosticStatus.WARNING,
                after_status=DiagnosticStatus.OK,
                actions_taken=[f"Created: {d}" for d in created]
            )
        except Exception as e:
            return FixResult(
                check_id="data_directories",
                success=False,
                message=f"Failed: {str(e)}",
                before_status=DiagnosticStatus.WARNING,
                after_status=DiagnosticStatus.ERROR
            )
    
    async def _fix_json_files(self) -> FixResult:
        """Восстановление поврежденных JSON файлов"""
        data_dir = Path("/home/ubuntu/seo_monster/backend/data")
        fixed = []
        failed = []
        
        for json_file in data_dir.rglob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                try:
                    # Создаем резервную копию
                    backup_path = json_file.with_suffix('.json.bak')
                    if json_file.exists():
                        import shutil
                        shutil.copy(json_file, backup_path)
                    
                    # Определяем тип файла по имени
                    if "config" in json_file.name:
                        default_content = {}
                    else:
                        default_content = []
                    
                    with open(json_file, 'w') as f:
                        json.dump(default_content, f, indent=2)
                    
                    fixed.append(str(json_file))
                except Exception as e:
                    failed.append({"file": str(json_file), "error": str(e)})
        
        if failed:
            return FixResult(
                check_id="json_files_integrity",
                success=False,
                message=f"Fixed {len(fixed)}, failed {len(failed)}",
                before_status=DiagnosticStatus.ERROR,
                after_status=DiagnosticStatus.WARNING,
                actions_taken=[f"Fixed: {f}" for f in fixed]
            )
        else:
            return FixResult(
                check_id="json_files_integrity",
                success=True,
                message=f"Fixed {len(fixed)} corrupted files",
                before_status=DiagnosticStatus.ERROR,
                after_status=DiagnosticStatus.OK,
                actions_taken=[f"Fixed: {f}" for f in fixed]
            )
    
    async def _fix_config_files(self) -> FixResult:
        """Создание отсутствующих конфигурационных файлов"""
        default_configs = {
            "/home/ubuntu/seo_monster/backend/data/diagnostics/diagnostics_config.json": {
                "auto_mode_enabled": False,
                "auto_fix_enabled": False,
                "check_interval": 300
            },
            "/home/ubuntu/seo_monster/backend/data/autopilot/campaigns.json": [],
            "/home/ubuntu/seo_monster/backend/data/ses/keys.json": [],
            "/home/ubuntu/seo_monster/backend/data/tds/config.json": {
                "enabled": True,
                "default_redirect": "/"
            }
        }
        
        created = []
        for config_path, default_content in default_configs.items():
            path = Path(config_path)
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w') as f:
                    json.dump(default_content, f, indent=2)
                created.append(config_path)
        
        return FixResult(
            check_id="config_files",
            success=True,
            message=f"Created {len(created)} config files",
            before_status=DiagnosticStatus.WARNING,
            after_status=DiagnosticStatus.OK,
            actions_taken=[f"Created: {f}" for f in created]
        )
    
    async def _fix_temp_files(self) -> FixResult:
        """Очистка старых временных файлов"""
        temp_dirs = ["/tmp"]
        cutoff = datetime.now() - timedelta(days=7)
        deleted = []
        
        for temp_dir in temp_dirs:
            temp_path = Path(temp_dir)
            if temp_path.exists():
                for temp_file in temp_path.glob("seo_monster_*"):
                    if temp_file.is_file():
                        mtime = datetime.fromtimestamp(temp_file.stat().st_mtime)
                        if mtime < cutoff:
                            try:
                                temp_file.unlink()
                                deleted.append(str(temp_file))
                            except:
                                pass
        
        return FixResult(
            check_id="temp_files",
            success=True,
            message=f"Deleted {len(deleted)} old temp files",
            before_status=DiagnosticStatus.WARNING,
            after_status=DiagnosticStatus.OK,
            actions_taken=[f"Deleted: {f}" for f in deleted[:10]]
        )
    
    async def _fix_log_files(self) -> FixResult:
        """Ротация больших лог-файлов"""
        log_dirs = ["/home/ubuntu/seo_monster/backend/logs", "/tmp"]
        rotated = []
        
        for log_dir in log_dirs:
            log_path = Path(log_dir)
            if log_path.exists():
                for log_file in log_path.glob("*.log"):
                    if log_file.stat().st_size > 100 * 1024 * 1024:  # > 100MB
                        try:
                            # Ротация: переименовываем и создаем новый
                            backup = log_file.with_suffix('.log.old')
                            if backup.exists():
                                backup.unlink()
                            log_file.rename(backup)
                            log_file.touch()
                            rotated.append(str(log_file))
                        except:
                            pass
        
        return FixResult(
            check_id="log_files",
            success=True,
            message=f"Rotated {len(rotated)} log files",
            before_status=DiagnosticStatus.WARNING,
            after_status=DiagnosticStatus.OK,
            actions_taken=[f"Rotated: {f}" for f in rotated]
        )
    
    async def _fix_file_permissions(self) -> FixResult:
        """Исправление прав доступа к файлам"""
        fixed = []
        sensitive_paths = [
            "/home/ubuntu/seo_monster/backend/data",
            "/home/ubuntu/seo_monster/backend/services"
        ]
        
        for path_str in sensitive_paths:
            path = Path(path_str)
            if path.exists():
                try:
                    # Убираем world-writable
                    current_mode = path.stat().st_mode
                    new_mode = current_mode & ~0o002
                    if current_mode != new_mode:
                        os.chmod(path, new_mode)
                        fixed.append(path_str)
                except:
                    pass
        
        return FixResult(
            check_id="file_permissions",
            success=True,
            message=f"Fixed permissions on {len(fixed)} paths",
            before_status=DiagnosticStatus.WARNING,
            after_status=DiagnosticStatus.OK,
            actions_taken=[f"Fixed: {f}" for f in fixed]
        )
    
    async def _fix_frontend_build(self) -> FixResult:
        """Пересборка frontend"""
        try:
            result = subprocess.run(
                ["pnpm", "run", "build"],
                cwd="/home/ubuntu/seo_monster/frontend",
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return FixResult(
                    check_id="frontend_build",
                    success=True,
                    message="Frontend rebuilt successfully",
                    before_status=DiagnosticStatus.ERROR,
                    after_status=DiagnosticStatus.OK,
                    actions_taken=["Ran pnpm run build"]
                )
            else:
                return FixResult(
                    check_id="frontend_build",
                    success=False,
                    message=f"Build failed: {result.stderr[:200]}",
                    before_status=DiagnosticStatus.ERROR,
                    after_status=DiagnosticStatus.ERROR
                )
        except Exception as e:
            return FixResult(
                check_id="frontend_build",
                success=False,
                message=f"Build error: {str(e)}",
                before_status=DiagnosticStatus.ERROR,
                after_status=DiagnosticStatus.ERROR
            )
    
    # ==================== ОСНОВНЫЕ МЕТОДЫ ====================
    
    async def run_all_checks(self) -> List[DiagnosticResult]:
        """Запуск всех проверок"""
        results = []
        
        for check_id, check_info in self.checks.items():
            if "all" not in self.config.get("enabled_checks", ["all"]):
                if check_id not in self.config.get("enabled_checks", []):
                    continue
            
            if check_id in self.config.get("disabled_checks", []):
                continue
            
            try:
                start_time = time.time()
                result = await check_info["func"]()
                result.duration_ms = (time.time() - start_time) * 1000
                results.append(result)
                
                self._last_results[check_id] = result
                self._add_to_history(result)
                
                # Автоисправление
                if self.auto_fix_enabled and result.fix_available:
                    if result.status in [DiagnosticStatus.ERROR, DiagnosticStatus.WARNING]:
                        fix_result = await self.apply_fix(check_id)
                        if fix_result.success:
                            result.fix_applied = True
                            result.status = DiagnosticStatus.FIXED
                
            except Exception as e:
                logger.error(f"Check {check_id} failed: {str(e)}")
                results.append(DiagnosticResult(
                    check_id=check_id,
                    category=check_info["category"],
                    name=check_id,
                    status=DiagnosticStatus.ERROR,
                    message=f"Check failed: {str(e)}",
                    severity=check_info["severity"]
                ))
        
        self._last_full_check = datetime.now()
        return results
    
    async def run_quick_check(self) -> List[DiagnosticResult]:
        """Быстрая проверка критических компонентов"""
        quick_ids = self.config.get("quick_check_ids", [])
        results = []
        
        for check_id in quick_ids:
            if check_id in self.checks:
                try:
                    result = await self.checks[check_id]["func"]()
                    results.append(result)
                    self._last_results[check_id] = result
                except Exception as e:
                    results.append(DiagnosticResult(
                        check_id=check_id,
                        category=self.checks[check_id]["category"],
                        name=check_id,
                        status=DiagnosticStatus.ERROR,
                        message=f"Quick check failed: {str(e)}",
                        severity=self.checks[check_id]["severity"]
                    ))
        
        return results
    
    async def run_category_checks(self, category: DiagnosticCategory) -> List[DiagnosticResult]:
        """Запуск проверок по категории"""
        results = []
        
        for check_id, check_info in self.checks.items():
            if check_info["category"] == category:
                try:
                    result = await check_info["func"]()
                    results.append(result)
                    self._last_results[check_id] = result
                except Exception as e:
                    results.append(DiagnosticResult(
                        check_id=check_id,
                        category=category,
                        name=check_id,
                        status=DiagnosticStatus.ERROR,
                        message=f"Check failed: {str(e)}",
                        severity=check_info["severity"]
                    ))
        
        return results
    
    async def run_single_check(self, check_id: str) -> Optional[DiagnosticResult]:
        """Запуск одной проверки"""
        if check_id not in self.checks:
            return None
        
        try:
            result = await self.checks[check_id]["func"]()
            self._last_results[check_id] = result
            self._add_to_history(result)
            return result
        except Exception as e:
            return DiagnosticResult(
                check_id=check_id,
                category=self.checks[check_id]["category"],
                name=check_id,
                status=DiagnosticStatus.ERROR,
                message=f"Check failed: {str(e)}",
                severity=self.checks[check_id]["severity"]
            )
    
    async def apply_fix(self, check_id: str) -> FixResult:
        """Применение исправления"""
        if check_id not in self.fixes:
            return FixResult(
                check_id=check_id,
                success=False,
                message="No fix available for this check",
                before_status=DiagnosticStatus.ERROR,
                after_status=DiagnosticStatus.ERROR
            )
        
        try:
            result = await self.fixes[check_id]()
            self._add_fix_to_history(result)
            return result
        except Exception as e:
            result = FixResult(
                check_id=check_id,
                success=False,
                message=f"Fix failed: {str(e)}",
                before_status=DiagnosticStatus.ERROR,
                after_status=DiagnosticStatus.ERROR
            )
            self._add_fix_to_history(result)
            return result
    
    async def apply_all_fixes(self) -> List[FixResult]:
        """Применение всех доступных исправлений"""
        results = []
        check_results = await self.run_all_checks()
        
        for check_result in check_results:
            if check_result.fix_available:
                if check_result.status in [DiagnosticStatus.ERROR, DiagnosticStatus.WARNING]:
                    fix_result = await self.apply_fix(check_result.check_id)
                    results.append(fix_result)
        
        return results
    
    async def generate_health_report(self) -> SystemHealthReport:
        """Генерация отчета о здоровье системы"""
        results = await self.run_all_checks()
        
        # Подсчет статусов
        passed = sum(1 for r in results if r.status == DiagnosticStatus.OK)
        warnings = sum(1 for r in results if r.status == DiagnosticStatus.WARNING)
        errors = sum(1 for r in results if r.status == DiagnosticStatus.ERROR)
        critical = sum(1 for r in results if r.status == DiagnosticStatus.CRITICAL)
        fixed = sum(1 for r in results if r.status == DiagnosticStatus.FIXED)
        
        # Расчет health score
        total = len(results)
        if total > 0:
            # Веса: OK=100, Fixed=90, Warning=50, Error=20, Critical=0
            score = (
                passed * 100 + 
                fixed * 90 + 
                warnings * 50 + 
                errors * 20 + 
                critical * 0
            ) / total
        else:
            score = 100
        
        # Определение общего статуса
        if critical > 0:
            overall_status = DiagnosticStatus.CRITICAL
        elif errors > 0:
            overall_status = DiagnosticStatus.ERROR
        elif warnings > 0:
            overall_status = DiagnosticStatus.WARNING
        else:
            overall_status = DiagnosticStatus.OK
        
        # Группировка по категориям
        categories_summary = {}
        for result in results:
            cat = result.category.value
            if cat not in categories_summary:
                categories_summary[cat] = {"ok": 0, "warning": 0, "error": 0, "critical": 0}
            
            if result.status == DiagnosticStatus.OK:
                categories_summary[cat]["ok"] += 1
            elif result.status == DiagnosticStatus.WARNING:
                categories_summary[cat]["warning"] += 1
            elif result.status == DiagnosticStatus.ERROR:
                categories_summary[cat]["error"] += 1
            elif result.status == DiagnosticStatus.CRITICAL:
                categories_summary[cat]["critical"] += 1
        
        # Топ проблем
        issues = [r for r in results if r.status in [DiagnosticStatus.ERROR, DiagnosticStatus.CRITICAL, DiagnosticStatus.WARNING]]
        issues.sort(key=lambda x: (
            0 if x.status == DiagnosticStatus.CRITICAL else
            1 if x.status == DiagnosticStatus.ERROR else 2
        ))
        top_issues = [asdict(i) for i in issues[:10]]
        
        # Сбор рекомендаций
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)
        
        report = SystemHealthReport(
            overall_status=overall_status,
            health_score=int(score),
            total_checks=total,
            passed_checks=passed,
            warning_checks=warnings,
            error_checks=errors,
            critical_checks=critical,
            fixed_checks=fixed,
            categories_summary=categories_summary,
            top_issues=top_issues,
            recommendations=list(set(all_recommendations))[:20]
        )
        
        # Сохраняем отчет
        self.health_reports.append(asdict(report))
        max_reports = self.config.get("max_reports_size", 100)
        if len(self.health_reports) > max_reports:
            self.health_reports = self.health_reports[-max_reports:]
        self._save_json(self.reports_file, self.health_reports)
        
        return report
    
    def _add_to_history(self, result: DiagnosticResult):
        """Добавление результата в историю"""
        self.history.append(asdict(result))
        
        max_size = self.config.get("max_history_size", 1000)
        if len(self.history) > max_size:
            self.history = self.history[-max_size:]
        
        self._save_json(self.history_file, self.history)
    
    def _add_fix_to_history(self, result: FixResult):
        """Добавление результата исправления в историю"""
        self.fixes_history.append(asdict(result))
        self._save_json(self.fixes_file, self.fixes_history)
    
    # ==================== УПРАВЛЕНИЕ РЕЖИМАМИ ====================
    
    def set_auto_mode(self, enabled: bool):
        """Включение/выключение автоматического режима"""
        self.auto_mode_enabled = enabled
        self.config["auto_mode_enabled"] = enabled
        self._save_config()
        
        if enabled:
            self.start_auto_mode()
        else:
            self.stop_auto_mode()
    
    def set_auto_fix(self, enabled: bool):
        """Включение/выключение автоисправления"""
        self.auto_fix_enabled = enabled
        self.config["auto_fix_enabled"] = enabled
        self._save_config()
    
    def set_check_interval(self, seconds: int):
        """Установка интервала проверок"""
        self.check_interval = max(60, seconds)
        self.config["check_interval"] = self.check_interval
        self._save_config()
    
    def start_auto_mode(self):
        """Запуск автоматического режима"""
        if self._auto_thread and self._auto_thread.is_alive():
            return
        
        self._stop_auto.clear()
        self._auto_thread = threading.Thread(target=self._auto_check_loop, daemon=True)
        self._auto_thread.start()
        logger.info("Auto diagnostics mode started")
    
    def stop_auto_mode(self):
        """Остановка автоматического режима"""
        self._stop_auto.set()
        if self._auto_thread:
            self._auto_thread.join(timeout=5)
        logger.info("Auto diagnostics mode stopped")
    
    def _auto_check_loop(self):
        """Цикл автоматической проверки"""
        while not self._stop_auto.is_set():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.run_all_checks())
                loop.close()
            except Exception as e:
                logger.error(f"Auto check failed: {str(e)}")
            
            self._stop_auto.wait(self.check_interval)
    
    # ==================== ПОЛУЧЕНИЕ ДАННЫХ ====================
    
    def get_status(self) -> Dict:
        """Получение текущего статуса"""
        return {
            "auto_mode_enabled": self.auto_mode_enabled,
            "auto_fix_enabled": self.auto_fix_enabled,
            "check_interval": self.check_interval,
            "total_checks": len(self.checks),
            "total_fixes": len(self.fixes),
            "history_size": len(self.history),
            "fixes_history_size": len(self.fixes_history),
            "last_full_check": self._last_full_check.isoformat() if self._last_full_check else None,
            "categories": list(set(c["category"].value for c in self.checks.values()))
        }
    
    def get_history(self, limit: int = 50, status_filter: str = None, 
                   category_filter: str = None) -> List[Dict]:
        """Получение истории проверок"""
        history = self.history
        
        if status_filter:
            history = [h for h in history if h.get("status") == status_filter]
        
        if category_filter:
            history = [h for h in history if h.get("category") == category_filter]
        
        return history[-limit:][::-1]
    
    def get_fixes_history(self, limit: int = 50) -> List[Dict]:
        """Получение истории исправлений"""
        return self.fixes_history[-limit:][::-1]
    
    def get_health_reports(self, limit: int = 10) -> List[Dict]:
        """Получение истории отчетов о здоровье"""
        return self.health_reports[-limit:][::-1]
    
    def get_available_checks(self) -> List[Dict]:
        """Получение списка доступных проверок"""
        return [
            {
                "id": check_id,
                "category": check_info["category"].value,
                "severity": check_info["severity"].value,
                "has_fix": check_id in self.fixes
            }
            for check_id, check_info in self.checks.items()
        ]
    
    def get_last_results(self) -> List[Dict]:
        """Получение последних результатов по каждой проверке"""
        return [asdict(r) for r in self._last_results.values()]
    
    def get_categories(self) -> List[Dict]:
        """Получение списка категорий с количеством проверок"""
        categories = {}
        for check_info in self.checks.values():
            cat = check_info["category"].value
            if cat not in categories:
                categories[cat] = {"name": cat, "checks_count": 0, "has_fixes": 0}
            categories[cat]["checks_count"] += 1
        
        for check_id, check_info in self.checks.items():
            if check_id in self.fixes:
                categories[check_info["category"].value]["has_fixes"] += 1
        
        return list(categories.values())


# Глобальный экземпляр сервиса
_diagnostics_service: Optional[DiagnosticsService] = None


def get_diagnostics_service() -> DiagnosticsService:
    """Получение экземпляра сервиса диагностики"""
    global _diagnostics_service
    if _diagnostics_service is None:
        _diagnostics_service = DiagnosticsService()
    return _diagnostics_service
