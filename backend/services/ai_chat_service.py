"""
SEO Monster - AI Chat Service
Чат-интерфейс для управления системой через естественный язык
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from openai import OpenAI
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    role: MessageRole
    content: str
    timestamp: str
    metadata: Optional[Dict] = None


@dataclass
class ChatSession:
    id: str
    messages: List[ChatMessage]
    created_at: str
    last_activity: str
    context: Dict  # Контекст для понимания намерений


class AIChatService:
    """
    AI Chat Service для управления SEO Monster
    
    Возможности:
    - Понимание естественного языка
    - Выполнение команд через чат
    - Контекстные диалоги
    - Отчеты и статистика
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "data/chat")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы данных
        self.sessions_file = self.data_dir / "sessions.json"
        self.history_file = self.data_dir / "history.json"
        
        # Загружаем данные
        self.sessions: Dict[str, ChatSession] = self._load_sessions()
        self.history: List[Dict] = self._load_json(self.history_file, [])
        
        # OpenAI клиент
        self.ai_client = None
        self._init_ai_client()
        
        # Системный промпт
        self.system_prompt = self._build_system_prompt()
        
        # Доступные команды
        self.commands = self._build_commands()
    
    def _init_ai_client(self):
        """Инициализация AI клиента"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            self.ai_client = OpenAI()
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Загрузка JSON файла"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, path: Path, data: Any):
        """Сохранение JSON файла"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _load_sessions(self) -> Dict[str, ChatSession]:
        """Загрузка сессий"""
        data = self._load_json(self.sessions_file, {})
        sessions = {}
        for sid, sdata in data.items():
            messages = [ChatMessage(**m) for m in sdata.get('messages', [])]
            sessions[sid] = ChatSession(
                id=sdata['id'],
                messages=messages,
                created_at=sdata['created_at'],
                last_activity=sdata['last_activity'],
                context=sdata.get('context', {})
            )
        return sessions
    
    def _save_sessions(self):
        """Сохранение сессий"""
        data = {}
        for sid, session in self.sessions.items():
            data[sid] = {
                'id': session.id,
                'messages': [asdict(m) for m in session.messages],
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'context': session.context
            }
        self._save_json(self.sessions_file, data)
    
    def _build_system_prompt(self) -> str:
        """Построение системного промпта"""
        return """Ты - AI-ассистент системы SEO Monster. Твоя задача - помогать пользователю управлять SEO-продвижением через естественный диалог.

ВОЗМОЖНОСТИ СИСТЕМЫ:
1. Автопилот - автоматическое продвижение сайтов
2. Управление аккаунтами - импорт, cookies, ротация
3. Индексация - отправка URL в поисковики
4. Генерация контента - создание SEO-статей
5. Мониторинг позиций - отслеживание в Google/Bing

ДОСТУПНЫЕ КОМАНДЫ (используй JSON формат для выполнения):
- {"action": "create_campaign", "domain": "example.com"} - создать кампанию
- {"action": "start_campaign", "campaign_id": "..."} - запустить автопилот
- {"action": "pause_campaign", "campaign_id": "..."} - приостановить
- {"action": "get_stats"} - получить статистику
- {"action": "import_accounts", "data": "..."} - импортировать аккаунты
- {"action": "generate_content", "keyword": "...", "language": "ru"} - сгенерировать контент
- {"action": "index_url", "url": "..."} - отправить на индексацию
- {"action": "check_positions", "domain": "...", "keywords": [...]} - проверить позиции

ПРАВИЛА:
1. Отвечай на русском языке
2. Будь кратким и информативным
3. Если нужно выполнить действие - верни JSON команду в блоке ```json
4. Если пользователь спрашивает - отвечай текстом
5. Предлагай следующие шаги
6. При ошибках объясняй причину и решение

КОНТЕКСТ ТЕКУЩЕЙ СЕССИИ:
{context}

Отвечай дружелюбно и профессионально."""
    
    def _build_commands(self) -> Dict[str, callable]:
        """Построение словаря команд"""
        return {
            "create_campaign": self._cmd_create_campaign,
            "start_campaign": self._cmd_start_campaign,
            "pause_campaign": self._cmd_pause_campaign,
            "resume_campaign": self._cmd_resume_campaign,
            "get_stats": self._cmd_get_stats,
            "get_campaigns": self._cmd_get_campaigns,
            "import_accounts": self._cmd_import_accounts,
            "generate_content": self._cmd_generate_content,
            "index_url": self._cmd_index_url,
            "check_positions": self._cmd_check_positions,
            "get_account_stats": self._cmd_get_account_stats,
            "help": self._cmd_help
        }
    
    def create_session(self, session_id: str = None) -> str:
        """Создание новой сессии чата"""
        if not session_id:
            session_id = f"chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        session = ChatSession(
            id=session_id,
            messages=[],
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            context={}
        )
        
        self.sessions[session_id] = session
        self._save_sessions()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Получение сессии"""
        return self.sessions.get(session_id)
    
    async def chat(self, session_id: str, user_message: str) -> Dict:
        """
        Обработка сообщения пользователя
        
        Returns:
            {
                "response": str,
                "action_result": Optional[Dict],
                "suggestions": List[str]
            }
        """
        # Получаем или создаем сессию
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        session = self.sessions[session_id]
        
        # Добавляем сообщение пользователя
        user_msg = ChatMessage(
            role=MessageRole.USER,
            content=user_message,
            timestamp=datetime.now().isoformat()
        )
        session.messages.append(user_msg)
        
        # Получаем ответ от AI
        response_text, action_data = await self._get_ai_response(session, user_message)
        
        # Выполняем действие если есть
        action_result = None
        if action_data:
            action_result = await self._execute_action(action_data)
            
            # Добавляем результат в ответ
            if action_result.get("success"):
                response_text += f"\n\n✅ Выполнено: {action_result.get('message', '')}"
            else:
                response_text += f"\n\n❌ Ошибка: {action_result.get('error', '')}"
        
        # Добавляем ответ ассистента
        assistant_msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=response_text,
            timestamp=datetime.now().isoformat(),
            metadata={"action": action_data, "result": action_result}
        )
        session.messages.append(assistant_msg)
        
        # Обновляем сессию
        session.last_activity = datetime.now().isoformat()
        self._save_sessions()
        
        # Генерируем предложения
        suggestions = self._generate_suggestions(session, action_result)
        
        return {
            "response": response_text,
            "action_result": action_result,
            "suggestions": suggestions
        }
    
    async def _get_ai_response(self, session: ChatSession, user_message: str) -> Tuple[str, Optional[Dict]]:
        """Получение ответа от AI"""
        
        # Если нет AI клиента - используем rule-based
        if not self.ai_client:
            return self._rule_based_response(user_message)
        
        # Строим контекст
        context_str = json.dumps(session.context, ensure_ascii=False) if session.context else "{}"
        system_prompt = self.system_prompt.replace("{context}", context_str)
        
        # Строим историю сообщений
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем последние 10 сообщений
        for msg in session.messages[-10:]:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            
            # Извлекаем JSON команду если есть
            action_data = self._extract_action(response_text)
            
            # Убираем JSON блок из текста ответа
            if action_data:
                response_text = re.sub(r'```json\s*\{[^}]+\}\s*```', '', response_text).strip()
            
            return response_text, action_data
            
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return self._rule_based_response(user_message)
    
    def _rule_based_response(self, message: str) -> Tuple[str, Optional[Dict]]:
        """Rule-based ответы без AI"""
        
        message_lower = message.lower()
        
        # Приветствие
        if any(word in message_lower for word in ['привет', 'здравствуй', 'hi', 'hello']):
            return "Привет! Я AI-ассистент SEO Monster. Чем могу помочь?\n\nВы можете:\n- Создать кампанию продвижения\n- Импортировать аккаунты\n- Проверить статистику\n- Сгенерировать контент", None
        
        # Статистика
        if any(word in message_lower for word in ['статистик', 'stats', 'отчет']):
            return "Получаю статистику системы...", {"action": "get_stats"}
        
        # Создание кампании
        if 'создай' in message_lower and 'кампани' in message_lower:
            # Пытаемся извлечь домен
            domain_match = re.search(r'(?:для|домен|сайт)\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', message)
            if domain_match:
                domain = domain_match.group(1)
                return f"Создаю кампанию для {domain}...", {"action": "create_campaign", "domain": domain}
            return "Укажите домен для создания кампании. Например: 'Создай кампанию для example.com'", None
        
        # Запуск кампании
        if 'запусти' in message_lower or 'старт' in message_lower:
            return "Для запуска укажите ID кампании. Используйте 'покажи кампании' чтобы увидеть список.", {"action": "get_campaigns"}
        
        # Список кампаний
        if 'кампани' in message_lower and ('покаж' in message_lower or 'список' in message_lower):
            return "Получаю список кампаний...", {"action": "get_campaigns"}
        
        # Импорт аккаунтов
        if 'импорт' in message_lower and 'аккаунт' in message_lower:
            return "Для импорта аккаунтов отправьте данные в формате:\nplatform:username:password\n\nИли загрузите файл через интерфейс.", None
        
        # Помощь
        if any(word in message_lower for word in ['помощь', 'help', 'что умеешь', 'команды']):
            return self._cmd_help(), None
        
        # Генерация контента
        if 'генер' in message_lower and 'контент' in message_lower:
            keyword_match = re.search(r'(?:ключ|keyword|тема)\s+["\']?([^"\']+)["\']?', message)
            if keyword_match:
                keyword = keyword_match.group(1)
                return f"Генерирую контент для '{keyword}'...", {"action": "generate_content", "keyword": keyword}
            return "Укажите ключевое слово для генерации. Например: 'Сгенерируй контент на тему SEO оптимизация'", None
        
        # Индексация
        if 'индекс' in message_lower:
            url_match = re.search(r'(https?://[^\s]+)', message)
            if url_match:
                url = url_match.group(1)
                return f"Отправляю на индексацию {url}...", {"action": "index_url", "url": url}
            return "Укажите URL для индексации. Например: 'Проиндексируй https://example.com/page'", None
        
        # По умолчанию
        return "Я понял ваш запрос. Могу помочь с:\n\n1. **Кампании** - создание и управление продвижением\n2. **Аккаунты** - импорт и управление\n3. **Контент** - генерация SEO-статей\n4. **Индексация** - отправка в поисковики\n\nЧто именно вас интересует?", None
    
    def _extract_action(self, text: str) -> Optional[Dict]:
        """Извлечение JSON команды из текста"""
        
        # Ищем JSON в блоке кода
        json_match = re.search(r'```json\s*(\{[^}]+\})\s*```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Ищем просто JSON
        json_match = re.search(r'\{["\']action["\']\s*:\s*["\'][^"\']+["\'][^}]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return None
    
    async def _execute_action(self, action_data: Dict) -> Dict:
        """Выполнение действия"""
        
        action = action_data.get("action")
        
        if action not in self.commands:
            return {"success": False, "error": f"Неизвестное действие: {action}"}
        
        try:
            result = await self.commands[action](action_data)
            return {"success": True, **result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_suggestions(self, session: ChatSession, action_result: Optional[Dict]) -> List[str]:
        """Генерация предложений следующих действий"""
        
        suggestions = []
        
        if action_result:
            action = action_result.get("action")
            
            if action == "create_campaign":
                suggestions = [
                    "Запустить кампанию",
                    "Настроить параметры",
                    "Показать все кампании"
                ]
            elif action == "get_stats":
                suggestions = [
                    "Создать новую кампанию",
                    "Показать кампании",
                    "Импортировать аккаунты"
                ]
            elif action == "get_campaigns":
                suggestions = [
                    "Запустить кампанию",
                    "Создать новую кампанию",
                    "Показать статистику"
                ]
        else:
            suggestions = [
                "Показать статистику",
                "Создать кампанию",
                "Помощь"
            ]
        
        return suggestions
    
    # ==================== КОМАНДЫ ====================
    
    async def _cmd_create_campaign(self, data: Dict) -> Dict:
        """Создание кампании"""
        from services.autopilot_engine import get_autopilot_engine
        
        engine = get_autopilot_engine()
        domain = data.get("domain")
        
        if not domain:
            return {"message": "Домен не указан"}
        
        campaign = engine.create_campaign(domain, data.get("settings"))
        
        return {
            "message": f"Кампания создана для {domain}",
            "campaign_id": campaign.id,
            "action": "create_campaign"
        }
    
    async def _cmd_start_campaign(self, data: Dict) -> Dict:
        """Запуск кампании"""
        from services.autopilot_engine import get_autopilot_engine
        
        engine = get_autopilot_engine()
        campaign_id = data.get("campaign_id")
        
        if not campaign_id:
            return {"message": "ID кампании не указан"}
        
        await engine.start_campaign(campaign_id)
        
        return {
            "message": f"Кампания {campaign_id} запущена",
            "action": "start_campaign"
        }
    
    async def _cmd_pause_campaign(self, data: Dict) -> Dict:
        """Приостановка кампании"""
        from services.autopilot_engine import get_autopilot_engine
        
        engine = get_autopilot_engine()
        campaign_id = data.get("campaign_id")
        
        engine.pause_campaign(campaign_id)
        
        return {
            "message": f"Кампания {campaign_id} приостановлена",
            "action": "pause_campaign"
        }
    
    async def _cmd_resume_campaign(self, data: Dict) -> Dict:
        """Возобновление кампании"""
        from services.autopilot_engine import get_autopilot_engine
        
        engine = get_autopilot_engine()
        campaign_id = data.get("campaign_id")
        
        await engine.resume_campaign(campaign_id)
        
        return {
            "message": f"Кампания {campaign_id} возобновлена",
            "action": "resume_campaign"
        }
    
    async def _cmd_get_stats(self, data: Dict) -> Dict:
        """Получение статистики"""
        from services.autopilot_engine import get_autopilot_engine
        from services.account_manager import get_account_manager
        
        autopilot = get_autopilot_engine()
        accounts = get_account_manager()
        
        autopilot_stats = autopilot.get_stats()
        account_stats = accounts.get_stats()
        
        return {
            "message": "Статистика системы",
            "autopilot": autopilot_stats,
            "accounts": account_stats,
            "action": "get_stats"
        }
    
    async def _cmd_get_campaigns(self, data: Dict) -> Dict:
        """Получение списка кампаний"""
        from services.autopilot_engine import get_autopilot_engine
        
        engine = get_autopilot_engine()
        campaigns = engine.get_all_campaigns()
        
        campaigns_list = [
            {
                "id": c.id,
                "domain": c.domain,
                "status": c.status.value if hasattr(c.status, 'value') else c.status,
                "content_generated": c.stats.get("content_generated", 0)
            }
            for c in campaigns
        ]
        
        return {
            "message": f"Найдено {len(campaigns_list)} кампаний",
            "campaigns": campaigns_list,
            "action": "get_campaigns"
        }
    
    async def _cmd_import_accounts(self, data: Dict) -> Dict:
        """Импорт аккаунтов"""
        from services.account_manager import get_account_manager
        
        manager = get_account_manager()
        content = data.get("data", "")
        
        if not content:
            return {"message": "Данные для импорта не указаны"}
        
        imported, skipped, errors = manager.import_from_text(content)
        
        return {
            "message": f"Импортировано {imported} аккаунтов, пропущено {skipped}",
            "imported": imported,
            "skipped": skipped,
            "action": "import_accounts"
        }
    
    async def _cmd_generate_content(self, data: Dict) -> Dict:
        """Генерация контента"""
        
        keyword = data.get("keyword")
        language = data.get("language", "ru")
        
        if not keyword:
            return {"message": "Ключевое слово не указано"}
        
        if not self.ai_client:
            return {"message": "AI клиент не настроен. Добавьте OPENAI_API_KEY."}
        
        prompt = f"""Создай SEO-оптимизированную статью.
