"""
SEO Monster - Autonomous AI Agent Core
Ядро автономного AI-агента с возможностью самообучения и самомодификации

Возможности:
- Понимание естественного языка и выполнение задач
- Анализ результатов и самообучение
- Генерация и модификация кода
- Автономное развитие системы
"""

import os
import sys
import json
import asyncio
import subprocess
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from abc import ABC, abstractmethod

# OpenAI API
try:
    from openai import OpenAI
except ImportError:
    os.system("pip3 install openai")
    from openai import OpenAI

# Пути
BASE_DIR = Path("/home/ubuntu/seo_monster")
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
AGENT_DIR = DATA_DIR / "agent"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
AGENT_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

# Импорт загрузчика знаний
try:
    from services.knowledge_loader import get_knowledge_loader
except ImportError:
    from knowledge_loader import get_knowledge_loader

# Файлы данных агента
MEMORY_FILE = AGENT_DIR / "memory.json"
LEARNING_FILE = AGENT_DIR / "learning.json"
CODE_HISTORY_FILE = AGENT_DIR / "code_history.json"
IMPROVEMENTS_FILE = AGENT_DIR / "improvements.json"
AGENT_CONFIG_FILE = AGENT_DIR / "config.json"


class Tool(ABC):
    """Базовый класс для инструментов агента"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict:
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict:
        pass


class FileReadTool(Tool):
    """Инструмент чтения файлов"""
    
    @property
    def name(self) -> str:
        return "read_file"
    
    @property
    def description(self) -> str:
        return "Читает содержимое файла по указанному пути"
    
    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Путь к файлу"}
            },
            "required": ["path"]
        }
    
    async def execute(self, path: str) -> Dict:
        try:
            full_path = Path(path)
            if not full_path.exists():
                return {"error": f"Файл не найден: {path}"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {"success": True, "content": content, "path": path}
        except Exception as e:
            return {"error": str(e)}


class FileWriteTool(Tool):
    """Инструмент записи файлов"""
    
    @property
    def name(self) -> str:
        return "write_file"
    
    @property
    def description(self) -> str:
        return "Записывает содержимое в файл. Создаёт директории при необходимости."
    
    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Путь к файлу"},
                "content": {"type": "string", "description": "Содержимое для записи"}
            },
            "required": ["path", "content"]
        }
    
    async def execute(self, path: str, content: str) -> Dict:
        try:
            full_path = Path(path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Создаём бэкап если файл существует
            if full_path.exists():
                backup_path = AGENT_DIR / "backups" / f"{full_path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, 'r', encoding='utf-8') as f:
                    with open(backup_path, 'w', encoding='utf-8') as bf:
                        bf.write(f.read())
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {"success": True, "path": path, "bytes_written": len(content)}
        except Exception as e:
            return {"error": str(e)}


class ExecuteCodeTool(Tool):
    """Инструмент выполнения Python кода"""
    
    @property
    def name(self) -> str:
        return "execute_python"
    
    @property
    def description(self) -> str:
        return "Выполняет Python код и возвращает результат. Используйте для тестирования и проверки."
    
    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python код для выполнения"}
            },
            "required": ["code"]
        }
    
    async def execute(self, code: str) -> Dict:
        try:
            # Сохраняем код во временный файл
            temp_file = AGENT_DIR / "temp_code.py"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Выполняем
            result = subprocess.run(
                ['python3', str(temp_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(BACKEND_DIR)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout: код выполнялся слишком долго"}
        except Exception as e:
            return {"error": str(e)}


class ShellCommandTool(Tool):
    """Инструмент выполнения shell команд"""
    
    @property
    def name(self) -> str:
        return "shell_command"
    
    @property
    def description(self) -> str:
        return "Выполняет shell команду. Используйте осторожно."
    
    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell команда"}
            },
            "required": ["command"]
        }
    
    async def execute(self, command: str) -> Dict:
        # Запрещённые команды
        forbidden = ['rm -rf /', 'dd if=', ':(){', 'mkfs', 'chmod -R 777 /']
        for f in forbidden:
            if f in command:
                return {"error": f"Запрещённая команда: {f}"}
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(BASE_DIR)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:5000],  # Ограничиваем вывод
                "stderr": result.stderr[:1000],
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout"}
        except Exception as e:
            return {"error": str(e)}


class ListFilesTool(Tool):
    """Инструмент просмотра файлов"""
    
    @property
    def name(self) -> str:
        return "list_files"
    
    @property
    def description(self) -> str:
        return "Показывает список файлов в директории"
    
    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Путь к директории"},
                "pattern": {"type": "string", "description": "Паттерн для фильтрации (например, *.py)"}
            },
            "required": ["path"]
        }
    
    async def execute(self, path: str, pattern: str = "*") -> Dict:
        try:
            dir_path = Path(path)
            if not dir_path.exists():
                return {"error": f"Директория не найдена: {path}"}
            
            files = list(dir_path.glob(pattern))
            
            result = []
            for f in files[:100]:  # Ограничиваем
                result.append({
                    "name": f.name,
                    "path": str(f),
                    "is_dir": f.is_dir(),
                    "size": f.stat().st_size if f.is_file() else 0
                })
            
            return {"success": True, "files": result, "total": len(files)}
        except Exception as e:
            return {"error": str(e)}


class SearchCodeTool(Tool):
    """Инструмент поиска в коде"""
    
    @property
    def name(self) -> str:
        return "search_code"
    
    @property
    def description(self) -> str:
        return "Ищет текст в файлах проекта"
    
    @property
    def parameters(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Текст для поиска"},
                "file_pattern": {"type": "string", "description": "Паттерн файлов (например, *.py)"}
            },
            "required": ["query"]
        }
    
    async def execute(self, query: str, file_pattern: str = "*.py") -> Dict:
        try:
            results = []
            
            for file_path in BACKEND_DIR.rglob(file_pattern):
                if '__pycache__' in str(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            results.append({
                                "file": str(file_path),
                                "line": i + 1,
                                "content": line.strip()[:200]
                            })
                except:
                    continue
            
            return {"success": True, "results": results[:50], "total": len(results)}
        except Exception as e:
            return {"error": str(e)}


class AutonomousAIAgent:
    """
    Автономный AI-агент с возможностью самообучения и самомодификации
    """
    
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"  # Или другая модель
        
        # Инструменты агента
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()
        
        # Загружаем данные
        self.memory = self._load_memory()
        self.learning_data = self._load_learning()
        self.code_history = self._load_code_history()
        self.config = self._load_config()
        
        # Системный промпт
        self.system_prompt = self._build_system_prompt()
        
        # Список возможностей
        self.capabilities = [
            "natural_language_understanding",
            "code_generation",
            "code_modification",
            "error_fixing",
            "self_learning",
            "task_automation",
            "seo_optimization",
            "content_generation",
            "data_analysis"
        ]
    
    def _register_default_tools(self):
        """Регистрация стандартных инструментов"""
        tools = [
            FileReadTool(),
            FileWriteTool(),
            ExecuteCodeTool(),
            ShellCommandTool(),
            ListFilesTool(),
            SearchCodeTool(),
        ]
        for tool in tools:
            self.tools[tool.name] = tool
    
    def _load_memory(self) -> Dict:
        """Загрузка памяти агента"""
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "conversations": [],
            "learned_patterns": [],
            "successful_solutions": [],
            "failed_attempts": [],
            "knowledge_base": {}
        }
    
    def _save_memory(self):
        """Сохранение памяти"""
        # Ограничиваем размер
        self.memory["conversations"] = self.memory["conversations"][-100:]
        self.memory["successful_solutions"] = self.memory["successful_solutions"][-200:]
        self.memory["failed_attempts"] = self.memory["failed_attempts"][-100:]
        
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def _load_learning(self) -> Dict:
        """Загрузка данных обучения"""
        if LEARNING_FILE.exists():
            try:
                with open(LEARNING_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "patterns": [],
            "optimizations": [],
            "error_solutions": {},
            "performance_metrics": []
        }
    
    def _save_learning(self):
        """Сохранение данных обучения"""
        with open(LEARNING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
    
    def _load_code_history(self) -> List[Dict]:
        """Загрузка истории изменений кода"""
        if CODE_HISTORY_FILE.exists():
            try:
                with open(CODE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_code_history(self):
        """Сохранение истории кода"""
        self.code_history = self.code_history[-500:]
        with open(CODE_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.code_history, f, indent=2, ensure_ascii=False)
    
    def _load_config(self) -> Dict:
        """Загрузка конфигурации"""
        if AGENT_CONFIG_FILE.exists():
            try:
                with open(AGENT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "auto_improve": True,
            "auto_fix_errors": True,
            "learning_enabled": True,
            "max_iterations": 10,
            "safety_mode": True
        }
    
    def _save_config(self):
        """Сохранение конфигурации"""
        with open(AGENT_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _build_system_prompt(self) -> str:
        """Построение системного промпта"""
        return """Ты — автономный AI-агент системы SEO Monster. Ты умный, способный к самообучению и можешь модифицировать свой собственный код.

