"""
SEO Monster - AI Code Generator
Модуль генерации и обновления кода AI-агентом

Возможности:
- Генерация новых модулей по описанию
- Обновление существующего кода
- Автоматическое исправление ошибок
- Рефакторинг и оптимизация
- Создание тестов
"""

import os
import sys
import json
import ast
import subprocess
import difflib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    os.system("pip3 install openai")
    from openai import OpenAI

# Пути
BASE_DIR = Path("/home/ubuntu/seo_monster")
BACKEND_DIR = BASE_DIR / "backend"
SERVICES_DIR = BACKEND_DIR / "services"
API_DIR = BACKEND_DIR / "app" / "api"
DATA_DIR = BACKEND_DIR / "data"
CODE_GEN_DIR = DATA_DIR / "code_generator"
CODE_GEN_DIR.mkdir(parents=True, exist_ok=True)

# Файлы
GENERATED_CODE_LOG = CODE_GEN_DIR / "generated_code.json"
CODE_TEMPLATES_FILE = CODE_GEN_DIR / "templates.json"
REFACTORING_LOG = CODE_GEN_DIR / "refactoring_log.json"


class AICodeGenerator:
    """
    AI-генератор кода для SEO Monster
    Создаёт, обновляет и оптимизирует код автоматически
    """
    
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"
        self.generated_log = self._load_log()
        self.templates = self._load_templates()
    
    def _load_log(self) -> List[Dict]:
        """Загрузка лога генерации"""
        if GENERATED_CODE_LOG.exists():
            try:
                with open(GENERATED_CODE_LOG, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_log(self):
        """Сохранение лога"""
        self.generated_log = self.generated_log[-200:]
        with open(GENERATED_CODE_LOG, 'w', encoding='utf-8') as f:
            json.dump(self.generated_log, f, indent=2, ensure_ascii=False)
    
    def _load_templates(self) -> Dict:
        """Загрузка шаблонов кода"""
        if CODE_TEMPLATES_FILE.exists():
            try:
                with open(CODE_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Базовые шаблоны
        return {
            "service": '''"""
{module_name} - {description}
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/{module_name_lower}")
DATA_DIR.mkdir(parents=True, exist_ok=True)


class {class_name}:
    """
    {description}
    """
    
    def __init__(self):
        self.data_file = DATA_DIR / "data.json"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {{"items": [], "settings": {{}}}}
    
    def _save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    # TODO: Добавить методы


# Singleton
_instance = None

def get_{instance_name}() -> {class_name}:
    global _instance
    if _instance is None:
        _instance = {class_name}()
    return _instance
''',
            "api_router": '''"""
{module_name} API Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.{service_file} import get_{instance_name}

router = APIRouter(prefix="/api/{route_prefix}", tags=["{tag}"])


# Pydantic Models
class CreateItemRequest(BaseModel):
    name: str
    # TODO: Добавить поля


# Endpoints
@router.get("/")
async def get_items():
    """Получение списка"""
    service = get_{instance_name}()
    return {{"items": service.data.get("items", [])}}


@router.post("/")
async def create_item(request: CreateItemRequest):
    """Создание элемента"""
    service = get_{instance_name}()
    # TODO: Реализовать
    return {{"status": "created"}}


@router.get("/{{item_id}}")
async def get_item(item_id: int):
    """Получение элемента"""
    service = get_{instance_name}()
    # TODO: Реализовать
    return {{"item": None}}


@router.delete("/{{item_id}}")
async def delete_item(item_id: int):
    """Удаление элемента"""
    service = get_{instance_name}()
    # TODO: Реализовать
    return {{"status": "deleted"}}
'''
        }
    
    def _save_templates(self):
        """Сохранение шаблонов"""
        with open(CODE_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=2, ensure_ascii=False)
    
    # ═══════════════════════════════════════════════════════════════
    # ГЕНЕРАЦИЯ КОДА
    # ═══════════════════════════════════════════════════════════════
    
    def generate_module(self, name: str, description: str, features: List[str] = None) -> Dict:
        """
        Генерация нового модуля по описанию
        Создаёт сервис и API роуты
        """
        result = {
            "name": name,
            "description": description,
            "files_created": [],
            "success": False,
            "errors": []
        }
        
        # Нормализуем имена
        module_name = name.replace(" ", "_").lower()
        class_name = "".join(word.capitalize() for word in name.split())
        instance_name = module_name
        
        # Генерируем сервис через LLM
        service_code = self._generate_service_code(name, description, features)
        if service_code:
            service_path = SERVICES_DIR / f"{module_name}_service.py"
            self._write_file(service_path, service_code)
            result["files_created"].append(str(service_path))
        else:
            result["errors"].append("Не удалось сгенерировать сервис")
        
        # Генерируем API роуты
        api_code = self._generate_api_code(name, module_name, description)
        if api_code:
            api_path = API_DIR / f"{module_name}_routes.py"
            self._write_file(api_path, api_code)
            result["files_created"].append(str(api_path))
        else:
            result["errors"].append("Не удалось сгенерировать API")
        
        # Обновляем main.py
        if result["files_created"]:
            main_updated = self._update_main_py(module_name)
            if main_updated:
                result["files_created"].append("main.py (updated)")
        
        result["success"] = len(result["errors"]) == 0
        
        # Логируем
        self._log_generation(result)
        
        return result
    
    def _generate_service_code(self, name: str, description: str, features: List[str] = None) -> Optional[str]:
        """Генерация кода сервиса через LLM"""
        features_text = "\n".join(f"- {f}" for f in (features or []))
        
        prompt = f"""Создай Python сервис для системы SEO Monster.

Название: {name}
Описание: {description}
Функции:
{features_text if features_text else "- Базовый CRUD"}

Требования:
1. Следуй архитектуре проекта (см. примеры в /backend/services/)
2. Используй JSON для хранения данных
3. Создай singleton паттерн
4. Добавь docstrings
5. Реализуй все указанные функции
6. Добавь обработку ошибок

Верни ТОЛЬКО код Python без markdown разметки."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты — эксперт Python разработчик. Генерируй чистый, рабочий код."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            code = response.choices[0].message.content
            
            # Очищаем от markdown
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            # Валидируем синтаксис
            if self._validate_python(code):
                return code.strip()
            
        except Exception as e:
            print(f"Error generating service: {e}")
        
        return None
    
    def _generate_api_code(self, name: str, module_name: str, description: str) -> Optional[str]:
        """Генерация кода API роутов"""
        prompt = f"""Создай FastAPI роуты для модуля {name}.

Модуль: {module_name}
Описание: {description}

Требования:
1. Используй APIRouter с prefix="/api/{module_name}"
2. Добавь Pydantic модели для запросов
3. Импортируй сервис из services.{module_name}_service
4. Создай CRUD эндпоинты
5. Добавь документацию к эндпоинтам

Верни ТОЛЬКО код Python без markdown разметки."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты — эксперт FastAPI разработчик. Генерируй чистый, рабочий код."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            code = response.choices[0].message.content
            
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            if self._validate_python(code):
                return code.strip()
            
        except Exception as e:
            print(f"Error generating API: {e}")
        
        return None
    
    def _update_main_py(self, module_name: str) -> bool:
        """Обновление main.py для добавления нового роутера"""
        main_path = BACKEND_DIR / "main.py"
        
        try:
            with open(main_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем, не добавлен ли уже
            if f"{module_name}_routes" in content:
                return True
            
            # Добавляем импорт
            import_line = f"from app.api.{module_name}_routes import router as {module_name}_router"
            
            # Находим последний импорт роутера
            lines = content.split('\n')
            last_import_idx = 0
            for i, line in enumerate(lines):
                if "from app.api." in line and "import router" in line:
                    last_import_idx = i
            
            if last_import_idx > 0:
                lines.insert(last_import_idx + 1, import_line)
            
            # Добавляем include_router
            include_line = f"app.include_router({module_name}_router)"
            
            for i, line in enumerate(lines):
                if "app.include_router(" in line:
                    last_include_idx = i
            
            lines.insert(last_include_idx + 1, include_line)
            
            # Сохраняем
            new_content = '\n'.join(lines)
            
            # Бэкап
            backup_path = CODE_GEN_DIR / f"main.py.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"Error updating main.py: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════════
    # ОБНОВЛЕНИЕ КОДА
    # ═══════════════════════════════════════════════════════════════
    
    def update_code(self, file_path: str, instruction: str) -> Dict:
        """
        Обновление существующего кода по инструкции
        """
        result = {
            "file": file_path,
            "instruction": instruction,
            "success": False,
            "changes": [],
            "error": None
        }
        
        path = Path(file_path)
        if not path.exists():
            result["error"] = f"Файл не найден: {file_path}"
            return result
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Генерируем обновлённый код
            updated_code = self._generate_code_update(original_code, instruction)
            
            if updated_code and updated_code != original_code:
                # Валидируем
                if self._validate_python(updated_code):
                    # Создаём бэкап
                    backup_path = CODE_GEN_DIR / f"{path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_code)
                    
                    # Записываем новый код
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(updated_code)
                    
                    # Вычисляем diff
                    diff = list(difflib.unified_diff(
                        original_code.splitlines(),
                        updated_code.splitlines(),
                        lineterm=''
                    ))
                    
                    result["success"] = True
                    result["changes"] = diff[:50]  # Ограничиваем
                    result["backup"] = str(backup_path)
                else:
                    result["error"] = "Сгенерированный код не прошёл валидацию"
            else:
                result["error"] = "Не удалось сгенерировать обновление"
            
        except Exception as e:
            result["error"] = str(e)
        
        self._log_generation(result)
        return result
    
    def _generate_code_update(self, original_code: str, instruction: str) -> Optional[str]:
        """Генерация обновлённого кода"""
        prompt = f"""Обнови следующий Python код согласно инструкции.

ИНСТРУКЦИЯ: {instruction}

ТЕКУЩИЙ КОД:
```python
{original_code}
```

Требования:
1. Сохрани существующую функциональность
2. Добавь/измени только то, что указано в инструкции
3. Сохрани стиль кода
4. Добавь комментарии к изменениям

Верни ТОЛЬКО обновлённый код Python без markdown разметки."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты — эксперт Python разработчик. Обновляй код аккуратно и точно."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            code = response.choices[0].message.content
            
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            return code.strip()
            
        except Exception as e:
            print(f"Error generating update: {e}")
        
        return None
    
    # ═══════════════════════════════════════════════════════════════
    # ИСПРАВЛЕНИЕ ОШИБОК
    # ═══════════════════════════════════════════════════════════════
    
    def fix_error(self, file_path: str, error_message: str, error_traceback: str = "") -> Dict:
        """
        Автоматическое исправление ошибки в коде
        """
        result = {
            "file": file_path,
            "error": error_message,
            "success": False,
            "fix_applied": None
        }
        
        path = Path(file_path)
        if not path.exists():
            result["fix_applied"] = "Файл не найден"
            return result
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Генерируем исправление
            fixed_code = self._generate_error_fix(original_code, error_message, error_traceback)
            
            if fixed_code and self._validate_python(fixed_code):
                # Бэкап
                backup_path = CODE_GEN_DIR / f"{path.name}.error_fix.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_code)
                
                # Применяем исправление
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                
                result["success"] = True
                result["fix_applied"] = "Исправление применено"
                result["backup"] = str(backup_path)
            else:
                result["fix_applied"] = "Не удалось сгенерировать исправление"
            
        except Exception as e:
            result["fix_applied"] = f"Ошибка: {str(e)}"
        
        self._log_generation(result)
        return result
    
    def _generate_error_fix(self, code: str, error: str, traceback: str) -> Optional[str]:
        """Генерация исправления ошибки"""
        prompt = f"""Исправь ошибку в Python коде.

ОШИБКА: {error}

TRACEBACK:
{traceback[:1000] if traceback else "Не предоставлен"}

КОД:
```python
{code}
```

Требования:
1. Исправь только ошибку
2. Не меняй логику без необходимости
3. Добавь комментарий к исправлению

Верни ТОЛЬКО исправленный код Python без markdown разметки."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты — эксперт по отладке Python. Исправляй ошибки точно и минимально."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            code = response.choices[0].message.content
            
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            return code.strip()
            
        except Exception as e:
            print(f"Error generating fix: {e}")
        
        return None
    
    # ═══════════════════════════════════════════════════════════════
    # РЕФАКТОРИНГ
    # ═══════════════════════════════════════════════════════════════
    
    def refactor_code(self, file_path: str, refactor_type: str = "optimize") -> Dict:
        """
        Рефакторинг кода
        Типы: optimize, clean, document, modernize
        """
        result = {
            "file": file_path,
            "type": refactor_type,
            "success": False,
            "improvements": []
        }
        
        path = Path(file_path)
        if not path.exists():
            result["error"] = "Файл не найден"
            return result
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            refactored = self._generate_refactoring(original_code, refactor_type)
            
            if refactored and self._validate_python(refactored):
                # Бэкап
                backup_path = CODE_GEN_DIR / f"{path.name}.refactor.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_code)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(refactored)
                
                result["success"] = True
                result["backup"] = str(backup_path)
            
        except Exception as e:
            result["error"] = str(e)
        
        # Логируем
        refactor_log = []
        if REFACTORING_LOG.exists():
            try:
                with open(REFACTORING_LOG, 'r') as f:
                    refactor_log = json.load(f)
            except:
                pass
        
        refactor_log.append({
            "timestamp": datetime.now().isoformat(),
            **result
        })
        refactor_log = refactor_log[-100:]
        
        with open(REFACTORING_LOG, 'w') as f:
            json.dump(refactor_log, f, indent=2, ensure_ascii=False)
        
        return result
    
    def _generate_refactoring(self, code: str, refactor_type: str) -> Optional[str]:
        """Генерация рефакторинга"""
        type_instructions = {
            "optimize": "Оптимизируй производительность: убери лишние операции, улучши алгоритмы",
            "clean": "Очисти код: убери дублирование, улучши именование, упрости логику",
            "document": "Добавь документацию: docstrings, комментарии, type hints",
            "modernize": "Модернизируй: используй современные Python конструкции, async/await где уместно"
        }
        
        instruction = type_instructions.get(refactor_type, type_instructions["clean"])
        
        prompt = f"""Выполни рефакторинг Python кода.

ЗАДАЧА: {instruction}

КОД:
```python
{code}
```

Требования:
1. Сохрани функциональность
2. Улучши качество кода
3. Добавь комментарии к изменениям

Верни ТОЛЬКО рефакторированный код Python без markdown разметки."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты — эксперт по рефакторингу Python кода."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            code = response.choices[0].message.content
            
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            return code.strip()
            
        except Exception as e:
            print(f"Error generating refactoring: {e}")
        
        return None
    
    # ═══════════════════════════════════════════════════════════════
    # УТИЛИТЫ
    # ═══════════════════════════════════════════════════════════════
    
    def _validate_python(self, code: str) -> bool:
        """Валидация синтаксиса Python"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def _write_file(self, path: Path, content: str):
        """Запись файла с созданием директорий"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _log_generation(self, result: Dict):
        """Логирование генерации"""
        self.generated_log.append({
            "timestamp": datetime.now().isoformat(),
            **result
        })
        self._save_log()
    
    def get_generation_stats(self) -> Dict:
        """Получение статистики генерации"""
        total = len(self.generated_log)
        successful = len([l for l in self.generated_log if l.get("success")])
        
        return {
            "total_generations": total,
            "successful": successful,
            "success_rate": round(successful / max(total, 1) * 100, 2),
            "recent": self.generated_log[-5:]
        }


# Singleton
_code_generator = None

def get_code_generator() -> AICodeGenerator:
    """Получение экземпляра генератора кода"""
    global _code_generator
    if _code_generator is None:
        _code_generator = AICodeGenerator()
    return _code_generator
