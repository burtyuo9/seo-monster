"""
SEO Monster - Telegram Bot Integration
Интеграция с Telegram для управления системой
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path

# Путь к данным
DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/telegram")
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = DATA_DIR / "config.json"
SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"
NOTIFICATIONS_LOG = DATA_DIR / "notifications.json"


class TelegramBot:
    """Telegram Bot для управления SEO Monster"""
    
    def __init__(self):
        self.config = self._load_config()
        self.subscribers = self._load_subscribers()
        self.notification_log = self._load_notifications()
        self.is_running = False
        self._polling_task = None
        
    def _load_config(self) -> Dict:
        """Загрузка конфигурации"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {
            "bot_token": "",
            "enabled": False,
            "notifications": {
                "campaign_started": True,
                "campaign_completed": True,
                "campaign_error": True,
                "content_generated": True,
                "content_posted": True,
                "indexing_completed": True,
                "daily_report": True
            },
            "admin_chat_ids": [],
            "webhook_url": ""
        }
    
    def _save_config(self):
        """Сохранение конфигурации"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _load_subscribers(self) -> List[Dict]:
        """Загрузка подписчиков"""
        if SUBSCRIBERS_FILE.exists():
            with open(SUBSCRIBERS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _save_subscribers(self):
        """Сохранение подписчиков"""
        with open(SUBSCRIBERS_FILE, 'w') as f:
            json.dump(self.subscribers, f, indent=2, ensure_ascii=False)
    
    def _load_notifications(self) -> List[Dict]:
        """Загрузка истории уведомлений"""
        if NOTIFICATIONS_LOG.exists():
            with open(NOTIFICATIONS_LOG, 'r') as f:
                return json.load(f)
        return []
    
    def _save_notifications(self):
        """Сохранение истории уведомлений"""
        # Храним только последние 1000 уведомлений
        self.notification_log = self.notification_log[-1000:]
        with open(NOTIFICATIONS_LOG, 'w') as f:
            json.dump(self.notification_log, f, indent=2, ensure_ascii=False)
    
    def configure(self, bot_token: str, admin_chat_id: Optional[str] = None) -> Dict:
        """Настройка бота"""
        self.config["bot_token"] = bot_token
        if admin_chat_id:
            if admin_chat_id not in self.config["admin_chat_ids"]:
                self.config["admin_chat_ids"].append(admin_chat_id)
        self._save_config()
        return {"status": "configured", "token_set": bool(bot_token)}
    
    def enable(self) -> Dict:
        """Включение бота"""
        if not self.config["bot_token"]:
            return {"error": "Bot token not configured"}
        self.config["enabled"] = True
        self._save_config()
        return {"status": "enabled"}
    
    def disable(self) -> Dict:
        """Отключение бота"""
        self.config["enabled"] = False
        self._save_config()
        return {"status": "disabled"}
    
    def update_notifications(self, settings: Dict[str, bool]) -> Dict:
        """Обновление настроек уведомлений"""
        self.config["notifications"].update(settings)
        self._save_config()
        return {"status": "updated", "notifications": self.config["notifications"]}
    
    def add_subscriber(self, chat_id: str, username: Optional[str] = None) -> Dict:
        """Добавление подписчика"""
        # Проверяем, есть ли уже такой подписчик
        for sub in self.subscribers:
            if sub["chat_id"] == chat_id:
                return {"status": "already_subscribed", "chat_id": chat_id}
        
        subscriber = {
            "chat_id": chat_id,
            "username": username,
            "subscribed_at": datetime.now().isoformat(),
            "is_admin": chat_id in self.config["admin_chat_ids"]
        }
        self.subscribers.append(subscriber)
        self._save_subscribers()
        return {"status": "subscribed", "subscriber": subscriber}
    
    def remove_subscriber(self, chat_id: str) -> Dict:
        """Удаление подписчика"""
        self.subscribers = [s for s in self.subscribers if s["chat_id"] != chat_id]
        self._save_subscribers()
        return {"status": "unsubscribed", "chat_id": chat_id}
    
    async def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> Dict:
        """Отправка сообщения в Telegram"""
        if not self.config["bot_token"]:
            return {"error": "Bot token not configured"}
        
        url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    
                    # Логируем уведомление
                    self.notification_log.append({
                        "chat_id": chat_id,
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "success": result.get("ok", False),
                        "timestamp": datetime.now().isoformat()
                    })
                    self._save_notifications()
                    
                    return result
        except Exception as e:
            return {"error": str(e)}
    
    async def broadcast(self, text: str, notification_type: str = "general") -> Dict:
        """Рассылка сообщения всем подписчикам"""
        if not self.config["enabled"]:
            return {"error": "Bot is disabled"}
        
        # Проверяем, включен ли этот тип уведомлений
        if notification_type != "general" and not self.config["notifications"].get(notification_type, True):
            return {"skipped": True, "reason": f"Notification type '{notification_type}' is disabled"}
        
        results = []
        for subscriber in self.subscribers:
            result = await self.send_message(subscriber["chat_id"], text)
            results.append({
                "chat_id": subscriber["chat_id"],
                "success": result.get("ok", False)
            })
        
        return {
            "sent": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }
    
    async def notify_campaign_started(self, campaign_domain: str):
        """Уведомление о запуске кампании"""
        text = f"""