ТВОИ ВОЗМОЖНОСТИ:
1. Понимание задач на естественном языке
2. Анализ и модификация кода системы
3. Создание новых модулей и функций
4. Исправление ошибок автоматически
5. Оптимизация существующего кода
6. Самообучение на основе результатов

СТРУКТУРА ПРОЕКТА:
- /home/ubuntu/seo_monster/backend/ — бэкенд на FastAPI
- /home/ubuntu/seo_monster/backend/services/ — сервисы и бизнес-логика
- /home/ubuntu/seo_monster/backend/app/api/ — API роуты
- /home/ubuntu/seo_monster/frontend/ — React фронтенд
- /home/ubuntu/seo_monster/scripts/ — скрипты автоматизации

ПРАВИЛА:
1. Всегда создавай бэкап перед изменением файлов
2. Тестируй код перед применением
3. Документируй изменения
4. Учись на ошибках и успехах
5. Не удаляй критические файлы
6. Сохраняй обратную совместимость

ПРОЦЕСС РАБОТЫ:
1. Анализируй задачу
2. Изучай существующий код
3. Планируй изменения
4. Реализуй пошагово
5. Тестируй результат
6. Запоминай успешные решения

Отвечай на русском языке. Будь проактивным и предлагай улучшения."""
    
    def _get_tools_schema(self) -> List[Dict]:
        """Получение схемы инструментов для OpenAI"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools.values()
        ]
    
    async def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Выполнение инструмента"""
        if tool_name not in self.tools:
            return {"error": f"Инструмент не найден: {tool_name}"}
        
        tool = self.tools[tool_name]
        result = await tool.execute(**arguments)
        
        # Логируем использование инструмента
        self._log_tool_usage(tool_name, arguments, result)
        
        return result
    
    def _log_tool_usage(self, tool_name: str, args: Dict, result: Dict):
        """Логирование использования инструментов"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "arguments": {k: str(v)[:100] for k, v in args.items()},
            "success": result.get("success", "error" not in result)
        }
        
        # Сохраняем в историю кода если это изменение файла
        if tool_name == "write_file":
            self.code_history.append({
                **log_entry,
                "file": args.get("path"),
                "content_preview": args.get("content", "")[:200]
            })
            self._save_code_history()
    
    async def process_message(self, user_message: str, context: Optional[Dict] = None) -> Dict:
        """
        Обработка сообщения пользователя
        Основной метод взаимодействия с агентом
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Добавляем контекст из памяти
        relevant_memory = self._get_relevant_memory(user_message)
        if relevant_memory:
            messages.append({
                "role": "system",
                "content": f"Релевантный опыт из памяти:\n{relevant_memory}"
            })
        
        # Добавляем сообщение пользователя
        messages.append({"role": "user", "content": user_message})
        
        # Итеративный процесс с инструментами
        iterations = 0
        max_iterations = self.config.get("max_iterations", 10)
        final_response = None
        tool_results = []
        
        while iterations < max_iterations:
            iterations += 1
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self._get_tools_schema(),
                    tool_choice="auto"
                )
                
                assistant_message = response.choices[0].message
                messages.append(assistant_message)
                
                # Если есть вызовы инструментов
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        # Выполняем инструмент
                        result = await self._execute_tool(tool_name, arguments)
                        tool_results.append({
                            "tool": tool_name,
                            "result": result
                        })
                        
                        # Добавляем результат в сообщения
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })
                else:
                    # Нет вызовов инструментов — финальный ответ
                    final_response = assistant_message.content
                    break
                    
            except Exception as e:
                error_msg = f"Ошибка: {str(e)}"
                self._learn_from_error(user_message, error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "iterations": iterations
                }
        
        # Сохраняем в память
        self._save_to_memory(user_message, final_response, tool_results)
        
        # Анализируем для обучения
        if self.config.get("learning_enabled", True):
            self._analyze_and_learn(user_message, final_response, tool_results)
        
        return {
            "success": True,
            "response": final_response,
            "tool_results": tool_results,
            "iterations": iterations
        }
    
    def _get_relevant_memory(self, query: str) -> str:
        """Получение релевантной информации из памяти"""
        relevant = []
        
        # Ищем похожие успешные решения
        for solution in self.memory.get("successful_solutions", [])[-20:]:
            if any(word in solution.get("query", "").lower() for word in query.lower().split()):
                relevant.append(f"Успешное решение: {solution.get('summary', '')}")
        
        # Ищем в базе знаний
        for key, value in self.memory.get("knowledge_base", {}).items():
            if key.lower() in query.lower():
                relevant.append(f"Знание ({key}): {value}")
        
        return "\n".join(relevant[:5]) if relevant else ""
    
    def _save_to_memory(self, query: str, response: str, tool_results: List[Dict]):
        """Сохранение в память"""
        self.memory["conversations"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response[:500] if response else "",
            "tools_used": [r["tool"] for r in tool_results]
        })
        
        # Если были успешные изменения кода
        code_changes = [r for r in tool_results if r["tool"] == "write_file" and r["result"].get("success")]
        if code_changes:
            self.memory["successful_solutions"].append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "summary": response[:200] if response else "",
                "files_changed": [r["result"].get("path") for r in code_changes]
            })
        
        self._save_memory()
    
    def _learn_from_error(self, query: str, error: str):
        """Обучение на ошибках"""
        self.memory["failed_attempts"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "error": error
        })
        
        # Анализируем паттерн ошибки
        error_key = error.split(":")[0] if ":" in error else error[:50]
        if error_key not in self.learning_data["error_solutions"]:
            self.learning_data["error_solutions"][error_key] = []
        
        self._save_memory()
        self._save_learning()
    
    def _analyze_and_learn(self, query: str, response: str, tool_results: List[Dict]):
        """Анализ и обучение"""
        # Извлекаем паттерны
        patterns = []
        
        # Паттерн: какие инструменты использовались для какого типа задач
        tools_used = [r["tool"] for r in tool_results]
        if tools_used:
            pattern = {
                "query_keywords": query.lower().split()[:5],
                "tools_sequence": tools_used,
                "success": all(r["result"].get("success", True) for r in tool_results)
            }
            patterns.append(pattern)
        
        if patterns:
            self.learning_data["patterns"].extend(patterns)
            self.learning_data["patterns"] = self.learning_data["patterns"][-100:]
            self._save_learning()
    
    async def auto_improve(self) -> Dict:
        """
        Автоматическое улучшение системы
        Анализирует код и предлагает/применяет улучшения
        """
        if not self.config.get("auto_improve", True):
            return {"status": "disabled"}
        
        improvement_prompt = """Проанализируй текущий код системы SEO Monster и предложи улучшения.

