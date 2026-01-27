"""
SEO Monster - Localization Service
Система локализации для поддержки русского и английского языков
"""

import json
import os
from typing import Dict, Optional, Any
from pathlib import Path
from functools import lru_cache

# Директория с переводами
LOCALES_DIR = Path("/home/ubuntu/seo_monster/backend/locales")
LOCALES_DIR.mkdir(parents=True, exist_ok=True)

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ["en", "ru"]
DEFAULT_LANGUAGE = "en"

# Переводы
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # General
        "app_name": "SEO Monster",
        "welcome": "Welcome to SEO Monster",
        "loading": "Loading...",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "create": "Create",
        "update": "Update",
        "search": "Search",
        "filter": "Filter",
        "export": "Export",
        "import": "Import",
        "refresh": "Refresh",
        "close": "Close",
        "confirm": "Confirm",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Information",
        "status": "Status",
        "actions": "Actions",
        "settings": "Settings",
        "help": "Help",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "all": "All",
        "none": "None",
        "select": "Select",
        "selected": "Selected",
        "total": "Total",
        "active": "Active",
        "inactive": "Inactive",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "online": "Online",
        "offline": "Offline",
        "connected": "Connected",
        "disconnected": "Disconnected",
        
        # Navigation
        "nav_dashboard": "Dashboard",
        "nav_autopilot": "Autopilot",
        "nav_sites": "Sites",
        "nav_platforms": "Platforms",
        "nav_content": "Content",
        "nav_ad_campaigns": "Ad Campaigns",
        "nav_tracker": "Tracker",
        "nav_ads_integration": "Ads Integration",
        "nav_email_ses": "Email SES",
        "nav_diagnostics": "Diagnostics",
        "nav_settings": "Settings",
        
        # Dashboard
        "total_sites": "Total Sites",
        "total_platforms": "Total Platforms",
        "total_content": "Total Content",
        "active_tasks": "Active Tasks",
        "today_stats": "Today's Statistics",
        "weekly_stats": "Weekly Statistics",
        "monthly_stats": "Monthly Statistics",
        
        # Autopilot
        "autopilot_status": "Autopilot Status",
        "autopilot_running": "Autopilot is running",
        "autopilot_stopped": "Autopilot is stopped",
        "start_autopilot": "Start Autopilot",
        "stop_autopilot": "Stop Autopilot",
        "autopilot_mode": "Autopilot Mode",
        "autopilot_aggressive": "Aggressive",
        "autopilot_moderate": "Moderate",
        "autopilot_conservative": "Conservative",
        
        # Email SES
        "ses_keys": "SES Keys",
        "add_ses_key": "Add SES Key",
        "ses_key_name": "Key Name",
        "ses_access_key": "Access Key ID",
        "ses_secret_key": "Secret Access Key",
        "ses_region": "Region",
        "ses_status": "Status",
        "ses_daily_quota": "Daily Quota",
        "ses_sent_today": "Sent Today",
        "ses_bounce_rate": "Bounce Rate",
        "ses_complaint_rate": "Complaint Rate",
        
        # Warmup
        "warmup_plans": "Warmup Plans",
        "create_warmup_plan": "Create Warmup Plan",
        "warmup_strategy": "Warmup Strategy",
        "warmup_conservative": "Conservative (21 days)",
        "warmup_moderate": "Moderate (14 days)",
        "warmup_aggressive": "Aggressive (7 days)",
        "warmup_status": "Warmup Status",
        "warmup_in_progress": "In Progress",
        "warmup_completed": "Completed",
        "warmup_paused": "Paused",
        "warmup_not_started": "Not Started",
        "warmup_day": "Day",
        "warmup_target_volume": "Target Volume",
        "warmup_actual_sent": "Actual Sent",
        "warmup_delivery_rate": "Delivery Rate",
        "warmup_health_score": "Health Score",
        
        # A/B Testing
        "ab_tests": "A/B Tests",
        "create_ab_test": "Create A/B Test",
        "ab_test_name": "Test Name",
        "ab_variant_a": "Variant A",
        "ab_variant_b": "Variant B",
        "ab_winner": "Winner",
        "ab_confidence": "Confidence",
        "ab_open_rate": "Open Rate",
        "ab_click_rate": "Click Rate",
        
        # Tracker/TDS
        "tds_campaigns": "TDS Campaigns",
        "create_campaign": "Create Campaign",
        "campaign_name": "Campaign Name",
        "campaign_url": "Campaign URL",
        "total_clicks": "Total Clicks",
        "unique_clicks": "Unique Clicks",
        "conversions": "Conversions",
        "conversion_rate": "Conversion Rate",
        "revenue": "Revenue",
        "cost": "Cost",
        "profit": "Profit",
        "roi": "ROI",
        "epc": "EPC",
        
        # Ad Campaigns
        "ad_accounts": "Ad Accounts",
        "add_ad_account": "Add Ad Account",
        "ad_platform": "Platform",
        "ad_budget": "Budget",
        "ad_spent": "Spent",
        "ad_impressions": "Impressions",
        "ad_ctr": "CTR",
        "ad_cpc": "CPC",
        
        # Diagnostics
        "run_diagnostics": "Run Diagnostics",
        "quick_check": "Quick Check",
        "full_check": "Full Check",
        "health_score": "Health Score",
        "issues_found": "Issues Found",
        "auto_fix": "Auto Fix",
        "fix_all": "Fix All",
        "diagnostic_category": "Category",
        "diagnostic_status": "Status",
        "diagnostic_message": "Message",
        "diagnostic_ok": "OK",
        "diagnostic_warning": "Warning",
        "diagnostic_error": "Error",
        "diagnostic_critical": "Critical",
        
        # Settings
        "general_settings": "General Settings",
        "api_settings": "API Settings",
        "notification_settings": "Notification Settings",
        "language": "Language",
        "theme": "Theme",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "timezone": "Timezone",
        "api_key": "API Key",
        "telegram_bot": "Telegram Bot",
        "telegram_token": "Bot Token",
        "telegram_chat_id": "Chat ID",
        
        # Messages
        "msg_saved": "Changes saved successfully",
        "msg_deleted": "Item deleted successfully",
        "msg_created": "Item created successfully",
        "msg_updated": "Item updated successfully",
        "msg_error": "An error occurred",
        "msg_confirm_delete": "Are you sure you want to delete this item?",
        "msg_no_data": "No data available",
        "msg_loading": "Loading data...",
        "msg_api_connected": "API Connected",
        "msg_api_disconnected": "API Disconnected",
        
        # Errors
        "err_required_field": "This field is required",
        "err_invalid_email": "Invalid email address",
        "err_invalid_url": "Invalid URL",
        "err_min_length": "Minimum length is {min} characters",
        "err_max_length": "Maximum length is {max} characters",
        "err_network": "Network error. Please try again.",
        "err_server": "Server error. Please try again later.",
        "err_unauthorized": "Unauthorized. Please log in.",
        "err_forbidden": "Access forbidden",
        "err_not_found": "Resource not found",
    },
    "ru": {
        # General
        "app_name": "SEO Monster",
        "welcome": "Добро пожаловать в SEO Monster",
        "loading": "Загрузка...",
        "save": "Сохранить",
        "cancel": "Отмена",
        "delete": "Удалить",
        "edit": "Редактировать",
        "create": "Создать",
        "update": "Обновить",
        "search": "Поиск",
        "filter": "Фильтр",
        "export": "Экспорт",
        "import": "Импорт",
        "refresh": "Обновить",
        "close": "Закрыть",
        "confirm": "Подтвердить",
        "yes": "Да",
        "no": "Нет",
        "ok": "ОК",
        "error": "Ошибка",
        "success": "Успешно",
        "warning": "Предупреждение",
        "info": "Информация",
        "status": "Статус",
        "actions": "Действия",
        "settings": "Настройки",
        "help": "Помощь",
        "back": "Назад",
        "next": "Далее",
        "previous": "Предыдущий",
        "all": "Все",
        "none": "Нет",
        "select": "Выбрать",
        "selected": "Выбрано",
        "total": "Всего",
        "active": "Активный",
        "inactive": "Неактивный",
        "enabled": "Включено",
        "disabled": "Отключено",
        "online": "Онлайн",
        "offline": "Оффлайн",
        "connected": "Подключено",
        "disconnected": "Отключено",
        
        # Navigation
        "nav_dashboard": "Панель управления",
        "nav_autopilot": "Автопилот",
        "nav_sites": "Сайты",
        "nav_platforms": "Платформы",
        "nav_content": "Контент",
        "nav_ad_campaigns": "Рекламные кампании",
        "nav_tracker": "Трекер",
        "nav_ads_integration": "Интеграция рекламы",
        "nav_email_ses": "Email SES",
        "nav_diagnostics": "Диагностика",
        "nav_settings": "Настройки",
        
        # Dashboard
        "total_sites": "Всего сайтов",
        "total_platforms": "Всего платформ",
        "total_content": "Всего контента",
        "active_tasks": "Активных задач",
        "today_stats": "Статистика за сегодня",
        "weekly_stats": "Статистика за неделю",
        "monthly_stats": "Статистика за месяц",
        
        # Autopilot
        "autopilot_status": "Статус автопилота",
        "autopilot_running": "Автопилот запущен",
        "autopilot_stopped": "Автопилот остановлен",
        "start_autopilot": "Запустить автопилот",
        "stop_autopilot": "Остановить автопилот",
        "autopilot_mode": "Режим автопилота",
        "autopilot_aggressive": "Агрессивный",
        "autopilot_moderate": "Умеренный",
        "autopilot_conservative": "Консервативный",
        
        # Email SES
        "ses_keys": "Ключи SES",
        "add_ses_key": "Добавить ключ SES",
        "ses_key_name": "Название ключа",
        "ses_access_key": "Access Key ID",
        "ses_secret_key": "Secret Access Key",
        "ses_region": "Регион",
        "ses_status": "Статус",
        "ses_daily_quota": "Дневная квота",
        "ses_sent_today": "Отправлено сегодня",
        "ses_bounce_rate": "Процент отказов",
        "ses_complaint_rate": "Процент жалоб",
        
        # Warmup
        "warmup_plans": "Планы прогрева",
        "create_warmup_plan": "Создать план прогрева",
        "warmup_strategy": "Стратегия прогрева",
        "warmup_conservative": "Консервативная (21 день)",
        "warmup_moderate": "Умеренная (14 дней)",
        "warmup_aggressive": "Агрессивная (7 дней)",
        "warmup_status": "Статус прогрева",
        "warmup_in_progress": "В процессе",
        "warmup_completed": "Завершено",
        "warmup_paused": "Приостановлено",
        "warmup_not_started": "Не начато",
        "warmup_day": "День",
        "warmup_target_volume": "Целевой объём",
        "warmup_actual_sent": "Фактически отправлено",
        "warmup_delivery_rate": "Процент доставки",
        "warmup_health_score": "Показатель здоровья",
        
        # A/B Testing
        "ab_tests": "A/B Тесты",
        "create_ab_test": "Создать A/B тест",
        "ab_test_name": "Название теста",
        "ab_variant_a": "Вариант A",
        "ab_variant_b": "Вариант B",
        "ab_winner": "Победитель",
        "ab_confidence": "Достоверность",
        "ab_open_rate": "Процент открытий",
        "ab_click_rate": "Процент кликов",
        
        # Tracker/TDS
        "tds_campaigns": "Кампании TDS",
        "create_campaign": "Создать кампанию",
        "campaign_name": "Название кампании",
        "campaign_url": "URL кампании",
        "total_clicks": "Всего кликов",
        "unique_clicks": "Уникальных кликов",
        "conversions": "Конверсии",
        "conversion_rate": "Процент конверсии",
        "revenue": "Доход",
        "cost": "Расходы",
        "profit": "Прибыль",
        "roi": "ROI",
        "epc": "EPC",
        
        # Ad Campaigns
        "ad_accounts": "Рекламные аккаунты",
        "add_ad_account": "Добавить аккаунт",
        "ad_platform": "Платформа",
        "ad_budget": "Бюджет",
        "ad_spent": "Потрачено",
        "ad_impressions": "Показы",
        "ad_ctr": "CTR",
        "ad_cpc": "CPC",
        
        # Diagnostics
        "run_diagnostics": "Запустить диагностику",
        "quick_check": "Быстрая проверка",
        "full_check": "Полная проверка",
        "health_score": "Показатель здоровья",
        "issues_found": "Найдено проблем",
        "auto_fix": "Авто-исправление",
        "fix_all": "Исправить все",
        "diagnostic_category": "Категория",
        "diagnostic_status": "Статус",
        "diagnostic_message": "Сообщение",
        "diagnostic_ok": "ОК",
        "diagnostic_warning": "Предупреждение",
        "diagnostic_error": "Ошибка",
        "diagnostic_critical": "Критично",
        
        # Settings
        "general_settings": "Общие настройки",
        "api_settings": "Настройки API",
        "notification_settings": "Настройки уведомлений",
        "language": "Язык",
        "theme": "Тема",
        "theme_light": "Светлая",
        "theme_dark": "Тёмная",
        "timezone": "Часовой пояс",
        "api_key": "API ключ",
        "telegram_bot": "Telegram бот",
        "telegram_token": "Токен бота",
        "telegram_chat_id": "ID чата",
        
        # Messages
        "msg_saved": "Изменения сохранены",
        "msg_deleted": "Элемент удалён",
        "msg_created": "Элемент создан",
        "msg_updated": "Элемент обновлён",
        "msg_error": "Произошла ошибка",
        "msg_confirm_delete": "Вы уверены, что хотите удалить этот элемент?",
        "msg_no_data": "Нет данных",
        "msg_loading": "Загрузка данных...",
        "msg_api_connected": "API подключено",
        "msg_api_disconnected": "API отключено",
        
        # Errors
        "err_required_field": "Это поле обязательно",
        "err_invalid_email": "Неверный email адрес",
        "err_invalid_url": "Неверный URL",
        "err_min_length": "Минимальная длина {min} символов",
        "err_max_length": "Максимальная длина {max} символов",
        "err_network": "Ошибка сети. Попробуйте снова.",
        "err_server": "Ошибка сервера. Попробуйте позже.",
        "err_unauthorized": "Не авторизован. Войдите в систему.",
        "err_forbidden": "Доступ запрещён",
        "err_not_found": "Ресурс не найден",
    }
}


