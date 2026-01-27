"""
Optional Features Service
Управление опциональными функциями системы
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class FeatureStatus(str, Enum):
    CONFIGURED = "configured"
    NOT_CONFIGURED = "not_configured"
    PARTIALLY_CONFIGURED = "partially_configured"


@dataclass
class OptionalFeature:
    """Опциональная функция системы"""
    id: str
    name: str
    name_ru: str
    description: str
    description_ru: str
    icon: str
    status: FeatureStatus
    config_url: str
    benefits: List[str]
    benefits_ru: List[str]
    requirements: List[Dict[str, str]]
    configured_items: int = 0
    total_items: int = 1
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "name_ru": self.name_ru,
            "description": self.description,
            "description_ru": self.description_ru,
            "icon": self.icon,
            "status": self.status.value,
            "config_url": self.config_url,
            "benefits": self.benefits,
            "benefits_ru": self.benefits_ru,
            "requirements": self.requirements,
            "configured_items": self.configured_items,
            "total_items": self.total_items,
            "progress": int((self.configured_items / self.total_items) * 100) if self.total_items > 0 else 0
        }


class OptionalFeaturesService:
    """Сервис управления опциональными функциями"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        
    def get_all_features(self) -> List[OptionalFeature]:
        """Получить список всех опциональных функций с их статусом"""
        features = []
        
        # 1. Email Marketing (AWS SES)
        features.append(self._check_email_marketing())
        
        # 2. Telegram Notifications
        features.append(self._check_telegram_notifications())
        
        # 3. AWS Cloud Integration
        features.append(self._check_aws_integration())
        
        # 4. Ad Platforms Integration
        features.append(self._check_ad_platforms())
        
        # 5. WordPress Integration
        features.append(self._check_wordpress_integration())
        
        # 6. cPanel Integration
        features.append(self._check_cpanel_integration())
        
        return features
    
    def get_feature_by_id(self, feature_id: str) -> Optional[OptionalFeature]:
        """Получить информацию о конкретной функции"""
        features = self.get_all_features()
        for feature in features:
            if feature.id == feature_id:
                return feature
        return None
    
    def get_setup_progress(self) -> Dict:
        """Получить общий прогресс настройки системы"""
        features = self.get_all_features()
        
        # Основные компоненты (всегда настроены)
        core_components = [
            {"id": "core_api", "name": "Core API", "name_ru": "Основной API", "configured": True},
            {"id": "ai_providers", "name": "AI Providers", "name_ru": "AI Провайдеры", "configured": True},
            {"id": "sites_manager", "name": "Sites Manager", "name_ru": "Менеджер сайтов", "configured": True},
            {"id": "content_engine", "name": "Content Engine", "name_ru": "Контент движок", "configured": True},
            {"id": "diagnostics", "name": "Diagnostics", "name_ru": "Диагностика", "configured": True},
        ]
        
        # Опциональные компоненты
        optional_components = []
        for feature in features:
            optional_components.append({
                "id": feature.id,
                "name": feature.name,
                "name_ru": feature.name_ru,
                "configured": feature.status == FeatureStatus.CONFIGURED,
                "icon": feature.icon
            })
        
        # Подсчет прогресса
        total_core = len(core_components)
        configured_core = sum(1 for c in core_components if c["configured"])
        
        total_optional = len(optional_components)
        configured_optional = sum(1 for c in optional_components if c["configured"])
        
        total = total_core + total_optional
        configured = configured_core + configured_optional
        
        return {
            "core": {
                "components": core_components,
                "total": total_core,
                "configured": configured_core,
                "progress": int((configured_core / total_core) * 100) if total_core > 0 else 0
            },
            "optional": {
                "components": optional_components,
                "total": total_optional,
                "configured": configured_optional,
                "progress": int((configured_optional / total_optional) * 100) if total_optional > 0 else 0
            },
            "overall": {
                "total": total,
                "configured": configured,
                "progress": int((configured / total) * 100) if total > 0 else 0
            }
        }
    
    def _check_email_marketing(self) -> OptionalFeature:
        """Проверка настройки Email Marketing (AWS SES)"""
        try:
            keys_file = self.data_dir / "ses" / "keys.json"
            if keys_file.exists():
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                    active_keys = [k for k in keys if k.get("status") == "active"]
                    if active_keys:
                        return OptionalFeature(
                            id="email_marketing",
                            name="Email Marketing",
                            name_ru="Email Маркетинг",
                            description="Send automated email campaigns with AWS SES",
                            description_ru="Отправка автоматических email кампаний через AWS SES",
                            icon="📧",
                            status=FeatureStatus.CONFIGURED,
                            config_url="/email-ses",
                            benefits=[
                                "Automated email campaigns",
                                "Domain warm-up for deliverability",
                                "A/B testing for emails",
                                "Detailed analytics"
                            ],
                            benefits_ru=[
                                "Автоматические email кампании",
                                "Прогрев домена для доставляемости",
                                "A/B тестирование писем",
                                "Детальная аналитика"
                            ],
                            requirements=[
                                {"name": "AWS Access Key", "configured": True},
                                {"name": "AWS Secret Key", "configured": True}
                            ],
                            configured_items=len(active_keys),
                            total_items=1
                        )
        except:
            pass
        
        return OptionalFeature(
            id="email_marketing",
            name="Email Marketing",
            name_ru="Email Маркетинг",
            description="Send automated email campaigns with AWS SES",
            description_ru="Отправка автоматических email кампаний через AWS SES",
            icon="📧",
            status=FeatureStatus.NOT_CONFIGURED,
            config_url="/email-ses",
            benefits=[
                "Automated email campaigns",
                "Domain warm-up for deliverability",
                "A/B testing for emails",
                "Detailed analytics"
            ],
            benefits_ru=[
                "Автоматические email кампании",
                "Прогрев домена для доставляемости",
                "A/B тестирование писем",
                "Детальная аналитика"
            ],
            requirements=[
                {"name": "AWS Access Key", "configured": False},
                {"name": "AWS Secret Key", "configured": False}
            ],
            configured_items=0,
            total_items=1
        )
    
    def _check_telegram_notifications(self) -> OptionalFeature:
        """Проверка настройки Telegram уведомлений"""
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        
        # Также проверяем в настройках
        try:
            config_file = self.data_dir / "config" / "settings.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    if settings.get("telegram_bot_token"):
                        bot_token = settings["telegram_bot_token"]
        except:
            pass
        
        if bot_token:
            return OptionalFeature(
                id="telegram_notifications",
                name="Telegram Notifications",
                name_ru="Telegram Уведомления",
                description="Get instant alerts on your phone via Telegram",
                description_ru="Мгновенные уведомления на телефон через Telegram",
                icon="📱",
                status=FeatureStatus.CONFIGURED,
                config_url="/settings",
                benefits=[
                    "Instant task notifications",
                    "Error alerts",
                    "Daily reports",
                    "Custom triggers"
                ],
                benefits_ru=[
                    "Мгновенные уведомления о задачах",
                    "Алерты об ошибках",
                    "Ежедневные отчеты",
                    "Настраиваемые триггеры"
                ],
                requirements=[
                    {"name": "Bot Token", "configured": True},
                    {"name": "Chat ID", "configured": True}
                ],
                configured_items=1,
                total_items=1
            )
        
        return OptionalFeature(
            id="telegram_notifications",
            name="Telegram Notifications",
            name_ru="Telegram Уведомления",
            description="Get instant alerts on your phone via Telegram",
            description_ru="Мгновенные уведомления на телефон через Telegram",
            icon="📱",
            status=FeatureStatus.NOT_CONFIGURED,
            config_url="/settings",
            benefits=[
                "Instant task notifications",
                "Error alerts",
                "Daily reports",
                "Custom triggers"
            ],
            benefits_ru=[
                "Мгновенные уведомления о задачах",
                "Алерты об ошибках",
                "Ежедневные отчеты",
                "Настраиваемые триггеры"
            ],
            requirements=[
                {"name": "Bot Token", "configured": False},
                {"name": "Chat ID", "configured": False}
            ],
            configured_items=0,
            total_items=1
        )
    
    def _check_aws_integration(self) -> OptionalFeature:
        """Проверка AWS интеграции"""
        aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
        aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
        
        if aws_key and aws_secret:
            return OptionalFeature(
                id="aws_integration",
                name="AWS Cloud Integration",
                name_ru="AWS Облачная интеграция",
                description="Cloud storage and advanced AWS features",
                description_ru="Облачное хранилище и расширенные функции AWS",
                icon="☁️",
                status=FeatureStatus.CONFIGURED,
                config_url="/settings",
                benefits=[
                    "S3 file storage",
                    "CloudFront CDN",
                    "Lambda functions",
                    "Auto-scaling"
                ],
                benefits_ru=[
                    "S3 хранилище файлов",
                    "CloudFront CDN",
                    "Lambda функции",
                    "Авто-масштабирование"
                ],
                requirements=[
                    {"name": "AWS Access Key", "configured": True},
                    {"name": "AWS Secret Key", "configured": True}
                ],
                configured_items=2,
                total_items=2
            )
        
        return OptionalFeature(
            id="aws_integration",
            name="AWS Cloud Integration",
            name_ru="AWS Облачная интеграция",
            description="Cloud storage and advanced AWS features",
            description_ru="Облачное хранилище и расширенные функции AWS",
            icon="☁️",
            status=FeatureStatus.NOT_CONFIGURED,
            config_url="/settings",
            benefits=[
                "S3 file storage",
                "CloudFront CDN",
                "Lambda functions",
                "Auto-scaling"
            ],
            benefits_ru=[
                "S3 хранилище файлов",
                "CloudFront CDN",
                "Lambda функции",
                "Авто-масштабирование"
            ],
            requirements=[
                {"name": "AWS Access Key", "configured": False},
                {"name": "AWS Secret Key", "configured": False}
            ],
            configured_items=0,
            total_items=2
        )
    
    def _check_ad_platforms(self) -> OptionalFeature:
        """Проверка интеграции рекламных платформ"""
        try:
            accounts_file = self.data_dir / "ads" / "accounts.json"
            if accounts_file.exists():
                with open(accounts_file, 'r') as f:
                    accounts = json.load(f)
                    if accounts:
                        return OptionalFeature(
                            id="ad_platforms",
                            name="Ad Platforms",
                            name_ru="Рекламные платформы",
                            description="Manage ads across Google, Facebook, TikTok, Yandex",
                            description_ru="Управление рекламой в Google, Facebook, TikTok, Яндекс",
                            icon="📢",
                            status=FeatureStatus.CONFIGURED,
                            config_url="/ad-campaigns",
                            benefits=[
                                "Multi-platform campaigns",
                                "Automated bidding",
                                "Fraud protection",
                                "Unified analytics"
                            ],
                            benefits_ru=[
                                "Мультиплатформенные кампании",
                                "Автоматические ставки",
                                "Защита от фрода",
                                "Единая аналитика"
                            ],
                            requirements=[
                                {"name": "Ad Account", "configured": True}
                            ],
                            configured_items=len(accounts),
                            total_items=1
                        )
        except:
            pass
        
        return OptionalFeature(
            id="ad_platforms",
            name="Ad Platforms",
            name_ru="Рекламные платформы",
            description="Manage ads across Google, Facebook, TikTok, Yandex",
            description_ru="Управление рекламой в Google, Facebook, TikTok, Яндекс",
            icon="📢",
            status=FeatureStatus.NOT_CONFIGURED,
            config_url="/ad-campaigns",
            benefits=[
                "Multi-platform campaigns",
                "Automated bidding",
                "Fraud protection",
                "Unified analytics"
            ],
            benefits_ru=[
                "Мультиплатформенные кампании",
                "Автоматические ставки",
                "Защита от фрода",
                "Единая аналитика"
            ],
            requirements=[
                {"name": "Ad Account", "configured": False}
            ],
            configured_items=0,
            total_items=1
        )
    
    def _check_wordpress_integration(self) -> OptionalFeature:
        """Проверка WordPress интеграции"""
        try:
            wp_file = self.data_dir / "wordpress" / "sites.json"
            if wp_file.exists():
                with open(wp_file, 'r') as f:
                    sites = json.load(f)
                    if sites:
                        return OptionalFeature(
                            id="wordpress_integration",
                            name="WordPress Integration",
                            name_ru="WordPress Интеграция",
                            description="Auto-publish content to WordPress sites",
                            description_ru="Автопубликация контента на WordPress сайты",
                            icon="📝",
                            status=FeatureStatus.CONFIGURED,
                            config_url="/sites",
                            benefits=[
                                "Auto-publish articles",
                                "SEO optimization",
                                "Image upload",
                                "Schedule posts"
                            ],
                            benefits_ru=[
                                "Автопубликация статей",
                                "SEO оптимизация",
                                "Загрузка изображений",
                                "Планирование постов"
                            ],
                            requirements=[
                                {"name": "WordPress Site", "configured": True}
                            ],
                            configured_items=len(sites),
                            total_items=1
                        )
        except:
            pass
        
        return OptionalFeature(
            id="wordpress_integration",
            name="WordPress Integration",
            name_ru="WordPress Интеграция",
            description="Auto-publish content to WordPress sites",
            description_ru="Автопубликация контента на WordPress сайты",
            icon="📝",
            status=FeatureStatus.NOT_CONFIGURED,
            config_url="/sites",
            benefits=[
                "Auto-publish articles",
                "SEO optimization",
                "Image upload",
                "Schedule posts"
            ],
            benefits_ru=[
                "Автопубликация статей",
                "SEO оптимизация",
                "Загрузка изображений",
                "Планирование постов"
            ],
            requirements=[
                {"name": "WordPress Site", "configured": False}
            ],
            configured_items=0,
            total_items=1
        )
    
    def _check_cpanel_integration(self) -> OptionalFeature:
        """Проверка cPanel интеграции"""
        try:
            cpanel_file = self.data_dir / "cpanel" / "accounts.json"
            if cpanel_file.exists():
                with open(cpanel_file, 'r') as f:
                    accounts = json.load(f)
                    if accounts:
                        return OptionalFeature(
                            id="cpanel_integration",
                            name="cPanel Integration",
                            name_ru="cPanel Интеграция",
                            description="Manage hosting accounts and domains",
                            description_ru="Управление хостинг аккаунтами и доменами",
                            icon="🖥️",
                            status=FeatureStatus.CONFIGURED,
                            config_url="/platforms",
                            benefits=[
                                "Domain management",
                                "SSL certificates",
                                "Database management",
                                "File manager"
                            ],
                            benefits_ru=[
                                "Управление доменами",
                                "SSL сертификаты",
                                "Управление базами данных",
                                "Файловый менеджер"
                            ],
                            requirements=[
                                {"name": "cPanel Account", "configured": True}
                            ],
                            configured_items=len(accounts),
                            total_items=1
                        )
        except:
            pass
        
        return OptionalFeature(
            id="cpanel_integration",
            name="cPanel Integration",
            name_ru="cPanel Интеграция",
            description="Manage hosting accounts and domains",
            description_ru="Управление хостинг аккаунтами и доменами",
            icon="🖥️",
            status=FeatureStatus.NOT_CONFIGURED,
            config_url="/platforms",
            benefits=[
                "Domain management",
                "SSL certificates",
                "Database management",
                "File manager"
            ],
            benefits_ru=[
                "Управление доменами",
                "SSL сертификаты",
                "Управление базами данных",
                "Файловый менеджер"
            ],
            requirements=[
                {"name": "cPanel Account", "configured": False}
            ],
            configured_items=0,
            total_items=1
        )


# Создание экземпляра сервиса
optional_features_service = OptionalFeaturesService()