Ключевое слово: {keyword}
Язык: {language}
Требования: 500-800 слов, уникальный контент, естественное использование ключевого слова.

Верни JSON: {{"title": "...", "content": "...", "meta_description": "..."}}"""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "message": f"Контент сгенерирован: {result.get('title', '')}",
                "content": result,
                "action": "generate_content"
            }
        except Exception as e:
            return {"message": f"Ошибка генерации: {str(e)}"}
    
    async def _cmd_index_url(self, data: Dict) -> Dict:
        """Индексация URL"""
        from services.indexing_service import get_indexing_service
        
        service = get_indexing_service()
        url = data.get("url")
        
        if not url:
            return {"message": "URL не указан"}
        
        result = await service.ping_google(url)
        
        return {
            "message": f"URL отправлен на индексацию: {result.status.value}",
            "url": url,
            "status": result.status.value,
            "action": "index_url"
        }
    
    async def _cmd_check_positions(self, data: Dict) -> Dict:
        """Проверка позиций"""
        return {
            "message": "Функция проверки позиций в разработке",
            "action": "check_positions"
        }
    
    async def _cmd_get_account_stats(self, data: Dict) -> Dict:
        """Статистика аккаунтов"""
        from services.account_manager import get_account_manager
        
        manager = get_account_manager()
        stats = manager.get_stats()
        
        return {
            "message": "Статистика аккаунтов",
            "stats": stats,
            "action": "get_account_stats"
        }
    
    def _cmd_help(self, data: Dict = None) -> str:
        """Справка по командам"""
        return """🤖 **SEO Monster - Справка**

