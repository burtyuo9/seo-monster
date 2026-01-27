"""
AWS SES Service - Модуль управления рассылками через Amazon SES
Полная информация о ключах, регионах, лимитах и статистике
"""

import json
import os
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re

# AWS SDK
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

class SESRegion(Enum):
    """Доступные регионы AWS SES"""
    US_EAST_1 = "us-east-1"  # N. Virginia
    US_EAST_2 = "us-east-2"  # Ohio
    US_WEST_1 = "us-west-1"  # N. California
    US_WEST_2 = "us-west-2"  # Oregon
    EU_WEST_1 = "eu-west-1"  # Ireland
    EU_WEST_2 = "eu-west-2"  # London
    EU_WEST_3 = "eu-west-3"  # Paris
    EU_CENTRAL_1 = "eu-central-1"  # Frankfurt
    EU_NORTH_1 = "eu-north-1"  # Stockholm
    AP_SOUTH_1 = "ap-south-1"  # Mumbai
    AP_NORTHEAST_1 = "ap-northeast-1"  # Tokyo
    AP_NORTHEAST_2 = "ap-northeast-2"  # Seoul
    AP_SOUTHEAST_1 = "ap-southeast-1"  # Singapore
    AP_SOUTHEAST_2 = "ap-southeast-2"  # Sydney
    SA_EAST_1 = "sa-east-1"  # São Paulo
    CA_CENTRAL_1 = "ca-central-1"  # Canada
    ME_SOUTH_1 = "me-south-1"  # Bahrain
    AF_SOUTH_1 = "af-south-1"  # Cape Town

class EmailFormat(Enum):
    """Поддерживаемые форматы писем"""
    HTML = "html"
    TEXT = "text"
    MIXED = "mixed"  # HTML + Text fallback
    TEMPLATE = "template"  # AWS SES Template
    RAW = "raw"  # Raw MIME
    AMP = "amp"  # AMP for Email

