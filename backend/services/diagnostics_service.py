"""
SEO Monster - Diagnostics & Auto-Fix Service
Модуль диагностики и автоматического исправления ошибок
"""

import asyncio
import json
import os
import sys
import traceback
import importlib
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
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


class DiagnosticCategory(str, Enum):
    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    SERVICES = "services"
    CONFIGURATION = "configuration"
    DEPENDENCIES = "dependencies"
    PERFORMANCE = "performance"
    SECURITY = "security"


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
    timestamp: str = None
    
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
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class DiagnosticsService:
    """Сервис диагностики и автоисправления"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "/home/ubuntu/seo_monster/backend/data/diagnostics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы данных
        self.config_file = self.data_dir / "diagnostics_config.json"
        self.history_file = self.data_dir / "diagnostics_history.json"
        self.fixes_file = self.data_dir / "fixes_history.json"
        
        # Загружаем конфигурацию
        self.config = self._load_config()
        self.history: List[Dict] = self._load_json(self.history_file, [])
        self.fixes_history: List[Dict] = self._load_json(self.fixes_file, [])
        
        # Состояние автоматического режима
        self.auto_mode_enabled = self.config.get("auto_mode_enabled", False)
        self.auto_fix_enabled = self.config.get("auto_fix_enabled", False)
        self.check_interval = self.config.get("check_interval", 300)  # 5 минут
        
        # Фоновый поток для автоматической диагностики
        self._auto_thread: Optional[threading.Thread] = None
        self._stop_auto = threading.Event()
        
        # Регистрация проверок
        self.checks: Dict[str, Callable] = {}
        self.fixes: Dict[str, Callable] = {}
        self._register_default_checks()
        
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
            "max_history_size": 1000,
            "enabled_checks": ["all"],
            "disabled_checks": []
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
    
    def _register_default_checks(self):
        """Регистрация стандартных проверок"""
        
        # API проверки
        self.register_check("api_health", self._check_api_health, DiagnosticCategory.API)
        self.register_check("api_endpoints", self._check_api_endpoints, DiagnosticCategory.API)
        
        # Проверки файловой системы
        self.register_check("data_directories", self._check_data_directories, DiagnosticCategory.FILE_SYSTEM)
        self.register_check("json_files_integrity", self._check_json_files, DiagnosticCategory.FILE_SYSTEM)
        self.register_check("disk_space", self._check_disk_space, DiagnosticCategory.FILE_SYSTEM)
        
        # Проверки сервисов
        self.register_check("indexing_service", self._check_indexing_service, DiagnosticCategory.SERVICES)
        self.register_check("sessions_service", self._check_sessions_service, DiagnosticCategory.SERVICES)
        self.register_check("learning_service", self._check_learning_service, DiagnosticCategory.SERVICES)
        
        # Проверки конфигурации
        self.register_check("config_files", self._check_config_files, DiagnosticCategory.CONFIGURATION)
        self.register_check("environment_vars", self._check_environment_vars, DiagnosticCategory.CONFIGURATION)
        
        # Проверки зависимостей
        self.register_check("python_packages", self._check_python_packages, DiagnosticCategory.DEPENDENCIES)
        
        # Проверки производительности
        self.register_check("memory_usage", self._check_memory_usage, DiagnosticCategory.PERFORMANCE)
        
        # Регистрация исправлений
        self.register_fix("data_directories", self._fix_data_directories)
        self.register_fix("json_files_integrity", self._fix_json_files)
        self.register_fix("config_files", self._fix_config_files)
    
    def register_check(self, check_id: str, check_func: Callable, category: DiagnosticCategory):
        """Регистрация проверки"""
        self.checks[check_id] = {
            "func": check_func,
            "category": category
        }
    
    def register_fix(self, check_id: str, fix_func: Callable):
        """Регистрация исправления"""
        self.fixes[check_id] = fix_func
    
    # ==================== ПРОВЕРКИ ====================
    
    async def _check_api_health(self) -> DiagnosticResult:
        """Проверка здоровья API"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health", timeout=5) as resp:
                    if resp.status == 200:
                        return DiagnosticResult(
                            check_id="api_health",
                            category=DiagnosticCategory.API,
                            name="API Health Check",
                            status=DiagnosticStatus.OK,
                            message="API is healthy and responding"
                        )
                    else:
                        return DiagnosticResult(
                            check_id="api_health",
                            category=DiagnosticCategory.API,
                            name="API Health Check",
                            status=DiagnosticStatus.ERROR,
                            message=f"API returned status {resp.status}",
                            fix_available=False
                        )
        except Exception as e:
            return DiagnosticResult(
                check_id="api_health",
                category=DiagnosticCategory.API,
                name="API Health Check",
                status=DiagnosticStatus.CRITICAL,
                message=f"API is not responding: {str(e)}",
                fix_available=False
            )
    
    async def _check_api_endpoints(self) -> DiagnosticResult:
        """Проверка всех API endpoints"""
        endpoints = [
            "/api/sites/",
            "/api/platforms/",
            "/api/content/",
            "/api/tasks/",
            "/api/indexing/stats",
            "/api/sessions/stats",
            "/api/learning/stats",
            "/api/agent/status"
        ]
        
        errors = []
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    try:
                        async with session.get(f"http://localhost:8000{endpoint}", timeout=5) as resp:
                            if resp.status != 200:
                                errors.append(f"{endpoint}: status {resp.status}")
                    except Exception as e:
                        errors.append(f"{endpoint}: {str(e)}")
            
            if not errors:
                return DiagnosticResult(
                    check_id="api_endpoints",
                    category=DiagnosticCategory.API,
                    name="API Endpoints Check",
                    status=DiagnosticStatus.OK,
                    message=f"All {len(endpoints)} endpoints are working",
                    details={"checked_endpoints": len(endpoints)}
                )
            else:
                return DiagnosticResult(
                    check_id="api_endpoints",
                    category=DiagnosticCategory.API,
                    name="API Endpoints Check",
                    status=DiagnosticStatus.ERROR,
                    message=f"{len(errors)} endpoints have issues",
                    details={"errors": errors},
                    fix_available=False
                )
        except Exception as e:
            return DiagnosticResult(
                check_id="api_endpoints",
                category=DiagnosticCategory.API,
                name="API Endpoints Check",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to check endpoints: {str(e)}",
                fix_available=False
            )
    
    async def _check_data_directories(self) -> DiagnosticResult:
        """Проверка директорий данных"""
        required_dirs = [
            "/home/ubuntu/seo_monster/backend/data",
            "/home/ubuntu/seo_monster/backend/data/indexing",
            "/home/ubuntu/seo_monster/backend/data/sessions",
            "/home/ubuntu/seo_monster/backend/data/autopilot",
            "/home/ubuntu/seo_monster/backend/data/knowledge",
            "/home/ubuntu/seo_monster/backend/data/positions",
            "/home/ubuntu/seo_monster/backend/data/diagnostics"
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
                message="All required directories exist",
                details={"checked_dirs": len(required_dirs)}
            )
        else:
            return DiagnosticResult(
                check_id="data_directories",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Data Directories Check",
                status=DiagnosticStatus.WARNING,
                message=f"{len(missing)} directories are missing",
                details={"missing": missing},
                fix_available=True
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
                details={"checked_files": checked}
            )
        else:
            return DiagnosticResult(
                check_id="json_files_integrity",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="JSON Files Integrity",
                status=DiagnosticStatus.ERROR,
                message=f"{len(corrupted)} JSON files are corrupted",
                details={"corrupted": corrupted},
                fix_available=True
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
            elif free_gb < 5:
                status = DiagnosticStatus.WARNING
                message = f"Warning: Only {free_gb:.2f} GB free"
            else:
                status = DiagnosticStatus.OK
                message = f"Disk space OK: {free_gb:.2f} GB free"
            
            return DiagnosticResult(
                check_id="disk_space",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Disk Space Check",
                status=status,
                message=message,
                details={
                    "total_gb": total / (1024 ** 3),
                    "used_gb": used / (1024 ** 3),
                    "free_gb": free_gb,
                    "used_percent": used_percent
                }
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="disk_space",
                category=DiagnosticCategory.FILE_SYSTEM,
                name="Disk Space Check",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to check disk space: {str(e)}"
            )
    
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
                details=stats
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="indexing_service",
                category=DiagnosticCategory.SERVICES,
                name="Indexing Service Check",
                status=DiagnosticStatus.ERROR,
                message=f"Indexing service error: {str(e)}",
                fix_available=False
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
                details=stats
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="sessions_service",
                category=DiagnosticCategory.SERVICES,
                name="Sessions Service Check",
                status=DiagnosticStatus.ERROR,
                message=f"Sessions service error: {str(e)}",
                fix_available=False
            )
    
    async def _check_learning_service(self) -> DiagnosticResult:
        """Проверка сервиса обучения"""
        try:
            from services.learning_service import LearningService
            service = LearningService()
            stats = service.get_stats()
            
            return DiagnosticResult(
                check_id="learning_service",
                category=DiagnosticCategory.SERVICES,
                name="Learning Service Check",
                status=DiagnosticStatus.OK,
                message="Learning service is working",
                details=stats
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="learning_service",
                category=DiagnosticCategory.SERVICES,
                name="Learning Service Check",
                status=DiagnosticStatus.ERROR,
                message=f"Learning service error: {str(e)}",
                fix_available=False
            )
    
    async def _check_config_files(self) -> DiagnosticResult:
        """Проверка конфигурационных файлов"""
        config_files = [
            "/home/ubuntu/seo_monster/backend/data/diagnostics/diagnostics_config.json",
            "/home/ubuntu/seo_monster/backend/data/autopilot/campaigns.json"
        ]
        
        missing = []
        for config_path in config_files:
            if not Path(config_path).exists():
                missing.append(config_path)
        
        if not missing:
            return DiagnosticResult(
                check_id="config_files",
                category=DiagnosticCategory.CONFIGURATION,
                name="Config Files Check",
                status=DiagnosticStatus.OK,
                message="All config files exist"
            )
        else:
            return DiagnosticResult(
                check_id="config_files",
                category=DiagnosticCategory.CONFIGURATION,
                name="Config Files Check",
                status=DiagnosticStatus.WARNING,
                message=f"{len(missing)} config files missing",
                details={"missing": missing},
                fix_available=True
            )
    
    async def _check_environment_vars(self) -> DiagnosticResult:
        """Проверка переменных окружения"""
        required_vars = ["OPENAI_API_KEY"]
        missing = []
        
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)
        
        if not missing:
            return DiagnosticResult(
                check_id="environment_vars",
                category=DiagnosticCategory.CONFIGURATION,
                name="Environment Variables Check",
                status=DiagnosticStatus.OK,
                message="All required environment variables are set"
            )
        else:
            return DiagnosticResult(
                check_id="environment_vars",
                category=DiagnosticCategory.CONFIGURATION,
                name="Environment Variables Check",
                status=DiagnosticStatus.WARNING,
                message=f"{len(missing)} environment variables missing",
                details={"missing": missing}
            )
    
    async def _check_python_packages(self) -> DiagnosticResult:
        """Проверка Python пакетов"""
        required_packages = [
            "fastapi", "uvicorn", "aiohttp", "openai", "pydantic"
        ]
        
        missing = []
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing.append(package)
        
        if not missing:
            return DiagnosticResult(
                check_id="python_packages",
                category=DiagnosticCategory.DEPENDENCIES,
                name="Python Packages Check",
                status=DiagnosticStatus.OK,
                message="All required packages are installed"
            )
        else:
            return DiagnosticResult(
                check_id="python_packages",
                category=DiagnosticCategory.DEPENDENCIES,
                name="Python Packages Check",
                status=DiagnosticStatus.ERROR,
                message=f"{len(missing)} packages are missing",
                details={"missing": missing}
            )
    
    async def _check_memory_usage(self) -> DiagnosticResult:
        """Проверка использования памяти"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = DiagnosticStatus.CRITICAL
                message = f"Critical: Memory usage at {memory.percent}%"
            elif memory.percent > 75:
                status = DiagnosticStatus.WARNING
                message = f"Warning: Memory usage at {memory.percent}%"
            else:
                status = DiagnosticStatus.OK
                message = f"Memory usage OK: {memory.percent}%"
            
            return DiagnosticResult(
                check_id="memory_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="Memory Usage Check",
                status=status,
                message=message,
                details={
                    "total_gb": memory.total / (1024 ** 3),
                    "available_gb": memory.available / (1024 ** 3),
                    "percent_used": memory.percent
                }
            )
        except ImportError:
            return DiagnosticResult(
                check_id="memory_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="Memory Usage Check",
                status=DiagnosticStatus.WARNING,
                message="psutil not installed, cannot check memory"
            )
        except Exception as e:
            return DiagnosticResult(
                check_id="memory_usage",
                category=DiagnosticCategory.PERFORMANCE,
                name="Memory Usage Check",
                status=DiagnosticStatus.ERROR,
                message=f"Failed to check memory: {str(e)}"
            )
    
    # ==================== ИСПРАВЛЕНИЯ ====================
    
    async def _fix_data_directories(self) -> FixResult:
        """Исправление: создание отсутствующих директорий"""
        required_dirs = [
            "/home/ubuntu/seo_monster/backend/data",
            "/home/ubuntu/seo_monster/backend/data/indexing",
            "/home/ubuntu/seo_monster/backend/data/sessions",
            "/home/ubuntu/seo_monster/backend/data/autopilot",
            "/home/ubuntu/seo_monster/backend/data/knowledge",
            "/home/ubuntu/seo_monster/backend/data/positions",
            "/home/ubuntu/seo_monster/backend/data/diagnostics"
        ]
        
        try:
            created = []
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
                after_status=DiagnosticStatus.OK
            )
        except Exception as e:
            return FixResult(
                check_id="data_directories",
                success=False,
                message=f"Failed to create directories: {str(e)}",
                before_status=DiagnosticStatus.WARNING,
                after_status=DiagnosticStatus.ERROR
            )
    
    async def _fix_json_files(self) -> FixResult:
        """Исправление: восстановление поврежденных JSON файлов"""
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
                    
                    # Создаем пустой валидный JSON
                    with open(json_file, 'w') as f:
                        json.dump([], f)
                    
                    fixed.append(str(json_file))
                except Exception as e:
                    failed.append({"file": str(json_file), "error": str(e)})
        
        if failed:
            return FixResult(
                check_id="json_files_integrity",
                success=False,
                message=f"Fixed {len(fixed)}, failed {len(failed)}",
                before_status=DiagnosticStatus.ERROR,
                after_status=DiagnosticStatus.WARNING
            )
        else:
            return FixResult(
                check_id="json_files_integrity",
                success=True,
                message=f"Fixed {len(fixed)} corrupted files",
                before_status=DiagnosticStatus.ERROR,
                after_status=DiagnosticStatus.OK
            )
    
    async def _fix_config_files(self) -> FixResult:
        """Исправление: создание отсутствующих конфигурационных файлов"""
        default_configs = {
            "/home/ubuntu/seo_monster/backend/data/diagnostics/diagnostics_config.json": {
                "auto_mode_enabled": False,
                "auto_fix_enabled": False,
                "check_interval": 300
            },
            "/home/ubuntu/seo_monster/backend/data/autopilot/campaigns.json": []
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
            after_status=DiagnosticStatus.OK
        )
    
    # ==================== ОСНОВНЫЕ МЕТОДЫ ====================
    
    async def run_all_checks(self) -> List[DiagnosticResult]:
        """Запуск всех проверок"""
        results = []
        
        for check_id, check_info in self.checks.items():
            # Проверяем, включена ли проверка
            if "all" not in self.config.get("enabled_checks", ["all"]):
                if check_id not in self.config.get("enabled_checks", []):
                    continue
            
            if check_id in self.config.get("disabled_checks", []):
                continue
            
            try:
                result = await check_info["func"]()
                results.append(result)
                
                # Сохраняем в историю
                self._add_to_history(result)
                
                # Автоисправление если включено
                if self.auto_fix_enabled and result.fix_available and result.status in [DiagnosticStatus.ERROR, DiagnosticStatus.WARNING]:
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
                    message=f"Check failed: {str(e)}"
                ))
        
        return results
    
    async def run_single_check(self, check_id: str) -> Optional[DiagnosticResult]:
        """Запуск одной проверки"""
        if check_id not in self.checks:
            return None
        
        try:
            result = await self.checks[check_id]["func"]()
            self._add_to_history(result)
            return result
        except Exception as e:
            return DiagnosticResult(
                check_id=check_id,
                category=self.checks[check_id]["category"],
                name=check_id,
                status=DiagnosticStatus.ERROR,
                message=f"Check failed: {str(e)}"
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
        
        # Сначала запускаем диагностику
        check_results = await self.run_all_checks()
        
        # Применяем исправления для проблем
        for check_result in check_results:
            if check_result.fix_available and check_result.status in [DiagnosticStatus.ERROR, DiagnosticStatus.WARNING]:
                fix_result = await self.apply_fix(check_result.check_id)
                results.append(fix_result)
        
        return results
    
    def _add_to_history(self, result: DiagnosticResult):
        """Добавление результата в историю"""
        self.history.append(asdict(result))
        
        # Ограничиваем размер истории
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
        self.check_interval = max(60, seconds)  # Минимум 1 минута
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
                # Запускаем проверки в asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.run_all_checks())
                loop.close()
            except Exception as e:
                logger.error(f"Auto check failed: {str(e)}")
            
            # Ждем следующего интервала
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
            "fixes_history_size": len(self.fixes_history)
        }
    
    def get_history(self, limit: int = 50, status_filter: str = None) -> List[Dict]:
        """Получение истории проверок"""
        history = self.history
        
        if status_filter:
            history = [h for h in history if h.get("status") == status_filter]
        
        return history[-limit:][::-1]
    
    def get_fixes_history(self, limit: int = 50) -> List[Dict]:
        """Получение истории исправлений"""
        return self.fixes_history[-limit:][::-1]
    
    def get_available_checks(self) -> List[Dict]:
        """Получение списка доступных проверок"""
        return [
            {
                "id": check_id,
                "category": check_info["category"].value,
                "has_fix": check_id in self.fixes
            }
            for check_id, check_info in self.checks.items()
        ]
    
    def get_last_results(self) -> List[Dict]:
        """Получение последних результатов по каждой проверке"""
        last_results = {}
        
        for item in reversed(self.history):
            check_id = item.get("check_id")
            if check_id and check_id not in last_results:
                last_results[check_id] = item
        
        return list(last_results.values())


# Глобальный экземпляр сервиса
_diagnostics_service: Optional[DiagnosticsService] = None


def get_diagnostics_service() -> DiagnosticsService:
    """Получение экземпляра сервиса диагностики"""
    global _diagnostics_service
    if _diagnostics_service is None:
        _diagnostics_service = DiagnosticsService()
    return _diagnostics_service