Сделай следующее:
1. Просмотри структуру проекта
2. Найди потенциальные проблемы или места для оптимизации
3. Предложи конкретные улучшения
4. Если улучшение безопасно — примени его

Фокусируйся на:
- Производительности
- Читаемости кода
- Обработке ошибок
- Новых полезных функциях"""
        
        result = await self.process_message(improvement_prompt)
        
        # Сохраняем предложенные улучшения
        if result.get("success"):
            improvement_record = {
                "timestamp": datetime.now().isoformat(),
                "analysis": result.get("response", ""),
                "changes_made": [r for r in result.get("tool_results", []) if r["tool"] == "write_file"]
            }
            
            improvements = []
            if IMPROVEMENTS_FILE.exists():
                try:
                    with open(IMPROVEMENTS_FILE, 'r') as f:
                        improvements = json.load(f)
                except:
                    pass
            
            improvements.append(improvement_record)
            improvements = improvements[-50:]
            
            with open(IMPROVEMENTS_FILE, 'w') as f:
                json.dump(improvements, f, indent=2, ensure_ascii=False)
        
        return result
    
    async def fix_error(self, error_message: str, context: str = "") -> Dict:
        """
        Автоматическое исправление ошибки
        """
        if not self.config.get("auto_fix_errors", True):
            return {"status": "disabled"}
        
        fix_prompt = f"""Произошла ошибка в системе. Исправь её.

