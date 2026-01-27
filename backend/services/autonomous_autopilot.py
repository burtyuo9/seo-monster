"""
SEO Monster - Автономный автопилот
Полностью автономная система для автоматического создания SEO-контента
Работает без внешних AI API
"""

import json
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from pathlib import Path
from enum import Enum
import time
import uuid


class AutopilotStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class AutopilotTask:
    """Задача автопилота"""
    def __init__(self, task_type: str, params: Dict):
        self.id = str(uuid.uuid4())[:8]
        self.type = task_type
        self.params = params
        self.status = "pending"
        self.result = None
        self.error = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None


class AutonomousAutopilot:
    """
    Полностью автономный автопилот SEO Monster.
    Автоматически анализирует сайты и генерирует контент без внешних API.
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.autopilot_dir = self.data_dir / "autopilot"
        self.autopilot_dir.mkdir(parents=True, exist_ok=True)
        
        # Состояние автопилота
        self.status = AutopilotStatus.STOPPED
        self.current_task = None
        self.task_queue: List[AutopilotTask] = []
        self.completed_tasks: List[AutopilotTask] = []
        self.logs: List[Dict] = []
        
        # Настройки
        self.settings = self._load_settings()
        
        # Фоновый поток
        self._thread = None
        self._stop_event = threading.Event()
        
        # Импортируем зависимости
        self._init_dependencies()
        
        # Загружаем историю
        self._load_history()
    
    def _init_dependencies(self):
        """Инициализация зависимостей"""
        try:
            from .autonomous_content_engine import AutonomousContentEngine
            from .autonomous_site_analyzer import AutonomousSiteAnalyzer
            
            self.content_engine = AutonomousContentEngine(str(self.data_dir))
            self.site_analyzer = AutonomousSiteAnalyzer(str(self.data_dir))
        except ImportError:
            # Fallback для прямого импорта
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from autonomous_content_engine import AutonomousContentEngine
            from autonomous_site_analyzer import AutonomousSiteAnalyzer
            
            self.content_engine = AutonomousContentEngine(str(self.data_dir))
            self.site_analyzer = AutonomousSiteAnalyzer(str(self.data_dir))
    
    def _load_settings(self) -> Dict:
        """Загрузка настроек автопилота"""
        settings_file = self.autopilot_dir / "settings.json"
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        default_settings = {
            "auto_analyze": True,
            "auto_generate": True,
            "articles_per_day": 5,
            "min_word_count": 800,
            "max_word_count": 2000,
            "languages": ["en", "ru"],
            "content_types": ["guide", "how_to", "listicle"],
            "schedule": {
                "enabled": True,
                "interval_hours": 4,
                "start_hour": 8,
                "end_hour": 22
            },
            "sites": [],
            "external_ai_enabled": False,  # Внешний AI выключен по умолчанию
            "external_ai_provider": None
        }
        
        self._save_settings(default_settings)
        return default_settings
    
    def _save_settings(self, settings: Dict = None):
        """Сохранение настроек"""
        if settings:
            self.settings = settings
        
        settings_file = self.autopilot_dir / "settings.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)
    
    def _load_history(self):
        """Загрузка истории задач"""
        history_file = self.autopilot_dir / "history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.logs = data.get("logs", [])[-100:]  # Последние 100 логов
    
    def _save_history(self):
        """Сохранение истории"""
        history_file = self.autopilot_dir / "history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({
                "logs": self.logs[-100:],
                "last_updated": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def _log(self, message: str, level: str = "info", details: Dict = None):
        """Добавление записи в лог"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "details": details or {}
        }
        self.logs.append(log_entry)
        self._save_history()
        print(f"[{level.upper()}] {message}")
    
    def start(self) -> Dict:
        """Запуск автопилота"""
        if self.status == AutopilotStatus.RUNNING:
            return {"success": False, "message": "Autopilot is already running"}
        
        self.status = AutopilotStatus.RUNNING
        self._stop_event.clear()
        
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        self._log("Autopilot started", "info")
        
        return {"success": True, "message": "Autopilot started successfully"}
    
    def stop(self) -> Dict:
        """Остановка автопилота"""
        if self.status == AutopilotStatus.STOPPED:
            return {"success": False, "message": "Autopilot is not running"}
        
        self._stop_event.set()
        self.status = AutopilotStatus.STOPPED
        
        if self._thread:
            self._thread.join(timeout=5)
        
        self._log("Autopilot stopped", "info")
        
        return {"success": True, "message": "Autopilot stopped successfully"}
    
    def pause(self) -> Dict:
        """Пауза автопилота"""
        if self.status != AutopilotStatus.RUNNING:
            return {"success": False, "message": "Autopilot is not running"}
        
        self.status = AutopilotStatus.PAUSED
        self._log("Autopilot paused", "info")
        
        return {"success": True, "message": "Autopilot paused"}
    
    def resume(self) -> Dict:
        """Возобновление автопилота"""
        if self.status != AutopilotStatus.PAUSED:
            return {"success": False, "message": "Autopilot is not paused"}
        
        self.status = AutopilotStatus.RUNNING
        self._log("Autopilot resumed", "info")
        
        return {"success": True, "message": "Autopilot resumed"}
    
    def _run_loop(self):
        """Основной цикл автопилота"""
        self._log("Autopilot loop started", "info")
        
        while not self._stop_event.is_set():
            try:
                if self.status == AutopilotStatus.PAUSED:
                    time.sleep(5)
                    continue
                
                # Проверяем расписание
                if not self._check_schedule():
                    time.sleep(60)
                    continue
                
                # Выполняем задачи
                self._process_tasks()
                
                # Автоматическое создание задач
                self._auto_create_tasks()
                
                # Пауза между итерациями
                time.sleep(30)
                
            except Exception as e:
                self._log(f"Error in autopilot loop: {str(e)}", "error")
                time.sleep(60)
        
        self._log("Autopilot loop ended", "info")
    
    def _check_schedule(self) -> bool:
        """Проверка расписания"""
        schedule = self.settings.get("schedule", {})
        if not schedule.get("enabled", True):
            return True
        
        current_hour = datetime.now().hour
        start_hour = schedule.get("start_hour", 0)
        end_hour = schedule.get("end_hour", 24)
        
        return start_hour <= current_hour < end_hour
    
    def _process_tasks(self):
        """Обработка очереди задач"""
        if not self.task_queue:
            return
        
        task = self.task_queue.pop(0)
        self.current_task = task
        task.status = "running"
        
        self._log(f"Processing task: {task.type}", "info", {"task_id": task.id})
        
        try:
            if task.type == "analyze_site":
                result = self._execute_analyze_site(task)
            elif task.type == "generate_content":
                result = self._execute_generate_content(task)
            elif task.type == "full_pipeline":
                result = self._execute_full_pipeline(task)
            else:
                result = {"error": f"Unknown task type: {task.type}"}
            
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()
            
            self._log(f"Task completed: {task.type}", "success", {"task_id": task.id})
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            task.completed_at = datetime.now().isoformat()
            
            self._log(f"Task failed: {task.type} - {str(e)}", "error", {"task_id": task.id})
        
        self.completed_tasks.append(task)
        self.current_task = None
    
    def _execute_analyze_site(self, task: AutopilotTask) -> Dict:
        """Выполнение анализа сайта"""
        url = task.params.get("url")
        if not url:
            return {"error": "URL not provided"}
        
        # Используем синхронный анализ
        result = self.site_analyzer.quick_analyze(url)
        
        self._log(f"Site analyzed: {url}", "success", {
            "seo_score": result.get("seo_score"),
            "keywords_found": len(result.get("keywords", {}))
        })
        
        return result
    
    def _execute_generate_content(self, task: AutopilotTask) -> Dict:
        """Выполнение генерации контента"""
        params = task.params
        
        topic = params.get("topic")
        keywords = params.get("keywords", [])
        content_type = params.get("content_type", "guide")
        language = params.get("language", "en")
        word_count = params.get("word_count", 1000)
        
        if not topic:
            return {"error": "Topic not provided"}
        
        # Генерируем контент
        result = self.content_engine.generate_article(
            topic=topic,
            keywords=keywords,
            content_type=content_type,
            word_count=word_count,
            language=language
        )
        
        self._log(f"Content generated: {topic}", "success", {
            "word_count": result.get("word_count"),
            "content_type": content_type,
            "language": language
        })
        
        return result
    
    def _execute_full_pipeline(self, task: AutopilotTask) -> Dict:
        """Выполнение полного пайплайна: анализ -> генерация"""
        url = task.params.get("url")
        language = task.params.get("language", "en")
        articles_count = task.params.get("articles_count", 3)
        
        if not url:
            return {"error": "URL not provided"}
        
        results = {
            "url": url,
            "analysis": None,
            "articles": [],
            "started_at": datetime.now().isoformat()
        }
        
        # Шаг 1: Анализ сайта
        self._log(f"Pipeline: Analyzing site {url}", "info")
        analysis = self.site_analyzer.quick_analyze(url)
        results["analysis"] = analysis
        
        if analysis.get("error"):
            return results
        
        # Шаг 2: Извлечение тем для контента
        keywords = analysis.get("keywords", {})
        top_keywords = list(keywords.keys())[:articles_count]
        
        if not top_keywords:
            # Если ключевых слов нет, используем заголовок
            title = analysis.get("title", "")
            if title:
                top_keywords = [title.split()[0]] if title.split() else ["content"]
        
        # Шаг 3: Генерация статей
        content_types = self.settings.get("content_types", ["guide", "how_to", "listicle"])
        
        for i, keyword in enumerate(top_keywords):
            content_type = content_types[i % len(content_types)]
            
            self._log(f"Pipeline: Generating article for '{keyword}'", "info")
            
            article = self.content_engine.generate_article(
                topic=keyword,
                keywords=list(keywords.keys())[:5],
                content_type=content_type,
                word_count=self.settings.get("min_word_count", 800),
                language=language
            )
            
            results["articles"].append(article)
            
            self._log(f"Pipeline: Article generated - {article.get('title')}", "success")
        
        results["completed_at"] = datetime.now().isoformat()
        results["articles_generated"] = len(results["articles"])
        
        self._log(f"Pipeline completed: {len(results['articles'])} articles generated", "success")
        
        return results
    
    def _auto_create_tasks(self):
        """Автоматическое создание задач"""
        # Проверяем, нужно ли создавать задачи
        if len(self.task_queue) >= 5:
            return
        
        sites = self.settings.get("sites", [])
        if not sites:
            return
        
        # Проверяем, сколько статей уже создано сегодня
        today = datetime.now().date().isoformat()
        articles_today = sum(
            1 for task in self.completed_tasks
            if task.type == "generate_content" 
            and task.completed_at 
            and task.completed_at.startswith(today)
        )
        
        max_articles = self.settings.get("articles_per_day", 5)
        if articles_today >= max_articles:
            return
        
        # Создаем задачу для случайного сайта
        import random
        site = random.choice(sites)
        
        task = AutopilotTask("full_pipeline", {
            "url": site.get("url"),
            "language": site.get("language", "en"),
            "articles_count": min(3, max_articles - articles_today)
        })
        
        self.task_queue.append(task)
        self._log(f"Auto-created task for site: {site.get('url')}", "info")
    
    def add_task(self, task_type: str, params: Dict) -> Dict:
        """Добавление задачи в очередь"""
        task = AutopilotTask(task_type, params)
        self.task_queue.append(task)
        
        self._log(f"Task added: {task_type}", "info", {"task_id": task.id})
        
        return {
            "success": True,
            "task_id": task.id,
            "message": f"Task added to queue. Position: {len(self.task_queue)}"
        }
    
    def add_site(self, url: str, name: str = None, language: str = "en") -> Dict:
        """Добавление сайта для мониторинга"""
        site = {
            "url": url,
            "name": name or url,
            "language": language,
            "added_at": datetime.now().isoformat()
        }
        
        self.settings["sites"].append(site)
        self._save_settings()
        
        self._log(f"Site added: {url}", "info")
        
        return {"success": True, "message": f"Site added: {url}"}
    
    def remove_site(self, url: str) -> Dict:
        """Удаление сайта"""
        self.settings["sites"] = [
            s for s in self.settings["sites"] 
            if s.get("url") != url
        ]
        self._save_settings()
        
        self._log(f"Site removed: {url}", "info")
        
        return {"success": True, "message": f"Site removed: {url}"}
    
    def get_status(self) -> Dict:
        """Получение статуса автопилота"""
        return {
            "status": self.status.value,
            "current_task": {
                "id": self.current_task.id,
                "type": self.current_task.type,
                "status": self.current_task.status
            } if self.current_task else None,
            "queue_length": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "sites_count": len(self.settings.get("sites", [])),
            "settings": {
                "auto_analyze": self.settings.get("auto_analyze"),
                "auto_generate": self.settings.get("auto_generate"),
                "articles_per_day": self.settings.get("articles_per_day"),
                "external_ai_enabled": self.settings.get("external_ai_enabled", False)
            }
        }
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        """Получение логов"""
        return self.logs[-limit:]
    
    def get_generated_articles(self) -> List[Dict]:
        """Получение списка сгенерированных статей"""
        return self.content_engine.get_generated_articles()
    
    def update_settings(self, new_settings: Dict) -> Dict:
        """Обновление настроек"""
        self.settings.update(new_settings)
        self._save_settings()
        
        self._log("Settings updated", "info", new_settings)
        
        return {"success": True, "message": "Settings updated"}
    
    def run_now(self, url: str, language: str = "en", articles_count: int = 3) -> Dict:
        """Немедленный запуск генерации для сайта"""
        self._log(f"Manual run started for: {url}", "info")
        
        task = AutopilotTask("full_pipeline", {
            "url": url,
            "language": language,
            "articles_count": articles_count
        })
        
        # Выполняем сразу, не добавляя в очередь
        self.current_task = task
        task.status = "running"
        
        try:
            result = self._execute_full_pipeline(task)
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()
            
            self.completed_tasks.append(task)
            self.current_task = None
            
            return {
                "success": True,
                "task_id": task.id,
                "result": result
            }
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            self.current_task = None
            
            return {
                "success": False,
                "task_id": task.id,
                "error": str(e)
            }


# Создаем глобальный экземпляр
autonomous_autopilot = AutonomousAutopilot()