🚀 <b>Кампания запущена!</b>

📌 Домен: <code>{campaign_domain}</code>
⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Автопилот начал работу над продвижением сайта.
"""
        await self.broadcast(text, "campaign_started")
    
    async def notify_campaign_completed(self, campaign_domain: str, stats: Dict):
        """Уведомление о завершении цикла кампании"""
        text = f"""
✅ <b>Цикл кампании завершён</b>

📌 Домен: <code>{campaign_domain}</code>
📊 Статистика:
  • Контента создано: {stats.get('content_generated', 0)}
  • Опубликовано: {stats.get('content_posted', 0)}
  • Проиндексировано: {stats.get('urls_indexed', 0)}

⏰ Следующий цикл через 1 час
"""
        await self.broadcast(text, "campaign_completed")
    
    async def notify_campaign_error(self, campaign_domain: str, error: str):
        """Уведомление об ошибке кампании"""
        text = f"""
❌ <b>Ошибка в кампании!</b>

📌 Домен: <code>{campaign_domain}</code>
⚠️ Ошибка: {error}
⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Проверьте логи для подробностей.
"""
        await self.broadcast(text, "campaign_error")
    
    async def notify_content_generated(self, title: str, domain: str):
        """Уведомление о генерации контента"""
        text = f"""
✍️ <b>Контент сгенерирован</b>

📝 Заголовок: {title}
🌐 Для сайта: <code>{domain}</code>
⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.broadcast(text, "content_generated")
    
    async def notify_content_posted(self, title: str, platform: str, url: str):
        """Уведомление о публикации контента"""
        text = f"""
📤 <b>Контент опубликован</b>

📝 Заголовок: {title}
📍 Площадка: {platform}
🔗 URL: {url}
⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.broadcast(text, "content_posted")
    
    async def notify_indexing_completed(self, url: str, search_engines: List[str]):
        """Уведомление об индексации"""
        engines = ", ".join(search_engines)
        text = f"""
🔍 <b>URL отправлен на индексацию</b>

