"""
SEO Monster - AI Evolution System
Система автономного развития и самосовершенствования AI

Возможности:
- Автоматический анализ и улучшение системы
- Создание новых функций по необходимости
- Адаптация к изменениям
- Мониторинг и оптимизация производительности
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import traceback

# Пути
BASE_DIR = Path("/home/ubuntu/seo_monster")
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
EVOLUTION_DIR = DATA_DIR / "evolution"
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

# Файлы
EVOLUTION_LOG_FILE = EVOLUTION_DIR / "evolution_log.json"
IMPROVEMENTS_QUEUE_FILE = EVOLUTION_DIR / "improvements_queue.json"
SYSTEM_HEALTH_FILE = EVOLUTION_DIR / "system_health.json"
GOALS_FILE = EVOLUTION_DIR / "goals.json"
CAPABILITIES_FILE = EVOLUTION_DIR / "capabilities.json"


class AIEvolutionSystem:
    """
    Система автономного развития AI
    Анализирует, планирует и реализует улучшения
    """
    
    def __init__(self):
        self.evolution_log = self._load_json(EVOLUTION_LOG_FILE, [])
        self.improvements_queue = self._load_json(IMPROVEMENTS_QUEUE_FILE, [])
        self.system_health = self._load_json(SYSTEM_HEALTH_FILE, {"status": "unknown", "checks": []})
        self.goals = self._load_json(GOALS_FILE, {"active": [], "completed": [], "failed": []})
        self.capabilities = self._load_json(CAPABILITIES_FILE, {"current": [], "planned": []})
        
        # Импортируем зависимости
        self._import_dependencies()
    
    def _import_dependencies(self):
        """Импорт зависимостей"""
        try:
            from services.ai_agent_core import get_ai_agent
            from services.ai_code_generator import get_code_generator
            from services.ai_learning_engine import get_learning_engine
            
            self.agent = get_ai_agent()
            self.code_generator = get_code_generator()
            self.learning_engine = get_learning_engine()
        except Exception as e:
            print(f"Warning: Could not import dependencies: {e}")
            self.agent = None
            self.code_generator = None
            self.learning_engine = None
    
    def _load_json(self, path: Path, default) -> any:
        """Загрузка JSON"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, path: Path, data):
        """Сохранение JSON"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # МОНИТОРИНГ ЗДОРОВЬЯ СИСТЕМЫ
    # ═══════════════════════════════════════════════════════════════
    
    async def check_system_health(self) -> Dict:
        """
        Проверка здоровья системы
        Анализирует все компоненты
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "components": {},
            "issues": [],
            "recommendations": []
        }
        
        # Проверка backend
        backend_health = await self._check_backend()
        health["components"]["backend"] = backend_health
        if not backend_health.get("healthy"):
            health["issues"].append(f"Backend: {backend_health.get('error')}")
        
        # Проверка файловой системы
        fs_health = self._check_filesystem()
        health["components"]["filesystem"] = fs_health
        if not fs_health.get("healthy"):
            health["issues"].append(f"Filesystem: {fs_health.get('error')}")
        
        # Проверка данных
        data_health = self._check_data_integrity()
        health["components"]["data"] = data_health
        if not data_health.get("healthy"):
            health["issues"].append(f"Data: {data_health.get('error')}")
        
        # Проверка зависимостей
        deps_health = self._check_dependencies()
        health["components"]["dependencies"] = deps_health
        
        # Общий статус
        if health["issues"]:
            health["status"] = "degraded" if len(health["issues"]) < 3 else "unhealthy"
        
        # Генерируем рекомендации
        health["recommendations"] = self._generate_health_recommendations(health)
        
        # Сохраняем
        self.system_health = health
        self.system_health["checks"].append({
            "timestamp": health["timestamp"],
            "status": health["status"],
            "issues_count": len(health["issues"])
        })
        self.system_health["checks"] = self.system_health["checks"][-100:]
        self._save_json(SYSTEM_HEALTH_FILE, self.system_health)
        
        return health
    
    async def _check_backend(self) -> Dict:
        """Проверка backend"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/", timeout=5) as response:
                    if response.status == 200:
                        return {"healthy": True, "status": "running"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
        
        return {"healthy": False, "error": "Backend not responding"}
    
    def _check_filesystem(self) -> Dict:
        """Проверка файловой системы"""
        required_dirs = [
            BACKEND_DIR / "services",
            BACKEND_DIR / "app" / "api",
            DATA_DIR,
            BASE_DIR / "scripts"
        ]
        
        missing = []
        for d in required_dirs:
            if not d.exists():
                missing.append(str(d))
        
        if missing:
            return {"healthy": False, "error": f"Missing directories: {missing}"}
        
        return {"healthy": True, "directories": len(required_dirs)}
    
    def _check_data_integrity(self) -> Dict:
        """Проверка целостности данных"""
        issues = []
        
        # Проверяем JSON файлы
        json_files = list(DATA_DIR.rglob("*.json"))
        corrupted = []
        
        for f in json_files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    json.load(file)
            except:
                corrupted.append(str(f))
        
        if corrupted:
            return {"healthy": False, "error": f"Corrupted files: {corrupted[:5]}"}
        
        return {"healthy": True, "files_checked": len(json_files)}
    
    def _check_dependencies(self) -> Dict:
        """Проверка зависимостей"""
        required = ["fastapi", "uvicorn", "aiohttp", "openai", "pydantic"]
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        
        return {
            "healthy": len(missing) == 0,
            "missing": missing,
            "total_required": len(required)
        }
    
    def _generate_health_recommendations(self, health: Dict) -> List[str]:
        """Генерация рекомендаций по здоровью"""
        recommendations = []
        
        for issue in health.get("issues", []):
            if "Backend" in issue:
                recommendations.append("Перезапустить backend сервер")
            if "Filesystem" in issue:
                recommendations.append("Восстановить отсутствующие директории")
            if "Data" in issue:
                recommendations.append("Проверить и восстановить повреждённые файлы")
        
        return recommendations
    
    # ═══════════════════════════════════════════════════════════════
    # АВТОМАТИЧЕСКОЕ УЛУЧШЕНИЕ
    # ═══════════════════════════════════════════════════════════════
    
    async def auto_improve(self) -> Dict:
        """
        Автоматическое улучшение системы
        Анализирует и применяет улучшения
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "improvements_analyzed": 0,
            "improvements_applied": 0,
            "details": []
        }
        
        # 1. Анализируем систему
        analysis = await self._analyze_system()
        result["analysis"] = analysis
        
        # 2. Генерируем предложения по улучшению
        suggestions = self._generate_improvement_suggestions(analysis)
        result["suggestions"] = suggestions
        result["improvements_analyzed"] = len(suggestions)
        
        # 3. Применяем безопасные улучшения
        for suggestion in suggestions:
            if suggestion.get("safe", False) and suggestion.get("priority", 0) > 7:
                applied = await self._apply_improvement(suggestion)
                if applied.get("success"):
                    result["improvements_applied"] += 1
                    result["details"].append(applied)
        
        # Логируем
        self._log_evolution("auto_improve", result)
        
        return result
    
    async def _analyze_system(self) -> Dict:
        """Анализ системы для улучшений"""
        analysis = {
            "code_quality": {},
            "performance": {},
            "features": {},
            "errors": []
        }
        
        # Анализ кода
        python_files = list(BACKEND_DIR.rglob("*.py"))
        total_lines = 0
        files_without_docs = []
        
        for f in python_files:
            if "__pycache__" in str(f):
                continue
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    content = file.read()
                    lines = len(content.split('\n'))
                    total_lines += lines
                    
                    # Проверяем наличие docstring
                    if '"""' not in content[:500]:
                        files_without_docs.append(str(f.name))
            except:
                pass
        
        analysis["code_quality"] = {
            "total_files": len(python_files),
            "total_lines": total_lines,
            "files_without_docs": files_without_docs[:10],
            "needs_documentation": len(files_without_docs)
        }
        
        # Анализ функций
        services = list((BACKEND_DIR / "services").glob("*.py"))
        api_routes = list((BACKEND_DIR / "app" / "api").glob("*.py"))
        
        analysis["features"] = {
            "services_count": len(services),
            "api_routes_count": len(api_routes),
            "data_directories": len(list(DATA_DIR.iterdir())) if DATA_DIR.exists() else 0
        }
        
        return analysis
    
    def _generate_improvement_suggestions(self, analysis: Dict) -> List[Dict]:
        """Генерация предложений по улучшению"""
        suggestions = []
        
        # Предложения по документации
        needs_docs = analysis.get("code_quality", {}).get("needs_documentation", 0)
        if needs_docs > 5:
            suggestions.append({
                "type": "documentation",
                "description": f"Добавить документацию к {needs_docs} файлам",
                "priority": 5,
                "safe": True,
                "action": "add_documentation"
            })
        
        # Предложения по оптимизации
        total_lines = analysis.get("code_quality", {}).get("total_lines", 0)
        if total_lines > 10000:
            suggestions.append({
                "type": "optimization",
                "description": "Провести рефакторинг больших файлов",
                "priority": 6,
                "safe": False,
                "action": "refactor_large_files"
            })
        
        # Предложения по новым функциям
        if self.learning_engine:
            learning_stats = self.learning_engine.get_learning_stats()
            if learning_stats.get("patterns_learned", 0) > 50:
                suggestions.append({
                    "type": "feature",
                    "description": "Создать модуль предсказаний на основе обученных паттернов",
                    "priority": 8,
                    "safe": True,
                    "action": "create_prediction_module"
                })
        
        return suggestions
    
    async def _apply_improvement(self, suggestion: Dict) -> Dict:
        """Применение улучшения"""
        result = {
            "suggestion": suggestion,
            "success": False,
            "details": None
        }
        
        action = suggestion.get("action")
        
        try:
            if action == "add_documentation" and self.code_generator:
                # Добавляем документацию к файлам без неё
                files_without_docs = suggestion.get("files", [])[:3]
                for f in files_without_docs:
                    self.code_generator.refactor_code(f, "document")
                result["success"] = True
                result["details"] = f"Documented {len(files_without_docs)} files"
                
            elif action == "create_prediction_module" and self.agent:
                # Создаём новый модуль через агента
                response = await self.agent.create_module(
                    "SEO Predictor",
                    "Модуль предсказания SEO-результатов на основе машинного обучения"
                )
                result["success"] = response.get("success", False)
                result["details"] = response.get("response", "")
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ ЦЕЛЯМИ
    # ═══════════════════════════════════════════════════════════════
    
    def add_goal(self, description: str, priority: int = 5, deadline: str = None) -> Dict:
        """Добавление новой цели для AI"""
        goal = {
            "id": len(self.goals["active"]) + len(self.goals["completed"]) + 1,
            "description": description,
            "priority": priority,
            "deadline": deadline,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "progress": 0,
            "steps": []
        }
        
        self.goals["active"].append(goal)
        self._save_json(GOALS_FILE, self.goals)
        
        return goal
    
    async def work_on_goals(self) -> Dict:
        """Работа над активными целями"""
        result = {
            "goals_processed": 0,
            "progress_made": [],
            "completed": []
        }
        
        if not self.agent:
            return {"error": "Agent not available"}
        
        # Сортируем по приоритету
        active_goals = sorted(self.goals["active"], key=lambda x: x.get("priority", 0), reverse=True)
        
        for goal in active_goals[:3]:  # Работаем над топ-3 целями
            progress = await self._work_on_goal(goal)
            result["goals_processed"] += 1
            
            if progress.get("progress_made"):
                result["progress_made"].append({
                    "goal_id": goal["id"],
                    "description": goal["description"],
                    "progress": progress
                })
            
            if progress.get("completed"):
                goal["status"] = "completed"
                goal["completed_at"] = datetime.now().isoformat()
                self.goals["completed"].append(goal)
                self.goals["active"].remove(goal)
                result["completed"].append(goal["id"])
        
        self._save_json(GOALS_FILE, self.goals)
        return result
    
    async def _work_on_goal(self, goal: Dict) -> Dict:
        """Работа над конкретной целью"""
        prompt = f"""Работай над следующей целью:

Цель: {goal['description']}
Текущий прогресс: {goal['progress']}%
Предыдущие шаги: {goal.get('steps', [])}

Определи следующий шаг и выполни его. Если цель достигнута, сообщи об этом."""

        try:
            response = await self.agent.process_message(prompt)
            
            # Обновляем прогресс
            if response.get("success"):
                goal["progress"] = min(goal["progress"] + 10, 100)
                goal["steps"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": response.get("response", "")[:200]
                })
                
                return {
                    "progress_made": True,
                    "completed": goal["progress"] >= 100,
                    "response": response.get("response", "")[:500]
                }
        except Exception as e:
            return {"error": str(e)}
        
        return {"progress_made": False}
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ ВОЗМОЖНОСТЯМИ
    # ═══════════════════════════════════════════════════════════════
    
    def register_capability(self, name: str, description: str, module: str) -> Dict:
        """Регистрация новой возможности"""
        capability = {
            "name": name,
            "description": description,
            "module": module,
            "added_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.capabilities["current"].append(capability)
        self._save_json(CAPABILITIES_FILE, self.capabilities)
        
        return capability
    
    def get_capabilities(self) -> List[Dict]:
        """Получение списка возможностей"""
        return self.capabilities.get("current", [])
    
    async def develop_new_capability(self, description: str) -> Dict:
        """Разработка новой возможности"""
        if not self.agent:
            return {"error": "Agent not available"}
        
        prompt = f"""Разработай новую возможность для системы SEO Monster:

Описание: {description}

Создай необходимый код и интегрируй его в систему."""

        result = await self.agent.process_message(prompt)
        
        if result.get("success"):
            # Регистрируем новую возможность
            self.register_capability(
                name=description[:50],
                description=description,
                module="auto_generated"
            )
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # ЛОГИРОВАНИЕ
    # ═══════════════════════════════════════════════════════════════
    
    def _log_evolution(self, action: str, data: Dict):
        """Логирование эволюции"""
        self.evolution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data
        })
        self.evolution_log = self.evolution_log[-200:]
        self._save_json(EVOLUTION_LOG_FILE, self.evolution_log)
    
    def get_evolution_stats(self) -> Dict:
        """Получение статистики эволюции"""
        return {
            "total_evolutions": len(self.evolution_log),
            "active_goals": len(self.goals.get("active", [])),
            "completed_goals": len(self.goals.get("completed", [])),
            "capabilities": len(self.capabilities.get("current", [])),
            "system_status": self.system_health.get("status", "unknown"),
            "recent_evolutions": self.evolution_log[-5:]
        }


# Singleton
_evolution_system = None

def get_evolution_system() -> AIEvolutionSystem:
    """Получение экземпляра системы эволюции"""
    global _evolution_system
    if _evolution_system is None:
        _evolution_system = AIEvolutionSystem()
    return _evolution_system