class CampaignStatus(Enum):
    """Статусы кампании рассылки"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AWSKeyInfo:
    """Полная информация об AWS ключе"""
    access_key_id: str
    secret_key_masked: str
    region: str
    account_id: str
    iam_user: str
    ses_verified: bool
    sandbox_mode: bool
    sending_enabled: bool
    max_send_rate: float  # emails per second
    max_24_hour_send: int
    sent_last_24_hours: int
    remaining_quota: int
    verified_emails: List[str]
    verified_domains: List[str]
    dedicated_ips: List[str]
    reputation_metrics: Dict[str, Any]
    suppression_list_count: int
    configuration_sets: List[str]
    created_at: str
    last_checked: str

@dataclass
class EmailTemplate:
    """Шаблон письма"""
    id: str
    name: str
    subject: str
    html_content: str
    text_content: str
    format: str
    variables: List[str]
    created_at: str
    updated_at: str
    used_count: int

@dataclass
class RecipientList:
    """База получателей"""
    id: str
    name: str
    description: str
    file_type: str  # csv, txt, xlsx, json
    total_count: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    fields: List[str]  # email, name, etc.
    file_path: str
    created_at: str
    last_used: str

@dataclass
class EmailCampaign:
    """Кампания рассылки"""
    id: str
    name: str
    aws_key_id: str
    template_id: str
    recipient_list_id: str
    from_email: str
    from_name: str
    reply_to: str
    subject: str
    status: str
    scheduled_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    total_recipients: int
    sent_count: int
    delivered_count: int
    bounced_count: int
    complained_count: int
    opened_count: int
    clicked_count: int
    send_rate: float  # emails per second
    created_at: str

class AWSSESService:
    """Сервис управления AWS SES"""
    
    def __init__(self):
        self.data_dir = "/home/ubuntu/seo_monster/backend/data"
        self.keys_file = f"{self.data_dir}/ses_keys.json"
        self.templates_file = f"{self.data_dir}/ses_templates.json"
        self.lists_file = f"{self.data_dir}/ses_recipient_lists.json"
        self.campaigns_file = f"{self.data_dir}/ses_campaigns.json"
        self.uploads_dir = f"{self.data_dir}/ses_uploads"
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        self.keys: Dict[str, Dict] = {}
        self.templates: Dict[str, EmailTemplate] = {}
        self.recipient_lists: Dict[str, RecipientList] = {}
        self.campaigns: Dict[str, EmailCampaign] = {}
        
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных из файлов"""
        # Keys
        if os.path.exists(self.keys_file):
            with open(self.keys_file, 'r') as f:
                self.keys = json.load(f)
        
        # Templates
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
                self.templates = {k: EmailTemplate(**v) for k, v in data.items()}
        
        # Recipient lists
        if os.path.exists(self.lists_file):
            with open(self.lists_file, 'r') as f:
                data = json.load(f)
                self.recipient_lists = {k: RecipientList(**v) for k, v in data.items()}
        
        # Campaigns
        if os.path.exists(self.campaigns_file):
            with open(self.campaigns_file, 'r') as f:
                data = json.load(f)
                self.campaigns = {k: EmailCampaign(**v) for k, v in data.items()}
    
    def _save_keys(self):
        """Сохранение ключей"""
        with open(self.keys_file, 'w') as f:
            json.dump(self.keys, f, indent=2, default=str)
    
    def _save_templates(self):
        """Сохранение шаблонов"""
        with open(self.templates_file, 'w') as f:
            data = {k: asdict(v) for k, v in self.templates.items()}
            json.dump(data, f, indent=2)
    
    def _save_lists(self):
        """Сохранение списков получателей"""
        with open(self.lists_file, 'w') as f:
            data = {k: asdict(v) for k, v in self.recipient_lists.items()}
            json.dump(data, f, indent=2)
    
    def _save_campaigns(self):
        """Сохранение кампаний"""
        with open(self.campaigns_file, 'w') as f:
            data = {k: asdict(v) for k, v in self.campaigns.items()}
            json.dump(data, f, indent=2)
    
    def _mask_secret_key(self, secret_key: str) -> str:
        """Маскирование секретного ключа"""
        if len(secret_key) <= 8:
            return "*" * len(secret_key)
        return secret_key[:4] + "*" * (len(secret_key) - 8) + secret_key[-4:]
    
    def _generate_id(self) -> str:
        """Генерация уникального ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{os.urandom(8).hex()}".encode()).hexdigest()[:12]
    
    async def add_aws_key(self, access_key_id: str, secret_access_key: str, 
                         region: str = "us-east-1", name: str = "") -> Dict:
        """
        Добавление AWS ключа с полной проверкой и получением информации
        """
        if not AWS_AVAILABLE:
            return {
                "success": False,
                "error": "boto3 not installed. Run: pip install boto3"
            }
        
        try:
            # Создаем клиент SES
            ses_client = boto3.client(
                'ses',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region
            )
            
            # Создаем клиент IAM для информации об аккаунте
            iam_client = boto3.client(
                'iam',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region
            )
            
            # Создаем клиент STS для ID аккаунта
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region
            )
            
            # Получаем информацию об аккаунте
            account_info = sts_client.get_caller_identity()
            account_id = account_info['Account']
            iam_user = account_info.get('Arn', '').split('/')[-1]
            
            # Получаем квоту отправки
            send_quota = ses_client.get_send_quota()
            
            # Получаем статистику отправки
            send_stats = ses_client.get_send_statistics()
            
            # Получаем верифицированные email адреса
            verified_emails_response = ses_client.list_verified_email_addresses()
            verified_emails = verified_emails_response.get('VerifiedEmailAddresses', [])
            
            # Получаем верифицированные домены
            verified_identities = ses_client.list_identities(IdentityType='Domain')
            verified_domains = verified_identities.get('Identities', [])
            
            # Проверяем sandbox режим
            # В sandbox режиме max_24_hour_send обычно 200
            sandbox_mode = send_quota['Max24HourSend'] <= 200
            
            # Получаем configuration sets
            try:
                config_sets_response = ses_client.list_configuration_sets()
                configuration_sets = [cs['Name'] for cs in config_sets_response.get('ConfigurationSets', [])]
            except:
                configuration_sets = []
            
            # Получаем dedicated IPs (если есть)
            dedicated_ips = []
            try:
                # SESv2 для dedicated IPs
                sesv2_client = boto3.client(
                    'sesv2',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    region_name=region
                )
                ips_response = sesv2_client.list_dedicated_ip_pools()
                for pool in ips_response.get('DedicatedIpPools', []):
                    pool_ips = sesv2_client.get_dedicated_ips(PoolName=pool)
                    dedicated_ips.extend([ip['Ip'] for ip in pool_ips.get('DedicatedIps', [])])
            except:
                pass
            
            # Получаем метрики репутации
            reputation_metrics = {}
            try:
                sesv2_client = boto3.client(
                    'sesv2',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    region_name=region
                )
                account_details = sesv2_client.get_account()
                reputation_metrics = {
                    "sending_enabled": account_details.get('SendingEnabled', False),
                    "enforcement_status": account_details.get('EnforcementStatus', 'UNKNOWN'),
                    "production_access": account_details.get('ProductionAccessEnabled', False)
                }
            except:
                reputation_metrics = {"sending_enabled": True, "enforcement_status": "UNKNOWN"}
            
            # Получаем количество в suppression list
            suppression_count = 0
            try:
                sesv2_client = boto3.client(
                    'sesv2',
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    region_name=region
                )
                # Просто проверяем доступность
                suppression_count = 0
            except:
                pass
            
            # Формируем информацию о ключе
            key_id = self._generate_id()
            key_info = {
                "id": key_id,
                "name": name or f"AWS Key {access_key_id[:8]}",
                "access_key_id": access_key_id,
                "secret_access_key": secret_access_key,  # Храним зашифрованно в реальном приложении
                "secret_key_masked": self._mask_secret_key(secret_access_key),
                "region": region,
                "region_name": self._get_region_name(region),
                "account_id": account_id,
                "iam_user": iam_user,
                "ses_verified": True,
                "sandbox_mode": sandbox_mode,
                "sending_enabled": reputation_metrics.get('sending_enabled', True),
                "max_send_rate": send_quota['MaxSendRate'],
                "max_24_hour_send": int(send_quota['Max24HourSend']),
                "sent_last_24_hours": int(send_quota['SentLast24Hours']),
                "remaining_quota": int(send_quota['Max24HourSend'] - send_quota['SentLast24Hours']),
                "verified_emails": verified_emails,
                "verified_domains": verified_domains,
                "dedicated_ips": dedicated_ips,
                "reputation_metrics": reputation_metrics,
                "suppression_list_count": suppression_count,
                "configuration_sets": configuration_sets,
                "created_at": datetime.now().isoformat(),
                "last_checked": datetime.now().isoformat(),
                "status": "active"
            }
            
            self.keys[key_id] = key_info
            self._save_keys()
            
            # Возвращаем информацию без секретного ключа
            safe_info = {k: v for k, v in key_info.items() if k != 'secret_access_key'}
            
            return {
                "success": True,
                "key_info": safe_info,
                "recommendations": self._get_recommendations(key_info)
            }
            
        except NoCredentialsError:
            return {"success": False, "error": "Invalid AWS credentials"}
        except ClientError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_region_name(self, region_code: str) -> str:
        """Получение человекочитаемого названия региона"""
        region_names = {
            "us-east-1": "US East (N. Virginia)",
            "us-east-2": "US East (Ohio)",
            "us-west-1": "US West (N. California)",
            "us-west-2": "US West (Oregon)",
            "eu-west-1": "Europe (Ireland)",
            "eu-west-2": "Europe (London)",
            "eu-west-3": "Europe (Paris)",
            "eu-central-1": "Europe (Frankfurt)",
            "eu-north-1": "Europe (Stockholm)",
            "ap-south-1": "Asia Pacific (Mumbai)",
            "ap-northeast-1": "Asia Pacific (Tokyo)",
            "ap-northeast-2": "Asia Pacific (Seoul)",
            "ap-southeast-1": "Asia Pacific (Singapore)",
            "ap-southeast-2": "Asia Pacific (Sydney)",
            "sa-east-1": "South America (São Paulo)",
            "ca-central-1": "Canada (Central)",
            "me-south-1": "Middle East (Bahrain)",
            "af-south-1": "Africa (Cape Town)"
        }
        return region_names.get(region_code, region_code)
    
    def _get_recommendations(self, key_info: Dict) -> List[str]:
        """Получение рекомендаций для ключа"""
        recommendations = []
        
        if key_info['sandbox_mode']:
            recommendations.append("⚠️ Аккаунт в Sandbox режиме. Можно отправлять только на верифицированные адреса. Запросите Production Access в AWS Console.")
        
        if not key_info['verified_domains']:
            recommendations.append("📧 Добавьте и верифицируйте домен для лучшей доставляемости")
        
        if key_info['remaining_quota'] < 100:
            recommendations.append("⚡ Осталось мало квоты на сегодня. Подождите или запросите увеличение лимита.")
        
        if not key_info['dedicated_ips']:
            recommendations.append("🌐 Рассмотрите использование Dedicated IPs для высоких объемов рассылки")
        
        if key_info['max_send_rate'] < 10:
            recommendations.append("🚀 Низкая скорость отправки. Запросите увеличение в AWS Support.")
        
        return recommendations
    
    async def refresh_key_info(self, key_id: str) -> Dict:
        """Обновление информации о ключе"""
        if key_id not in self.keys:
            return {"success": False, "error": "Key not found"}
        
        key = self.keys[key_id]
        return await self.add_aws_key(
            key['access_key_id'],
            key['secret_access_key'],
            key['region'],
            key['name']
        )
    
    def get_all_keys(self) -> List[Dict]:
        """Получение всех ключей (без секретных данных)"""
        result = []
        for key_id, key_info in self.keys.items():
            safe_info = {k: v for k, v in key_info.items() if k != 'secret_access_key'}
            result.append(safe_info)
        return result
    
    def get_key_info(self, key_id: str) -> Optional[Dict]:
        """Получение информации о конкретном ключе"""
        if key_id not in self.keys:
            return None
        key_info = self.keys[key_id]
        return {k: v for k, v in key_info.items() if k != 'secret_access_key'}
    
    def delete_key(self, key_id: str) -> bool:
        """Удаление ключа"""
        if key_id in self.keys:
            del self.keys[key_id]
            self._save_keys()
            return True
        return False
    
    def get_available_regions(self) -> List[Dict]:
        """Получение списка доступных регионов SES"""
        regions = []
        for region in SESRegion:
            regions.append({
                "code": region.value,
                "name": self._get_region_name(region.value),
                "recommended_for_inbox": region.value in ["us-east-1", "eu-west-1", "eu-central-1"]
            })
        return regions


# Создаем глобальный экземпляр сервиса
ses_service = AWSSESService()