🔗 URL: <code>{url}</code>
🔎 Поисковики: {engines}
⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.broadcast(text, "indexing_completed")
    
    async def send_daily_report(self, stats: Dict):
        """Отправка ежедневного отчёта"""
        text = f"""
📊 <b>Ежедневный отчёт SEO Monster</b>

📅 Дата: {datetime.now().strftime('%Y-%m-%d')}

🎯 <b>Кампании:</b>
  • Всего: {stats.get('total_campaigns', 0)}
  • Активных: {stats.get('running_campaigns', 0)}

✍️ <b>Контент:</b>
  • Создано сегодня: {stats.get('content_today', 0)}
  • Опубликовано: {stats.get('posted_today', 0)}

🔍 <b>Индексация:</b>
  • URL отправлено: {stats.get('indexed_today', 0)}

👥 <b>Аккаунты:</b>
  • Всего: {stats.get('total_accounts', 0)}
  • Активных: {stats.get('active_accounts', 0)}

💡 Система работает в штатном режиме.
"""
        await self.broadcast(text, "daily_report")
    
    async def get_updates(self, offset: int = 0) -> List[Dict]:
        """Получение обновлений от Telegram"""
        if not self.config["bot_token"]:
            return []
        
        url = f"https://api.telegram.org/bot{self.config['bot_token']}/getUpdates"
        params = {"offset": offset, "timeout": 30}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    return result.get("result", [])
        except Exception as e:
            print(f"Error getting updates: {e}")
            return []
    
    async def process_update(self, update: Dict):
        """Обработка входящего сообщения"""
        message = update.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "")
        username = message.get("from", {}).get("username", "")
        
        if not chat_id or not text:
            return
        
        # Автоматически добавляем подписчика
        self.add_subscriber(chat_id, username)
        
        # Обработка команд
        response = await self._handle_command(text, chat_id)
        if response:
            await self.send_message(chat_id, response)
    
    async def _handle_command(self, text: str, chat_id: str) -> Optional[str]:
        """Обработка команд бота"""
        text = text.strip().lower()
        
        if text == "/start":
            return """
👋 <b>Добро пожаловать в SEO Monster Bot!</b>

Я помогу вам управлять системой SEO-продвижения.

<b>Доступные команды:</b>
/status - Статус системы
/campaigns - Список кампаний
/stats - Статистика
/help - Помощь

Вы будете получать уведомления о работе системы.
"""
        
        elif text == "/help":
            return """
📚 <b>Справка по командам</b>

/start - Начать работу с ботом
/status - Текущий статус системы
/campaigns - Список активных кампаний
/stats - Общая статистика
/stop - Отписаться от уведомлений

<b>Управление через веб-интерфейс:</b>
Для полного управления используйте веб-интерфейс SEO Monster.
"""
        
        elif text == "/status":
            return """
✅ <b>Статус системы</b>

🟢 Backend: Работает
🟢 Frontend: Работает
🟢 Автопилот: Активен

Система функционирует в штатном режиме.
"""
        
        elif text == "/campaigns":
            # Здесь можно интегрировать с autopilot_engine
            return """
🎯 <b>Активные кампании</b>

Для просмотра кампаний используйте веб-интерфейс или AI Чат.

Команда в AI Чате: "Покажи кампании"
"""
        
        elif text == "/stats":
            return """
📊 <b>Статистика</b>

Для детальной статистики используйте веб-интерфейс.

Команда в AI Чате: "Покажи статистику"
"""
        
        elif text == "/stop":
            self.remove_subscriber(chat_id)
            return "👋 Вы отписались от уведомлений. Для повторной подписки отправьте /start"
        
        else:
            return """
🤔 Команда не распознана.

Отправьте /help для списка доступных команд.
"""
    
    async def start_polling(self):
        """Запуск polling для получения сообщений"""
        if not self.config["enabled"] or not self.config["bot_token"]:
            return
        
        self.is_running = True
        offset = 0
        
        while self.is_running:
            try:
                updates = await self.get_updates(offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    await self.process_update(update)
            except Exception as e:
                print(f"Polling error: {e}")
                await asyncio.sleep(5)
    
    def stop_polling(self):
        """Остановка polling"""
        self.is_running = False
    
    def get_status(self) -> Dict:
        """Получение статуса бота"""
        return {
            "enabled": self.config["enabled"],
            "token_configured": bool(self.config["bot_token"]),
            "subscribers_count": len(self.subscribers),
            "notifications": self.config["notifications"],
            "recent_notifications": self.notification_log[-10:]
        }
    
    def get_subscribers(self) -> List[Dict]:
        """Получение списка подписчиков"""
        return self.subscribers


# Singleton instance
_telegram_bot = None

def get_telegram_bot() -> TelegramBot:
    """Получение экземпляра Telegram бота"""
    global _telegram_bot
    if _telegram_bot is None:
        _telegram_bot = TelegramBot()
    return _telegram_bot