class LocalizationService:
    """Сервис локализации"""
    
    def __init__(self):
        self.current_language = DEFAULT_LANGUAGE
        self._load_custom_translations()
    
    def _load_custom_translations(self):
        """Загрузка пользовательских переводов"""
        for lang in SUPPORTED_LANGUAGES:
            custom_file = LOCALES_DIR / f"{lang}.json"
            if custom_file.exists():
                try:
                    with open(custom_file, 'r', encoding='utf-8') as f:
                        custom = json.load(f)
                        TRANSLATIONS[lang].update(custom)
                except Exception:
                    pass
    
    def set_language(self, lang: str) -> bool:
        """Установка текущего языка"""
        if lang in SUPPORTED_LANGUAGES:
            self.current_language = lang
            return True
        return False
    
    def get_language(self) -> str:
        """Получение текущего языка"""
        return self.current_language
    
    def get_supported_languages(self) -> list:
        """Получение списка поддерживаемых языков"""
        return SUPPORTED_LANGUAGES.copy()
    
    @lru_cache(maxsize=1000)
    def t(self, key: str, lang: str = None, **kwargs) -> str:
        """Получение перевода по ключу"""
        lang = lang or self.current_language
        
        if lang not in TRANSLATIONS:
            lang = DEFAULT_LANGUAGE
        
        text = TRANSLATIONS[lang].get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
        
        # Подстановка параметров
        if kwargs:
            for k, v in kwargs.items():
                text = text.replace(f"{{{k}}}", str(v))
        
        return text
    
    def translate(self, key: str, lang: str = None, **kwargs) -> str:
        """Алиас для t()"""
        return self.t(key, lang, **kwargs)
    
    def get_all_translations(self, lang: str = None) -> Dict[str, str]:
        """Получение всех переводов для языка"""
        lang = lang or self.current_language
        return TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE]).copy()
    
    def add_translation(self, key: str, translations: Dict[str, str]):
        """Добавление нового перевода"""
        for lang, text in translations.items():
            if lang in TRANSLATIONS:
                TRANSLATIONS[lang][key] = text
        
        # Очистка кэша
        self.t.cache_clear()
    
    def save_custom_translations(self, lang: str, translations: Dict[str, str]):
        """Сохранение пользовательских переводов"""
        custom_file = LOCALES_DIR / f"{lang}.json"
        with open(custom_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
        
        # Обновляем в памяти
        TRANSLATIONS[lang].update(translations)
        self.t.cache_clear()


# Глобальный экземпляр
localization = LocalizationService()

# Удобные функции
def t(key: str, **kwargs) -> str:
    """Получение перевода"""
    return localization.t(key, **kwargs)

def set_language(lang: str) -> bool:
    """Установка языка"""
    return localization.set_language(lang)

def get_language() -> str:
    """Получение текущего языка"""
    return localization.get_language()
