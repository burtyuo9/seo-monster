"""
SEO Monster - cPanel Manager
Модуль для работы с cPanel хостингами

Возможности:
- Управление файлами через File Manager API
- Редактирование .htaccess для редиректов
- Управление базами данных MySQL
- Создание поддоменов
- Управление DNS записями
- Автоматическое создание бэкапов
"""

import os
import json
import asyncio
import aiohttp
import base64
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from urllib.parse import urlencode

# Пути
DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/cpanel")
DATA_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNTS_FILE = DATA_DIR / "accounts.json"
HTACCESS_TEMPLATES_FILE = DATA_DIR / "htaccess_templates.json"


@dataclass
class CPanelAccount:
    """cPanel аккаунт"""
    id: str
    name: str
    hostname: str  # cpanel.example.com или IP
    port: int  # Обычно 2083 для HTTPS
    username: str
    password: str  # Зашифрованный
    api_token: Optional[str] = None  # API Token (рекомендуется)
    document_root: str = "/public_html"
    status: str = "active"
    last_check: Optional[str] = None
    domains: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.domains is None:
            self.domains = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class CPanelManager:
    """
    Менеджер cPanel аккаунтов
    """
    
    def __init__(self):
        self.accounts: Dict[str, CPanelAccount] = {}
        self.htaccess_templates: Dict[str, Dict] = {}
        
        self._load_data()
        self._init_default_templates()
    
    def _load_data(self):
        """Загрузка данных"""
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for acc_data in data:
                        acc = CPanelAccount(**acc_data)
                        self.accounts[acc.id] = acc
            except Exception as e:
                print(f"Ошибка загрузки cPanel аккаунтов: {e}")
        
        if HTACCESS_TEMPLATES_FILE.exists():
            try:
                with open(HTACCESS_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                    self.htaccess_templates = json.load(f)
            except:
                pass
    
    def _save_accounts(self):
        """Сохранение аккаунтов"""
        data = [asdict(acc) for acc in self.accounts.values()]
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_templates(self):
        """Сохранение шаблонов"""
        with open(HTACCESS_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.htaccess_templates, f, indent=2, ensure_ascii=False)
    
    def _init_default_templates(self):
        """Инициализация стандартных шаблонов .htaccess"""
        if not self.htaccess_templates:
            self.htaccess_templates = {
                "redirect_301": {
                    "name": "301 Редирект на домен",
                    "template": """# 301 Redirect to {{target_domain}}
RewriteEngine On
RewriteCond %{HTTP_HOST} !^{{target_domain}}$ [NC]
RewriteRule ^(.*)$ https://{{target_domain}}/$1 [R=301,L]
"""
                },
                "redirect_302": {
                    "name": "302 Временный редирект",
                    "template": """# 302 Temporary Redirect
RewriteEngine On
RewriteRule ^(.*)$ {{target_url}} [R=302,L]
"""
                },
                "redirect_all_pages": {
                    "name": "Редирект всех страниц на главную",
                    "template": """# Redirect all pages to target
RewriteEngine On
RewriteRule ^.*$ {{target_url}} [R=301,L]
"""
                },
                "geo_redirect": {
                    "name": "Гео-редирект",
                    "template": """# Geo-based redirect
RewriteEngine On
RewriteCond %{HTTP:CF-IPCountry} ^(RU|UA|BY|KZ)$
RewriteRule ^(.*)$ {{target_url_ru}} [R=302,L]

RewriteCond %{HTTP:CF-IPCountry} ^(US|GB|CA|AU)$
RewriteRule ^(.*)$ {{target_url_en}} [R=302,L]
"""
                },
                "mobile_redirect": {
                    "name": "Мобильный редирект",
                    "template": """# Mobile redirect
RewriteEngine On
RewriteCond %{HTTP_USER_AGENT} "android|blackberry|iphone|ipod|iemobile|opera mobile|palmos|webos|googlebot-mobile" [NC]
RewriteRule ^(.*)$ {{mobile_url}} [R=302,L]
"""
                },
                "cloaking": {
                    "name": "Клоакинг для ботов",
                    "template": """# Cloaking - show different content to bots
RewriteEngine On
RewriteCond %{HTTP_USER_AGENT} (googlebot|bingbot|yandex|baiduspider|facebookexternalhit) [NC]
RewriteRule ^(.*)$ {{bot_page}} [L]

RewriteRule ^(.*)$ {{user_page}} [L]
"""
                },
                "block_countries": {
                    "name": "Блокировка стран",
                    "template": """# Block specific countries
RewriteEngine On
RewriteCond %{HTTP:CF-IPCountry} ^(CN|IN|PK)$
RewriteRule ^(.*)$ - [F,L]
"""
                },
                "force_https": {
                    "name": "Принудительный HTTPS",
                    "template": """# Force HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
"""
                }
            }
            self._save_templates()
    
    def _generate_id(self) -> str:
        """Генерация уникального ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{len(self.accounts)}".encode()).hexdigest()[:12]
    
    def _encrypt(self, text: str) -> str:
        """Простое шифрование"""
        return base64.b64encode(text.encode()).decode()
    
    def _decrypt(self, encrypted: str) -> str:
        """Расшифровка"""
        return base64.b64decode(encrypted.encode()).decode()
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ АККАУНТАМИ
    # ═══════════════════════════════════════════════════════════════
    
    def add_account(self, name: str, hostname: str, username: str, 
                   password: str, port: int = 2083,
                   api_token: Optional[str] = None,
                   document_root: str = "/public_html") -> Dict:
        """
        Добавление cPanel аккаунта
        """
        # Нормализация hostname
        hostname = hostname.replace('https://', '').replace('http://', '').split('/')[0]
        
        acc_id = self._generate_id()
        
        account = CPanelAccount(
            id=acc_id,
            name=name,
            hostname=hostname,
            port=port,
            username=username,
            password=self._encrypt(password),
            api_token=self._encrypt(api_token) if api_token else None,
            document_root=document_root
        )
        
        self.accounts[acc_id] = account
        self._save_accounts()
        
        return {
            "success": True,
            "account_id": acc_id,
            "message": f"cPanel аккаунт {name} добавлен"
        }
    
    def import_accounts_bulk(self, accounts_data: str, format_type: str = "txt") -> Dict:
        """
        Массовый импорт cPanel аккаунтов
        Формат TXT: hostname:username:password (по строкам)
        """
        imported = 0
        errors = []
        
        try:
            if format_type == "txt":
                lines = accounts_data.strip().split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(':')
                    if len(parts) >= 3:
                        hostname = parts[0]
                        username = parts[1]
                        password = ':'.join(parts[2:])
                        
                        # Опциональный порт
                        port = 2083
                        if len(parts) >= 4 and parts[3].isdigit():
                            port = int(parts[3])
                            password = parts[2]
                        
                        name = hostname.split('.')[0] if '.' in hostname else hostname
                        
                        try:
                            self.add_account(name, hostname, username, password, port)
                            imported += 1
                        except Exception as e:
                            errors.append(f"Строка {i+1}: {str(e)}")
                    else:
                        errors.append(f"Строка {i+1}: неверный формат")
            
            elif format_type == "json":
                data = json.loads(accounts_data)
                for i, item in enumerate(data):
                    try:
                        self.add_account(
                            name=item.get('name', item.get('hostname', '')),
                            hostname=item['hostname'],
                            username=item['username'],
                            password=item['password'],
                            port=item.get('port', 2083),
                            api_token=item.get('api_token'),
                            document_root=item.get('document_root', '/public_html')
                        )
                        imported += 1
                    except Exception as e:
                        errors.append(f"Элемент {i+1}: {str(e)}")
        
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "imported": imported,
            "errors": errors,
            "total_accounts": len(self.accounts)
        }
    
    def get_accounts(self, status: Optional[str] = None) -> List[Dict]:
        """Получение списка аккаунтов"""
        accounts = []
        for acc in self.accounts.values():
            if status and acc.status != status:
                continue
            
            acc_dict = asdict(acc)
            acc_dict['password'] = '***'
            acc_dict['api_token'] = '***' if acc.api_token else None
            accounts.append(acc_dict)
        
        return accounts
    
    def delete_account(self, account_id: str) -> Dict:
        """Удаление аккаунта"""
        if account_id not in self.accounts:
            return {"success": False, "error": "Аккаунт не найден"}
        
        del self.accounts[account_id]
        self._save_accounts()
        
        return {"success": True, "message": "Аккаунт удалён"}
    
    # ═══════════════════════════════════════════════════════════════
    # РАБОТА С cPanel API
    # ═══════════════════════════════════════════════════════════════
    
    def _get_api_url(self, account: CPanelAccount, module: str, func: str) -> str:
        """Формирование URL для API"""
        return f"https://{account.hostname}:{account.port}/execute/{module}/{func}"
    
    def _get_uapi_url(self, account: CPanelAccount) -> str:
        """URL для UAPI"""
        return f"https://{account.hostname}:{account.port}/execute"
    
    async def _make_api_request(self, account: CPanelAccount, 
                               module: str, func: str, 
                               params: Dict = None) -> Dict:
        """Выполнение API запроса к cPanel"""
        url = self._get_api_url(account, module, func)
        
        # Авторизация
        if account.api_token:
            token = self._decrypt(account.api_token)
            headers = {
                "Authorization": f"cpanel {account.username}:{token}"
            }
        else:
            password = self._decrypt(account.password)
            credentials = f"{account.username}:{password}"
            auth_token = base64.b64encode(credentials.encode()).decode()
            headers = {
                "Authorization": f"Basic {auth_token}"
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params or {},
                    headers=headers,
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"success": True, "data": data}
                    else:
                        text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {text[:200]}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_connection(self, account_id: str) -> Dict:
        """Проверка подключения к cPanel"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        # Пробуем получить информацию о домене
        result = await self._make_api_request(account, "DomainInfo", "list_domains")
        
        if result.get("success"):
            data = result.get("data", {})
            if data.get("status") == 1:
                domains = data.get("data", {})
                account.domains = domains.get("main_domain", [])
                if isinstance(account.domains, str):
                    account.domains = [account.domains]
                account.domains.extend(domains.get("addon_domains", []))
                account.domains.extend(domains.get("parked_domains", []))
                account.status = "active"
                account.last_check = datetime.now().isoformat()
                self._save_accounts()
                
                return {
                    "success": True,
                    "message": "Подключение успешно",
                    "domains": account.domains
                }
            else:
                return {"success": False, "error": data.get("errors", ["Unknown error"])}
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ ФАЙЛАМИ
    # ═══════════════════════════════════════════════════════════════
    
    async def list_files(self, account_id: str, path: str = "/public_html") -> Dict:
        """Получение списка файлов"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        result = await self._make_api_request(
            account, "Fileman", "list_files",
            params={"dir": path, "include_mime": 1, "include_permissions": 1}
        )
        
        if result.get("success"):
            data = result.get("data", {})
            if data.get("status") == 1:
                return {
                    "success": True,
                    "files": data.get("data", []),
                    "path": path
                }
        
        return result
    
    async def read_file(self, account_id: str, file_path: str) -> Dict:
        """Чтение содержимого файла"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        result = await self._make_api_request(
            account, "Fileman", "get_file_content",
            params={"file": file_path}
        )
        
        if result.get("success"):
            data = result.get("data", {})
            if data.get("status") == 1:
                return {
                    "success": True,
                    "content": data.get("data", {}).get("content", ""),
                    "path": file_path
                }
        
        return result
    
    async def write_file(self, account_id: str, file_path: str, content: str) -> Dict:
        """Запись в файл"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        # Для записи используем POST запрос
        url = f"https://{account.hostname}:{account.port}/execute/Fileman/save_file_content"
        
        if account.api_token:
            token = self._decrypt(account.api_token)
            headers = {"Authorization": f"cpanel {account.username}:{token}"}
        else:
            password = self._decrypt(account.password)
            credentials = f"{account.username}:{password}"
            auth_token = base64.b64encode(credentials.encode()).decode()
            headers = {"Authorization": f"Basic {auth_token}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data={"file": file_path, "content": content},
                    headers=headers,
                    ssl=False
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == 1:
                            return {"success": True, "message": "Файл сохранён"}
                        else:
                            return {"success": False, "error": data.get("errors", ["Unknown error"])}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_file(self, account_id: str, file_path: str) -> Dict:
        """Удаление файла"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        result = await self._make_api_request(
            account, "Fileman", "delete_files",
            params={"files": file_path}
        )
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ .htaccess
    # ═══════════════════════════════════════════════════════════════
    
    async def get_htaccess(self, account_id: str, path: str = "/public_html") -> Dict:
        """Получение содержимого .htaccess"""
        htaccess_path = f"{path}/.htaccess"
        return await self.read_file(account_id, htaccess_path)
    
    async def update_htaccess(self, account_id: str, content: str, 
                             path: str = "/public_html") -> Dict:
        """Обновление .htaccess"""
        htaccess_path = f"{path}/.htaccess"
        return await self.write_file(account_id, htaccess_path, content)
    
    async def apply_htaccess_template(self, account_id: str, template_id: str,
                                     variables: Dict[str, str],
                                     path: str = "/public_html",
                                     append: bool = True) -> Dict:
        """
        Применение шаблона .htaccess
        """
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        template = self.htaccess_templates.get(template_id)
        if not template:
            return {"success": False, "error": "Шаблон не найден"}
        
        # Подготовка контента
        content = template.get("template", "")
        
        # Замена переменных
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{{{var_name}}}}}", var_value)
        
        if append:
            # Получаем текущий .htaccess
            current = await self.get_htaccess(account_id, path)
            current_content = current.get("content", "") if current.get("success") else ""
            
            # Добавляем новый контент
            new_content = f"{current_content}\n\n# Added by SEO Monster - {datetime.now().isoformat()}\n{content}"
        else:
            new_content = f"# Generated by SEO Monster - {datetime.now().isoformat()}\n{content}"
        
        return await self.update_htaccess(account_id, new_content, path)
    
    async def setup_redirect(self, account_id: str, target_url: str,
                            redirect_type: str = "301",
                            path: str = "/public_html") -> Dict:
        """
        Быстрая настройка редиректа на целевой URL
        """
        if redirect_type == "301":
            template_id = "redirect_301"
        else:
            template_id = "redirect_302"
        
        # Извлекаем домен из URL
        target_domain = target_url.replace('https://', '').replace('http://', '').split('/')[0]
        
        return await self.apply_htaccess_template(
            account_id=account_id,
            template_id=template_id,
            variables={
                "target_domain": target_domain,
                "target_url": target_url
            },
            path=path,
            append=False  # Заменяем весь .htaccess
        )
    
    async def setup_mass_redirect(self, account_ids: List[str], 
                                 target_url: str,
                                 redirect_type: str = "301") -> Dict:
        """
        Массовая настройка редиректов на нескольких аккаунтах
        """
        results = {
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for account_id in account_ids:
            result = await self.setup_redirect(account_id, target_url, redirect_type)
            
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
                account = self.accounts.get(account_id)
                name = account.name if account else account_id
                results["errors"].append(f"{name}: {result.get('error')}")
            
            await asyncio.sleep(1)  # Задержка между запросами
        
        return results
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ БАЗАМИ ДАННЫХ
    # ═══════════════════════════════════════════════════════════════
    
    async def list_databases(self, account_id: str) -> Dict:
        """Получение списка баз данных"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        result = await self._make_api_request(account, "Mysql", "list_databases")
        
        if result.get("success"):
            data = result.get("data", {})
            if data.get("status") == 1:
                return {
                    "success": True,
                    "databases": data.get("data", [])
                }
        
        return result
    
    async def create_database(self, account_id: str, db_name: str) -> Dict:
        """Создание базы данных"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        # Добавляем префикс пользователя если нужно
        if not db_name.startswith(f"{account.username}_"):
            db_name = f"{account.username}_{db_name}"
        
        result = await self._make_api_request(
            account, "Mysql", "create_database",
            params={"name": db_name}
        )
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ ПОДДОМЕНАМИ
    # ═══════════════════════════════════════════════════════════════
    
    async def list_subdomains(self, account_id: str) -> Dict:
        """Получение списка поддоменов"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        result = await self._make_api_request(account, "SubDomain", "listsubdomains")
        
        if result.get("success"):
            data = result.get("data", {})
            if data.get("status") == 1:
                return {
                    "success": True,
                    "subdomains": data.get("data", [])
                }
        
        return result
    
    async def create_subdomain(self, account_id: str, subdomain: str, 
                              domain: str, document_root: Optional[str] = None) -> Dict:
        """Создание поддомена"""
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": "Аккаунт не найден"}
        
        if document_root is None:
            document_root = f"/public_html/{subdomain}"
        
        result = await self._make_api_request(
            account, "SubDomain", "addsubdomain",
            params={
                "domain": subdomain,
                "rootdomain": domain,
                "dir": document_root
            }
        )
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # ШАБЛОНЫ И СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    def get_htaccess_templates(self) -> Dict:
        """Получение списка шаблонов .htaccess"""
        return self.htaccess_templates
    
    def add_htaccess_template(self, template_id: str, name: str, template: str) -> Dict:
        """Добавление пользовательского шаблона"""
        self.htaccess_templates[template_id] = {
            "name": name,
            "template": template
        }
        self._save_templates()
        
        return {"success": True, "message": "Шаблон добавлен"}
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        total_accounts = len(self.accounts)
        active_accounts = sum(1 for a in self.accounts.values() if a.status == "active")
        total_domains = sum(len(a.domains) for a in self.accounts.values())
        
        return {
            "total_accounts": total_accounts,
            "active_accounts": active_accounts,
            "error_accounts": total_accounts - active_accounts,
            "total_domains": total_domains,
            "htaccess_templates": len(self.htaccess_templates)
        }


# Singleton
_cpanel_manager = None

def get_cpanel_manager() -> CPanelManager:
    """Получение экземпляра cPanel Manager"""
    global _cpanel_manager
    if _cpanel_manager is None:
        _cpanel_manager = CPanelManager()
    return _cpanel_manager
