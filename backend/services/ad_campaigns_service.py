"""
SEO Monster - Ad Campaigns Manager Service
Модуль управления рекламными кампаниями с полной автоматизацией
Поддержка: Google Ads, Bing Ads, LinkedIn Ads, Facebook Ads, TikTok
 Ads
"""

import asyncio
import json
import os
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict


class AdPlatform(str, Enum):
    """Поддерживаемые рекламные платформы"""
    GOOGLE_ADS = "google_ads"
    BING_ADS = "bing_ads"
    LINKEDIN_ADS = "linkedin_ads"
    FACEBOOK_ADS = "facebook_ads"
    TIKTOK_ADS = "tiktok_ads"

    YANDEX_DIRECT = "yandex_direct"
    TWITTER_ADS = "twitter_ads"
    PINTEREST_ADS = "pinterest_ads"


class CampaignStatus(str, Enum):
    """Статусы кампании"""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    MODERATION = "moderation"
    REJECTED = "rejected"


class CampaignType(str, Enum):
    """Типы кампаний"""
    SEO_ONLY = "seo_only"
    ADS_ONLY = "ads_only"
    COMPLEX = "complex"  # SEO + Ads


@dataclass
class AdAccount:
    """Рекламный кабинет"""
    id: str
    platform: AdPlatform
    name: str
    credentials: Dict[str, str]  # Зашифрованные credentials
    balance: float
    currency: str
    status: str
    is_active: bool
    created_at: str
    last_sync: Optional[str] = None
    daily_budget_limit: float = 0.0
    total_spent: float = 0.0
    campaigns_count: int = 0


@dataclass
class AdCampaign:
    """Рекламная кампания"""
    id: str
    account_id: str
    domain_id: str
    name: str
    platform: AdPlatform
    campaign_type: CampaignType
    status: CampaignStatus
    budget: float
    daily_budget: float
    spent: float
    keywords: List[str]
    negative_keywords: List[str]
    white_list: List[str]  # Белый список сайтов
    black_list: List[str]  # Чёрный список сайтов
    geo_targets: List[str]
    language_targets: List[str]
    ad_texts: List[Dict[str, str]]
    landing_url: str
    tracking_url: str  # URL с трекером
    cloaking_enabled: bool
    start_date: str
    end_date: Optional[str]
    created_at: str
    updated_at: str
    stats: Dict[str, Any]