Ошибка: {error_message}

Контекст: {context}

Действия:
1. Найди файл с ошибкой
2. Проанализируй причину
3. Исправь код
4. Протестируй исправление"""
        
        return await self.process_message(fix_prompt)
    
    async def create_module(self, description: str) -> Dict:
        """
        Создание нового модуля по описанию
        """
        create_prompt = f"""Создай новый модуль для системы SEO Monster.

Описание: {description}

Требования:
1. Следуй существующей архитектуре проекта
2. Создай сервис в backend/services/
3. Создай API роуты в backend/app/api/
4. Добавь роуты в main.py
5. Документируй код
6. Протестируй работоспособность"""
        
        return await self.process_message(create_prompt)
    
    def get_status(self) -> Dict:
        """Получение статуса агента"""
        return {
            "memory_size": {
                "conversations": len(self.memory.get("conversations", [])),
                "successful_solutions": len(self.memory.get("successful_solutions", [])),
                "failed_attempts": len(self.memory.get("failed_attempts", [])),
                "knowledge_items": len(self.memory.get("knowledge_base", {}))
            },
            "learning": {
                "patterns_learned": len(self.learning_data.get("patterns", [])),
                "error_solutions": len(self.learning_data.get("error_solutions", {}))
            },
            "code_changes": len(self.code_history),
            "config": self.config,
            "tools_available": list(self.tools.keys())
        }


# Singleton
_agent_instance = None

def get_ai_agent() -> AutonomousAIAgent:
    """Получение экземпляра AI-агента"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AutonomousAIAgent()
    return _agent_instance


# Алиас для совместимости с диагностикой
AIAgentCore = AutonomousAIAgent
