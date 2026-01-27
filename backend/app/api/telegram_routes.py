"""
SEO Monster - Telegram API Routes
API эндпоинты для интеграции с Telegram
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, List

import sys
sys.path.append('/home/ubuntu/seo_monster/backend')

from services.telegram_bot import get_telegram_bot

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


# Pydantic модели
class ConfigureRequest(BaseModel):
    bot_token: str
    admin_chat_id: Optional[str] = None


class NotificationSettingsRequest(BaseModel):
    campaign_started: Optional[bool] = None
    campaign_completed: Optional[bool] = None
    campaign_error: Optional[bool] = None
    content_generated: Optional[bool] = None
    content_posted: Optional[bool] = None
    indexing_completed: Optional[bool] = None
    daily_report: Optional[bool] = None


class SendMessageRequest(BaseModel):
    chat_id: str
    message: str


class BroadcastRequest(BaseModel):
    message: str
    notification_type: Optional[str] = "general"


class TestNotificationRequest(BaseModel):
    notification_type: str


# API Endpoints

@router.get("/status")
async def get_status():
    """Получение статуса Telegram бота"""
    bot = get_telegram_bot()
    return bot.get_status()


@router.post("/configure")
async def configure_bot(request: ConfigureRequest):
    """
    Настройка Telegram бота
    
    Для получения токена:
    1. Напишите @BotFather в Telegram
    2. Отправьте /newbot
    3. Следуйте инструкциям
    4. Скопируйте токен
    """
    bot = get_telegram_bot()
    result = bot.configure(request.bot_token, request.admin_chat_id)
    return result


@router.post("/enable")
async def enable_bot():
    """Включение бота"""
    bot = get_telegram_bot()
    return bot.enable()


@router.post("/disable")
async def disable_bot():
    """Отключение бота"""
    bot = get_telegram_bot()
    return bot.disable()


@router.put("/notifications")
async def update_notifications(request: NotificationSettingsRequest):
    """Обновление настроек уведомлений"""
    bot = get_telegram_bot()
    
    settings = {}
    if request.campaign_started is not None:
        settings["campaign_started"] = request.campaign_started
    if request.campaign_completed is not None:
        settings["campaign_completed"] = request.campaign_completed
    if request.campaign_error is not None:
        settings["campaign_error"] = request.campaign_error
    if request.content_generated is not None:
        settings["content_generated"] = request.content_generated
    if request.content_posted is not None:
        settings["content_posted"] = request.content_posted
    if request.indexing_completed is not None:
        settings["indexing_completed"] = request.indexing_completed
    if request.daily_report is not None:
        settings["daily_report"] = request.daily_report
    
    return bot.update_notifications(settings)


@router.get("/subscribers")
async def get_subscribers():
    """Получение списка подписчиков"""
    bot = get_telegram_bot()
    return {"subscribers": bot.get_subscribers()}


@router.delete("/subscribers/{chat_id}")
async def remove_subscriber(chat_id: str):
    """Удаление подписчика"""
    bot = get_telegram_bot()
    return bot.remove_subscriber(chat_id)


@router.post("/send")
async def send_message(request: SendMessageRequest):
    """Отправка сообщения конкретному пользователю"""
    bot = get_telegram_bot()
    result = await bot.send_message(request.chat_id, request.message)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/broadcast")
async def broadcast_message(request: BroadcastRequest):
    """Рассылка сообщения всем подписчикам"""
    bot = get_telegram_bot()
    result = await bot.broadcast(request.message, request.notification_type)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/test")
async def test_notification(request: TestNotificationRequest):
    """
    Отправка тестового уведомления
    
    Типы уведомлений:
    - campaign_started
    - campaign_completed
    - campaign_error
    - content_generated
    - content_posted
    - indexing_completed
    - daily_report
    """
    bot = get_telegram_bot()
    
    test_messages = {
        "campaign_started": lambda: bot.notify_campaign_started("test-domain.com"),
        "campaign_completed": lambda: bot.notify_campaign_completed("test-domain.com", {
            "content_generated": 5,
            "content_posted": 3,
            "urls_indexed": 10
        }),
        "campaign_error": lambda: bot.notify_campaign_error("test-domain.com", "Тестовая ошибка"),
        "content_generated": lambda: bot.notify_content_generated("Тестовая статья", "test-domain.com"),
        "content_posted": lambda: bot.notify_content_posted("Тестовая статья", "Test Platform", "https://example.com/post"),
        "indexing_completed": lambda: bot.notify_indexing_completed("https://test-domain.com/page", ["Google", "Bing"]),
        "daily_report": lambda: bot.send_daily_report({
            "total_campaigns": 5,
            "running_campaigns": 2,
            "content_today": 10,
            "posted_today": 8,
            "indexed_today": 15,
            "total_accounts": 100,
            "active_accounts": 85
        })
    }
    
    if request.notification_type not in test_messages:
        raise HTTPException(status_code=400, detail=f"Unknown notification type: {request.notification_type}")
    
    await test_messages[request.notification_type]()
    
    return {"status": "sent", "type": request.notification_type}


@router.get("/notifications/history")
async def get_notification_history(limit: int = 50):
    """Получение истории уведомлений"""
    bot = get_telegram_bot()
    status = bot.get_status()
    
    notifications = status.get("recent_notifications", [])
    return {"notifications": notifications[-limit:]}


@router.get("/webhook/info")
async def get_webhook_info():
    """Информация о настройке webhook"""
    return {
        "info": "Webhook позволяет получать сообщения без polling",
        "setup_steps": [
            "1. Настройте HTTPS на вашем сервере",
            "2. Укажите URL webhook в настройках",
            "3. Telegram будет отправлять обновления на этот URL"
        ],
        "webhook_url_format": "https://your-domain.com/api/telegram/webhook"
    }


@router.post("/webhook")
async def telegram_webhook(update: Dict, background_tasks: BackgroundTasks):
    """
    Webhook endpoint для получения обновлений от Telegram
    
    Telegram будет отправлять POST запросы на этот URL
    """
    bot = get_telegram_bot()
    
    # Обрабатываем в фоне, чтобы быстро ответить Telegram
    background_tasks.add_task(bot.process_update, update)
    
    return {"ok": True}


@router.get("/commands")
async def get_bot_commands():
    """Список команд бота"""
    return {
        "commands": [
            {"command": "/start", "description": "Начать работу с ботом"},
            {"command": "/help", "description": "Показать справку"},
            {"command": "/status", "description": "Статус системы"},
            {"command": "/campaigns", "description": "Список кампаний"},
            {"command": "/stats", "description": "Статистика"},
            {"command": "/stop", "description": "Отписаться от уведомлений"}
        ]
    }