**Кампании продвижения:**
- "Создай кампанию для example.com" - создание новой кампании
- "Запусти кампанию" - запуск автопилота
- "Покажи кампании" - список всех кампаний
- "Приостанови кампанию" - пауза

**Аккаунты:**
- "Покажи статистику аккаунтов" - статистика
- "Импортируй аккаунты" - импорт из текста

**Контент:**
- "Сгенерируй контент на тему X" - создание статьи

**Индексация:**
- "Проиндексируй https://..." - отправка в Google

**Общее:**
- "Покажи статистику" - общая статистика системы
- "Помощь" - эта справка

💡 Просто пишите что хотите сделать - я пойму!"""
    
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Получение истории чата"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return [
            {
                "role": m.role.value,
                "content": m.content,
                "timestamp": m.timestamp
            }
            for m in session.messages[-limit:]
        ]
    
    def clear_session(self, session_id: str) -> bool:
        """Очистка сессии"""
        if session_id in self.sessions:
            self.sessions[session_id].messages = []
            self.sessions[session_id].context = {}
            self._save_sessions()
            return True
        return False


# Глобальный экземпляр
_chat_service = None

def get_chat_service() -> AIChatService:
    """Получение глобального экземпляра"""
    global _chat_service
    if _chat_service is None:
        _chat_service = AIChatService()
    return _chat_service