class AdCampaignsService:
    """Сервис управления рекламными кампаниями"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "ad_campaigns")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.accounts_file = os.path.join(self.data_dir, "accounts.json")
        self.campaigns_file = os.path.join(self.data_dir, "campaigns.json")
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.stats_file = os.path.join(self.data_dir, "stats.json")
        self.keywords_file = os.path.join(self.data_dir, "keywords_db.json")
        
        self._init_files()
        
        # Состояние модуля
        self.is_enabled = False
        self.auto_mode = False
        self._running_task = None
    
    def _init_files(self):
        """Инициализация файлов данных"""
        default_config = {
            "enabled": False,
            "auto_mode": False,
            "check_interval": 300,
            "auto_budget_management": True,
            "auto_keyword_research": True,
            "cloaking_default": True,
            "min_budget_threshold": 10.0,
            "max_daily_spend_percent": 20,
            "fraud_protection": True,
            "bot_filtering": True,
            "platforms_config": {
                "google_ads": {"enabled": True, "api_version": "v14"},
                "bing_ads": {"enabled": True, "api_version": "v13"},
                "linkedin_ads": {"enabled": True},
                "facebook_ads": {"enabled": True, "api_version": "v18.0"},
                "tiktok_ads": {"enabled": True},
                "yandex_direct": {"enabled": True, "api_version": "v5"},
                "twitter_ads": {"enabled": False},
                "pinterest_ads": {"enabled": False}
            }
        }
        
        if not os.path.exists(self.config_file):
            self._save_json(self.config_file, default_config)
        
        if not os.path.exists(self.accounts_file):
            self._save_json(self.accounts_file, {"accounts": []})
        
        if not os.path.exists(self.campaigns_file):
            self._save_json(self.campaigns_file, {"campaigns": []})
        
        if not os.path.exists(self.stats_file):
            self._save_json(self.stats_file, {
                "total_accounts": 0,
                "total_campaigns": 0,
                "total_spent": 0.0,
                "total_clicks": 0,
                "total_impressions": 0,
                "total_conversions": 0,
                "blocked_bots": 0,
                "fraud_prevented": 0.0,
                "by_platform": {}
            })
        
        if not os.path.exists(self.keywords_file):
            self._save_json(self.keywords_file, {"keywords": {}, "negative": []})
        
        # Загрузка конфига
        config = self._load_json(self.config_file)
        self.is_enabled = config.get("enabled", False)
        self.auto_mode = config.get("auto_mode", False)
    
    def _load_json(self, filepath: str) -> dict:
        """Загрузка JSON файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_json(self, filepath: str, data: dict):
        """Сохранение JSON файла"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, prefix: str = "") -> str:
        """Генерация уникального ID"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}{timestamp}_{random_str}"
    
    def _encrypt_credentials(self, credentials: Dict[str, str]) -> Dict[str, str]:
        """Простое шифрование credentials (в продакшене использовать proper encryption)"""
        encrypted = {}
        for key, value in credentials.items():
            # В реальном приложении использовать AES или подобное
            encrypted[key] = hashlib.sha256(value.encode()).hexdigest()[:32] + "..." + value[-4:]
        return encrypted
    
    # ==================== УПРАВЛЕНИЕ МОДУЛЕМ ====================
    
    async def enable(self) -> Dict[str, Any]:
        """Включить модуль"""
        self.is_enabled = True
        config = self._load_json(self.config_file)
        config["enabled"] = True
        self._save_json(self.config_file, config)
        return {"status": "enabled", "message": "Ad Campaigns module enabled"}
    
    async def disable(self) -> Dict[str, Any]:
        """Выключить модуль"""
        self.is_enabled = False
        self.auto_mode = False
        if self._running_task:
            self._running_task.cancel()
        config = self._load_json(self.config_file)
        config["enabled"] = False
        config["auto_mode"] = False
        self._save_json(self.config_file, config)
        return {"status": "disabled", "message": "Ad Campaigns module disabled"}
    
    async def set_auto_mode(self, enabled: bool) -> Dict[str, Any]:
        """Установить автоматический режим"""
        if not self.is_enabled:
            return {"error": "Module is disabled. Enable it first."}
        
        self.auto_mode = enabled
        config = self._load_json(self.config_file)
        config["auto_mode"] = enabled
        self._save_json(self.config_file, config)
        
        if enabled:
            # Запуск автоматического цикла
            asyncio.create_task(self._auto_management_loop())
        
        return {"auto_mode": enabled, "message": f"Auto mode {'enabled' if enabled else 'disabled'}"}
    
    async def get_status(self) -> Dict[str, Any]:
        """Получить статус модуля"""
        config = self._load_json(self.config_file)
        stats = self._load_json(self.stats_file)
        accounts_data = self._load_json(self.accounts_file)
        campaigns_data = self._load_json(self.campaigns_file)
        
        active_campaigns = len([c for c in campaigns_data.get("campaigns", []) 
                               if c.get("status") == "active"])
        
        return {
            "enabled": self.is_enabled,
            "auto_mode": self.auto_mode,
            "total_accounts": len(accounts_data.get("accounts", [])),
            "total_campaigns": len(campaigns_data.get("campaigns", [])),
            "active_campaigns": active_campaigns,
            "total_spent": stats.get("total_spent", 0),
            "total_clicks": stats.get("total_clicks", 0),
            "blocked_bots": stats.get("blocked_bots", 0),
            "fraud_prevented": stats.get("fraud_prevented", 0),
            "platforms_enabled": sum(1 for p in config.get("platforms_config", {}).values() 
                                    if p.get("enabled", False))
        }
    
    # ==================== УПРАВЛЕНИЕ АККАУНТАМИ ====================
    
    async def add_account(self, platform: str, name: str, credentials: Dict[str, str],
                         currency: str = "USD", daily_budget_limit: float = 0.0) -> Dict[str, Any]:
        """Добавить рекламный аккаунт"""
        if not self.is_enabled:
            return {"error": "Module is disabled"}
        
        accounts_data = self._load_json(self.accounts_file)
        
        account = {
            "id": self._generate_id("acc_"),
            "platform": platform,
            "name": name,
            "credentials": credentials,  # В реальности шифровать
            "balance": 0.0,
            "currency": currency,
            "status": "pending_verification",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_sync": None,
            "daily_budget_limit": daily_budget_limit,
            "total_spent": 0.0,
            "campaigns_count": 0
        }
        
        accounts_data["accounts"].append(account)
        self._save_json(self.accounts_file, accounts_data)
        
        # Обновление статистики
        stats = self._load_json(self.stats_file)
        stats["total_accounts"] = len(accounts_data["accounts"])
        self._save_json(self.stats_file, stats)
        
        return {"success": True, "account": account}
    
    async def get_accounts(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить список аккаунтов"""
        accounts_data = self._load_json(self.accounts_file)
        accounts = accounts_data.get("accounts", [])
        
        if platform:
            accounts = [a for a in accounts if a.get("platform") == platform]
        
        # Скрываем credentials
        for account in accounts:
            if "credentials" in account:
                account["credentials"] = {"status": "hidden"}
        
        return accounts
    
    async def update_account_balance(self, account_id: str, balance: float) -> Dict[str, Any]:
        """Обновить баланс аккаунта"""
        accounts_data = self._load_json(self.accounts_file)
        
        for account in accounts_data["accounts"]:
            if account["id"] == account_id:
                account["balance"] = balance
                account["last_sync"] = datetime.now().isoformat()
                self._save_json(self.accounts_file, accounts_data)
                return {"success": True, "balance": balance}
        
        return {"error": "Account not found"}
    
    async def delete_account(self, account_id: str) -> Dict[str, Any]:
        """Удалить аккаунт"""
        accounts_data = self._load_json(self.accounts_file)
        accounts_data["accounts"] = [a for a in accounts_data["accounts"] 
                                     if a["id"] != account_id]
        self._save_json(self.accounts_file, accounts_data)
        return {"success": True, "message": "Account deleted"}
    
    # ==================== УПРАВЛЕНИЕ КАМПАНИЯМИ ====================
    
    async def create_campaign(self, account_id: str, domain_id: str, name: str,
                            campaign_type: str, budget: float, daily_budget: float,
                            keywords: List[str], geo_targets: List[str],
                            language_targets: List[str], landing_url: str,
                            ad_texts: List[Dict[str, str]] = None,
                            white_list: List[str] = None,
                            black_list: List[str] = None,
                            cloaking_enabled: bool = True,
                            auto_keywords: bool = True) -> Dict[str, Any]:
        """Создать рекламную кампанию"""
        if not self.is_enabled:
            return {"error": "Module is disabled"}
        
        # Получаем аккаунт
        accounts_data = self._load_json(self.accounts_file)
        account = next((a for a in accounts_data["accounts"] if a["id"] == account_id), None)
        
        if not account:
            return {"error": "Account not found"}
        
        # Автоподбор ключевых слов если нужно
        if auto_keywords and not keywords:
            keywords = await self._auto_research_keywords(domain_id, landing_url)
        
        # Генерация tracking URL с интеграцией трекера
        tracking_url = await self._generate_tracking_url(landing_url, domain_id)
        
        campaigns_data = self._load_json(self.campaigns_file)
        
        campaign = {
            "id": self._generate_id("camp_"),
            "account_id": account_id,
            "domain_id": domain_id,
            "name": name,
            "platform": account["platform"],
            "campaign_type": campaign_type,
            "status": "draft",
            "budget": budget,
            "daily_budget": daily_budget,
            "spent": 0.0,
            "keywords": keywords,
            "negative_keywords": await self._get_default_negative_keywords(),
            "white_list": white_list or [],
            "black_list": black_list or await self._get_default_blacklist(),
            "geo_targets": geo_targets,
            "language_targets": language_targets,
            "ad_texts": ad_texts or [],
            "landing_url": landing_url,
            "tracking_url": tracking_url,
            "cloaking_enabled": cloaking_enabled,
            "start_date": datetime.now().isoformat(),
            "end_date": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "stats": {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "ctr": 0.0,
                "cpc": 0.0,
                "cpa": 0.0,
                "roi": 0.0
            }
        }
        
        campaigns_data["campaigns"].append(campaign)
        self._save_json(self.campaigns_file, campaigns_data)
        
        # Обновление счётчика кампаний в аккаунте
        for acc in accounts_data["accounts"]:
            if acc["id"] == account_id:
                acc["campaigns_count"] = acc.get("campaigns_count", 0) + 1
        self._save_json(self.accounts_file, accounts_data)
        
        return {"success": True, "campaign": campaign}
    
    async def get_campaigns(self, domain_id: Optional[str] = None, 
                           account_id: Optional[str] = None,
                           status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить список кампаний"""
        campaigns_data = self._load_json(self.campaigns_file)
        campaigns = campaigns_data.get("campaigns", [])
        
        if domain_id:
            campaigns = [c for c in campaigns if c.get("domain_id") == domain_id]
        if account_id:
            campaigns = [c for c in campaigns if c.get("account_id") == account_id]
        if status:
            campaigns = [c for c in campaigns if c.get("status") == status]
        
        return campaigns
    
    async def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Запустить кампанию"""
        campaigns_data = self._load_json(self.campaigns_file)
        
        for campaign in campaigns_data["campaigns"]:
            if campaign["id"] == campaign_id:
                # Проверка баланса аккаунта
                accounts_data = self._load_json(self.accounts_file)
                account = next((a for a in accounts_data["accounts"] 
                               if a["id"] == campaign["account_id"]), None)
                
                if account and account.get("balance", 0) < campaign.get("daily_budget", 0):
                    return {"error": "Insufficient balance in account"}
                
                campaign["status"] = "active"
                campaign["updated_at"] = datetime.now().isoformat()
                self._save_json(self.campaigns_file, campaigns_data)
                
                # Интеграция с трекером
                await self._notify_tracker_campaign_started(campaign)
                
                return {"success": True, "status": "active"}
        
        return {"error": "Campaign not found"}
    
    async def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Приостановить кампанию"""
        campaigns_data = self._load_json(self.campaigns_file)
        
        for campaign in campaigns_data["campaigns"]:
            if campaign["id"] == campaign_id:
                campaign["status"] = "paused"
                campaign["updated_at"] = datetime.now().isoformat()
                self._save_json(self.campaigns_file, campaigns_data)
                return {"success": True, "status": "paused"}
        
        return {"error": "Campaign not found"}
    
    async def update_campaign_budget(self, campaign_id: str, budget: float = None,
                                    daily_budget: float = None) -> Dict[str, Any]:
        """Обновить бюджет кампании"""
        campaigns_data = self._load_json(self.campaigns_file)
        
        for campaign in campaigns_data["campaigns"]:
            if campaign["id"] == campaign_id:
                if budget is not None:
                    campaign["budget"] = budget
                if daily_budget is not None:
                    campaign["daily_budget"] = daily_budget
                campaign["updated_at"] = datetime.now().isoformat()
                self._save_json(self.campaigns_file, campaigns_data)
                return {"success": True, "campaign": campaign}
        
        return {"error": "Campaign not found"}
    
    async def add_keywords(self, campaign_id: str, keywords: List[str]) -> Dict[str, Any]:
        """Добавить ключевые слова в кампанию"""
        campaigns_data = self._load_json(self.campaigns_file)
        
        for campaign in campaigns_data["campaigns"]:
            if campaign["id"] == campaign_id:
                existing = set(campaign.get("keywords", []))
                existing.update(keywords)
                campaign["keywords"] = list(existing)
                campaign["updated_at"] = datetime.now().isoformat()
                self._save_json(self.campaigns_file, campaigns_data)
                return {"success": True, "keywords_count": len(campaign["keywords"])}
        
        return {"error": "Campaign not found"}
    
    async def update_white_black_lists(self, campaign_id: str, 
                                       white_list: List[str] = None,
                                       black_list: List[str] = None) -> Dict[str, Any]:
        """Обновить белый/чёрный списки"""
        campaigns_data = self._load_json(self.campaigns_file)
        
        for campaign in campaigns_data["campaigns"]:
            if campaign["id"] == campaign_id:
                if white_list is not None:
                    campaign["white_list"] = white_list
                if black_list is not None:
                    campaign["black_list"] = black_list
                campaign["updated_at"] = datetime.now().isoformat()
                self._save_json(self.campaigns_file, campaigns_data)
                return {"success": True}
        
        return {"error": "Campaign not found"}
    
    # ==================== АВТОМАТИЗАЦИЯ ====================
    
    async def _auto_management_loop(self):
        """Автоматический цикл управления кампаниями"""
        config = self._load_json(self.config_file)
        interval = config.get("check_interval", 300)
        
        while self.auto_mode and self.is_enabled:
            try:
                await self._auto_manage_campaigns()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Auto management error: {e}")
                await asyncio.sleep(60)
    
    async def _auto_manage_campaigns(self):
        """Автоматическое управление кампаниями"""
        campaigns_data = self._load_json(self.campaigns_file)
        accounts_data = self._load_json(self.accounts_file)
        config = self._load_json(self.config_file)
        
        for campaign in campaigns_data["campaigns"]:
            if campaign["status"] != "active":
                continue
            
            account = next((a for a in accounts_data["accounts"] 
                           if a["id"] == campaign["account_id"]), None)
            
            if not account:
                continue
            
            # Проверка бюджета
            if config.get("auto_budget_management"):
                await self._check_and_adjust_budget(campaign, account)
            
            # Обновление ключевых слов
            if config.get("auto_keyword_research"):
                await self._auto_optimize_keywords(campaign)
        
        self._save_json(self.campaigns_file, campaigns_data)
    
    async def _check_and_adjust_budget(self, campaign: Dict, account: Dict):
        """Проверка и корректировка бюджета"""
        config = self._load_json(self.config_file)
        min_threshold = config.get("min_budget_threshold", 10.0)
        
        # Если баланс аккаунта низкий - приостановить кампанию
        if account.get("balance", 0) < min_threshold:
            campaign["status"] = "paused"
            campaign["updated_at"] = datetime.now().isoformat()
        
        # Если потрачено больше дневного бюджета - приостановить до завтра
        daily_spent = campaign.get("stats", {}).get("daily_spent", 0)
        if daily_spent >= campaign.get("daily_budget", 0):
            campaign["status"] = "paused"
    
    async def _auto_optimize_keywords(self, campaign: Dict):
        """Автоматическая оптимизация ключевых слов"""
        stats = campaign.get("stats", {})
        keywords = campaign.get("keywords", [])
        
        # Анализ эффективности ключевых слов
        # В реальности здесь был бы анализ CTR, конверсий и т.д.
        pass
    
    async def _auto_research_keywords(self, domain_id: str, landing_url: str) -> List[str]:
        """Автоматический подбор ключевых слов"""
        # Базовые ключевые слова на основе URL
        keywords = []
        
        # Извлечение слов из URL
        url_parts = landing_url.replace("https://", "").replace("http://", "").split("/")
        for part in url_parts:
            words = part.replace("-", " ").replace("_", " ").split()
            keywords.extend([w for w in words if len(w) > 3])
        
        # Загрузка сохранённых ключевых слов для домена
        keywords_data = self._load_json(self.keywords_file)
        domain_keywords = keywords_data.get("keywords", {}).get(domain_id, [])
        keywords.extend(domain_keywords)
        
        return list(set(keywords))[:50]  # Максимум 50 ключевых слов
    
    async def _get_default_negative_keywords(self) -> List[str]:
        """Получить дефолтные минус-слова"""
        return [
            "free", "бесплатно", "скачать", "download", "torrent",
            "crack", "keygen", "serial", "hack", "cheat",
            "xxx", "porn", "adult", "casino", "gambling"
        ]
    
    async def _get_default_blacklist(self) -> List[str]:
        """Получить дефолтный чёрный список сайтов"""
        return [
            "*.torrent.*", "*.xxx.*", "*.porn.*",
            "*.casino.*", "*.gambling.*", "*.adult.*"
        ]
    
    async def _generate_tracking_url(self, landing_url: str, domain_id: str) -> str:
        """Генерация tracking URL с интеграцией трекера"""
        # Интеграция с TDS трекером
        tracking_params = {
            "utm_source": "{source}",
            "utm_medium": "cpc",
            "utm_campaign": "{campaign_id}",
            "utm_content": "{ad_id}",
            "click_id": "{click_id}",
            "domain_id": domain_id
        }
        
        params_str = "&".join([f"{k}={v}" for k, v in tracking_params.items()])
        separator = "&" if "?" in landing_url else "?"
        
        return f"{landing_url}{separator}{params_str}"
    
    async def _notify_tracker_campaign_started(self, campaign: Dict):
        """Уведомить трекер о запуске кампании"""
        # Интеграция с TDS сервисом
        pass
    
    # ==================== СТАТИСТИКА ====================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получить общую статистику"""
        stats = self._load_json(self.stats_file)
        campaigns_data = self._load_json(self.campaigns_file)
        accounts_data = self._load_json(self.accounts_file)
        
        # Агрегация статистики по кампаниям
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        total_spent = 0.0
        
        for campaign in campaigns_data.get("campaigns", []):
            camp_stats = campaign.get("stats", {})
            total_impressions += camp_stats.get("impressions", 0)
            total_clicks += camp_stats.get("clicks", 0)
            total_conversions += camp_stats.get("conversions", 0)
            total_spent += campaign.get("spent", 0)
        
        # Статистика по платформам
        by_platform = {}
        for campaign in campaigns_data.get("campaigns", []):
            platform = campaign.get("platform", "unknown")
            if platform not in by_platform:
                by_platform[platform] = {
                    "campaigns": 0,
                    "spent": 0.0,
                    "clicks": 0,
                    "conversions": 0
                }
            by_platform[platform]["campaigns"] += 1
            by_platform[platform]["spent"] += campaign.get("spent", 0)
            by_platform[platform]["clicks"] += campaign.get("stats", {}).get("clicks", 0)
            by_platform[platform]["conversions"] += campaign.get("stats", {}).get("conversions", 0)
        
        # Общий баланс всех аккаунтов
        total_balance = sum(a.get("balance", 0) for a in accounts_data.get("accounts", []))
        
        return {
            "total_accounts": len(accounts_data.get("accounts", [])),
            "total_campaigns": len(campaigns_data.get("campaigns", [])),
            "active_campaigns": len([c for c in campaigns_data.get("campaigns", []) 
                                    if c.get("status") == "active"]),
            "total_balance": total_balance,
            "total_spent": total_spent,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "avg_ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
            "avg_cpc": (total_spent / total_clicks) if total_clicks > 0 else 0,
            "blocked_bots": stats.get("blocked_bots", 0),
            "fraud_prevented": stats.get("fraud_prevented", 0),
            "by_platform": by_platform
        }
    
    async def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Получить статистику кампании"""
        campaigns_data = self._load_json(self.campaigns_file)
        
        for campaign in campaigns_data["campaigns"]:
            if campaign["id"] == campaign_id:
                return {
                    "campaign_id": campaign_id,
                    "name": campaign.get("name"),
                    "status": campaign.get("status"),
                    "budget": campaign.get("budget"),
                    "spent": campaign.get("spent"),
                    "stats": campaign.get("stats", {}),
                    "keywords_count": len(campaign.get("keywords", [])),
                    "white_list_count": len(campaign.get("white_list", [])),
                    "black_list_count": len(campaign.get("black_list", []))
                }
        
        return {"error": "Campaign not found"}


# Глобальный экземпляр сервиса
ad_campaigns_service = AdCampaignsService()
