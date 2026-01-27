"""
SEO Monster - WordPress Manager
Модуль для управления WordPress сайтами

Возможности:
- Подключение к WP через REST API или XML-RPC
- Создание/редактирование постов и страниц
- Управление плагинами и темами
- Настройка редиректов
- Автоматическая смена контента
- Вставка рекламных блоков
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
from enum import Enum

# Пути
DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/wordpress")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SITES_FILE = DATA_DIR / "sites.json"
CONTENT_TEMPLATES_FILE = DATA_DIR / "content_templates.json"
REDIRECT_RULES_FILE = DATA_DIR / "redirect_rules.json"
AD_BLOCKS_FILE = DATA_DIR / "ad_blocks.json"


class WPConnectionType(Enum):
    REST_API = "rest_api"
    XML_RPC = "xml_rpc"
    DIRECT_DB = "direct_db"


@dataclass
class WPSite:
    """WordPress сайт"""
    id: str
    name: str
    url: str
    admin_url: str
    username: str
    password: str  # Зашифрованный
    app_password: Optional[str] = None  # Application Password для REST API
    connection_type: str = "rest_api"
    status: str = "active"
    last_sync: Optional[str] = None
    posts_count: int = 0
    pages_count: int = 0
    target_domains: List[str] = None  # Домены для редиректа
    ad_enabled: bool = False
    auto_content: bool = False
    created_at: str = None
    
    def __post_init__(self):
        if self.target_domains is None:
            self.target_domains = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ContentTemplate:
    """Шаблон контента для автозамены"""
    id: str
    name: str
    content_type: str  # post, page, widget
    template: str  # HTML шаблон с плейсхолдерами
    variables: Dict[str, str]  # Переменные для замены
    redirect_url: Optional[str] = None
    ad_code: Optional[str] = None
    created_at: str = None


class WordPressManager:
    """
    Менеджер WordPress сайтов
    """
    
    def __init__(self):
        self.sites: Dict[str, WPSite] = {}
        self.content_templates: Dict[str, ContentTemplate] = {}
        self.redirect_rules: Dict[str, List[Dict]] = {}
        self.ad_blocks: Dict[str, str] = {}
        
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных"""
        # Сайты
        if SITES_FILE.exists():
            try:
                with open(SITES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for site_data in data:
                        site = WPSite(**site_data)
                        self.sites[site.id] = site
            except Exception as e:
                print(f"Ошибка загрузки сайтов: {e}")
        
        # Шаблоны контента
        if CONTENT_TEMPLATES_FILE.exists():
            try:
                with open(CONTENT_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for tmpl_data in data:
                        tmpl = ContentTemplate(**tmpl_data)
                        self.content_templates[tmpl.id] = tmpl
            except:
                pass
        
        # Правила редиректов
        if REDIRECT_RULES_FILE.exists():
            try:
                with open(REDIRECT_RULES_FILE, 'r', encoding='utf-8') as f:
                    self.redirect_rules = json.load(f)
            except:
                pass
        
        # Рекламные блоки
        if AD_BLOCKS_FILE.exists():
            try:
                with open(AD_BLOCKS_FILE, 'r', encoding='utf-8') as f:
                    self.ad_blocks = json.load(f)
            except:
                pass
    
    def _save_sites(self):
        """Сохранение сайтов"""
        data = [asdict(site) for site in self.sites.values()]
        with open(SITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_templates(self):
        """Сохранение шаблонов"""
        data = [asdict(tmpl) for tmpl in self.content_templates.values()]
        with open(CONTENT_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_redirects(self):
        """Сохранение правил редиректов"""
        with open(REDIRECT_RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.redirect_rules, f, indent=2, ensure_ascii=False)
    
    def _save_ads(self):
        """Сохранение рекламных блоков"""
        with open(AD_BLOCKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.ad_blocks, f, indent=2, ensure_ascii=False)
    
    def _generate_id(self) -> str:
        """Генерация уникального ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{len(self.sites)}".encode()).hexdigest()[:12]
    
    def _encrypt_password(self, password: str) -> str:
        """Простое шифрование пароля (в продакшене использовать Fernet)"""
        return base64.b64encode(password.encode()).decode()
    
    def _decrypt_password(self, encrypted: str) -> str:
        """Расшифровка пароля"""
        return base64.b64decode(encrypted.encode()).decode()
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ САЙТАМИ
    # ═══════════════════════════════════════════════════════════════
    
    def add_site(self, name: str, url: str, username: str, password: str,
                 app_password: Optional[str] = None,
                 connection_type: str = "rest_api") -> Dict:
        """
        Добавление WordPress сайта
        """
        # Нормализация URL
        url = url.rstrip('/')
        if not url.startswith('http'):
            url = f"https://{url}"
        
        admin_url = f"{url}/wp-admin"
        
        site_id = self._generate_id()
        
        site = WPSite(
            id=site_id,
            name=name,
            url=url,
            admin_url=admin_url,
            username=username,
            password=self._encrypt_password(password),
            app_password=self._encrypt_password(app_password) if app_password else None,
            connection_type=connection_type
        )
        
        self.sites[site_id] = site
        self._save_sites()
        
        return {
            "success": True,
            "site_id": site_id,
            "message": f"Сайт {name} добавлен"
        }
    
    def import_sites_bulk(self, sites_data: str, format_type: str = "txt") -> Dict:
        """
        Массовый импорт сайтов
        Формат TXT: url:username:password (по строкам)
        Формат JSON: [{"url": "...", "username": "...", "password": "..."}]
        """
        imported = 0
        errors = []
        
        try:
            if format_type == "txt":
                lines = sites_data.strip().split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(':')
                    if len(parts) >= 3:
                        url = parts[0]
                        username = parts[1]
                        password = ':'.join(parts[2:])  # Пароль может содержать :
                        
                        name = url.replace('https://', '').replace('http://', '').split('/')[0]
                        
                        try:
                            self.add_site(name, url, username, password)
                            imported += 1
                        except Exception as e:
                            errors.append(f"Строка {i+1}: {str(e)}")
                    else:
                        errors.append(f"Строка {i+1}: неверный формат")
            
            elif format_type == "json":
                data = json.loads(sites_data)
                for i, item in enumerate(data):
                    try:
                        url = item.get('url', '')
                        username = item.get('username', '')
                        password = item.get('password', '')
                        name = item.get('name', url.replace('https://', '').replace('http://', '').split('/')[0])
                        app_password = item.get('app_password')
                        
                        self.add_site(name, url, username, password, app_password)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Элемент {i+1}: {str(e)}")
        
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "imported": imported,
            "errors": errors,
            "total_sites": len(self.sites)
        }
    
    def get_sites(self, status: Optional[str] = None) -> List[Dict]:
        """Получение списка сайтов"""
        sites = []
        for site in self.sites.values():
            if status and site.status != status:
                continue
            
            site_dict = asdict(site)
            # Не отдаём пароли
            site_dict['password'] = '***'
            site_dict['app_password'] = '***' if site.app_password else None
            sites.append(site_dict)
        
        return sites
    
    def get_site(self, site_id: str) -> Optional[Dict]:
        """Получение информации о сайте"""
        site = self.sites.get(site_id)
        if not site:
            return None
        
        site_dict = asdict(site)
        site_dict['password'] = '***'
        site_dict['app_password'] = '***' if site.app_password else None
        return site_dict
    
    def delete_site(self, site_id: str) -> Dict:
        """Удаление сайта"""
        if site_id not in self.sites:
            return {"success": False, "error": "Сайт не найден"}
        
        del self.sites[site_id]
        self._save_sites()
        
        return {"success": True, "message": "Сайт удалён"}
    
    def update_site(self, site_id: str, **kwargs) -> Dict:
        """Обновление настроек сайта"""
        if site_id not in self.sites:
            return {"success": False, "error": "Сайт не найден"}
        
        site = self.sites[site_id]
        
        for key, value in kwargs.items():
            if hasattr(site, key):
                if key in ['password', 'app_password'] and value:
                    value = self._encrypt_password(value)
                setattr(site, key, value)
        
        self._save_sites()
        
        return {"success": True, "message": "Сайт обновлён"}
    
    # ═══════════════════════════════════════════════════════════════
    # РАБОТА С WORDPRESS API
    # ═══════════════════════════════════════════════════════════════
    
    async def _get_wp_auth_headers(self, site: WPSite) -> Dict:
        """Получение заголовков авторизации"""
        if site.app_password:
            # Application Password (рекомендуется)
            password = self._decrypt_password(site.app_password)
            credentials = f"{site.username}:{password}"
            token = base64.b64encode(credentials.encode()).decode()
            return {"Authorization": f"Basic {token}"}
        else:
            # Обычный пароль (менее безопасно)
            password = self._decrypt_password(site.password)
            credentials = f"{site.username}:{password}"
            token = base64.b64encode(credentials.encode()).decode()
            return {"Authorization": f"Basic {token}"}
    
    async def test_connection(self, site_id: str) -> Dict:
        """Проверка подключения к сайту"""
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Проверяем REST API
                headers = await self._get_wp_auth_headers(site)
                
                async with session.get(
                    f"{site.url}/wp-json/wp/v2/posts?per_page=1",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                    ssl=False
                ) as response:
                    if response.status == 200:
                        return {
                            "success": True,
                            "message": "Подключение успешно",
                            "api_version": "REST API v2"
                        }
                    elif response.status == 401:
                        return {
                            "success": False,
                            "error": "Ошибка авторизации. Проверьте логин/пароль или создайте Application Password"
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_posts(self, site_id: str, per_page: int = 10, page: int = 1) -> Dict:
        """Получение постов с сайта"""
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = await self._get_wp_auth_headers(site)
                
                async with session.get(
                    f"{site.url}/wp-json/wp/v2/posts",
                    params={"per_page": per_page, "page": page},
                    headers=headers,
                    ssl=False
                ) as response:
                    if response.status == 200:
                        posts = await response.json()
                        total = response.headers.get('X-WP-Total', 0)
                        
                        return {
                            "success": True,
                            "posts": posts,
                            "total": int(total),
                            "page": page,
                            "per_page": per_page
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_post(self, site_id: str, title: str, content: str,
                         status: str = "publish", categories: List[int] = None) -> Dict:
        """Создание поста"""
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = await self._get_wp_auth_headers(site)
                headers["Content-Type"] = "application/json"
                
                data = {
                    "title": title,
                    "content": content,
                    "status": status
                }
                
                if categories:
                    data["categories"] = categories
                
                async with session.post(
                    f"{site.url}/wp-json/wp/v2/posts",
                    json=data,
                    headers=headers,
                    ssl=False
                ) as response:
                    if response.status == 201:
                        post = await response.json()
                        return {
                            "success": True,
                            "post_id": post['id'],
                            "url": post['link'],
                            "message": "Пост создан"
                        }
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_post(self, site_id: str, post_id: int, 
                         title: Optional[str] = None,
                         content: Optional[str] = None,
                         status: Optional[str] = None) -> Dict:
        """Обновление поста"""
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = await self._get_wp_auth_headers(site)
                headers["Content-Type"] = "application/json"
                
                data = {}
                if title:
                    data["title"] = title
                if content:
                    data["content"] = content
                if status:
                    data["status"] = status
                
                async with session.post(
                    f"{site.url}/wp-json/wp/v2/posts/{post_id}",
                    json=data,
                    headers=headers,
                    ssl=False
                ) as response:
                    if response.status == 200:
                        return {"success": True, "message": "Пост обновлён"}
                    else:
                        error = await response.text()
                        return {"success": False, "error": error}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_post(self, site_id: str, post_id: int, force: bool = False) -> Dict:
        """Удаление поста"""
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = await self._get_wp_auth_headers(site)
                
                async with session.delete(
                    f"{site.url}/wp-json/wp/v2/posts/{post_id}",
                    params={"force": force},
                    headers=headers,
                    ssl=False
                ) as response:
                    if response.status == 200:
                        return {"success": True, "message": "Пост удалён"}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # АВТОМАТИЧЕСКАЯ СМЕНА КОНТЕНТА
    # ═══════════════════════════════════════════════════════════════
    
    def add_content_template(self, name: str, content_type: str, 
                            template: str, variables: Dict[str, str],
                            redirect_url: Optional[str] = None,
                            ad_code: Optional[str] = None) -> Dict:
        """Добавление шаблона контента"""
        template_id = self._generate_id()
        
        tmpl = ContentTemplate(
            id=template_id,
            name=name,
            content_type=content_type,
            template=template,
            variables=variables,
            redirect_url=redirect_url,
            ad_code=ad_code,
            created_at=datetime.now().isoformat()
        )
        
        self.content_templates[template_id] = tmpl
        self._save_templates()
        
        return {
            "success": True,
            "template_id": template_id,
            "message": "Шаблон добавлен"
        }
    
    def get_content_templates(self) -> List[Dict]:
        """Получение списка шаблонов"""
        return [asdict(tmpl) for tmpl in self.content_templates.values()]
    
    async def apply_template_to_site(self, site_id: str, template_id: str,
                                    variables: Optional[Dict[str, str]] = None) -> Dict:
        """
        Применение шаблона контента к сайту
        Создаёт или обновляет посты с контентом из шаблона
        """
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        template = self.content_templates.get(template_id)
        if not template:
            return {"success": False, "error": "Шаблон не найден"}
        
        # Подготовка контента
        content = template.template
        
        # Замена переменных
        all_vars = {**template.variables}
        if variables:
            all_vars.update(variables)
        
        for var_name, var_value in all_vars.items():
            content = content.replace(f"{{{{{var_name}}}}}", var_value)
        
        # Добавление рекламного кода
        if template.ad_code:
            content = f"{template.ad_code}\n\n{content}\n\n{template.ad_code}"
        
        # Добавление редиректа (JavaScript)
        if template.redirect_url:
            redirect_script = f"""
<script>
setTimeout(function() {{
    window.location.href = "{template.redirect_url}";
}}, 5000);
</script>
<p style="text-align:center;">Вы будете перенаправлены через 5 секунд... 
<a href="{template.redirect_url}">Нажмите здесь</a> если не хотите ждать.</p>
"""
            content = redirect_script + content
        
        # Создание поста
        result = await self.create_post(
            site_id=site_id,
            title=template.name,
            content=content,
            status="publish"
        )
        
        return result
    
    async def mass_update_content(self, site_id: str, template_id: str,
                                 update_all: bool = False) -> Dict:
        """
        Массовое обновление контента на сайте
        """
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        template = self.content_templates.get(template_id)
        if not template:
            return {"success": False, "error": "Шаблон не найден"}
        
        # Получаем все посты
        posts_result = await self.get_posts(site_id, per_page=100)
        if not posts_result.get("success"):
            return posts_result
        
        posts = posts_result.get("posts", [])
        updated = 0
        errors = []
        
        for post in posts:
            try:
                # Подготовка контента с редиректом и рекламой
                content = template.template
                
                # Добавление рекламы
                if template.ad_code:
                    content = f"{template.ad_code}\n\n{content}\n\n{template.ad_code}"
                
                # Добавление редиректа
                if template.redirect_url:
                    redirect_script = f"""
<script>
setTimeout(function() {{
    window.location.href = "{template.redirect_url}";
}}, 3000);
</script>
"""
                    content = redirect_script + content
                
                result = await self.update_post(
                    site_id=site_id,
                    post_id=post['id'],
                    content=content
                )
                
                if result.get("success"):
                    updated += 1
                else:
                    errors.append(f"Post {post['id']}: {result.get('error')}")
                
                # Небольшая задержка
                await asyncio.sleep(0.5)
            
            except Exception as e:
                errors.append(f"Post {post['id']}: {str(e)}")
        
        return {
            "success": True,
            "updated": updated,
            "total": len(posts),
            "errors": errors
        }
    
    # ═══════════════════════════════════════════════════════════════
    # РЕДИРЕКТЫ И РЕКЛАМА
    # ═══════════════════════════════════════════════════════════════
    
    def add_redirect_rule(self, site_id: str, source_pattern: str, 
                         target_url: str, redirect_type: str = "302") -> Dict:
        """
        Добавление правила редиректа
        """
        if site_id not in self.redirect_rules:
            self.redirect_rules[site_id] = []
        
        rule = {
            "id": self._generate_id(),
            "source_pattern": source_pattern,
            "target_url": target_url,
            "redirect_type": redirect_type,
            "created_at": datetime.now().isoformat()
        }
        
        self.redirect_rules[site_id].append(rule)
        self._save_redirects()
        
        return {"success": True, "rule": rule}
    
    def get_redirect_rules(self, site_id: str) -> List[Dict]:
        """Получение правил редиректа для сайта"""
        return self.redirect_rules.get(site_id, [])
    
    def add_ad_block(self, name: str, code: str) -> Dict:
        """Добавление рекламного блока"""
        ad_id = self._generate_id()
        self.ad_blocks[ad_id] = {
            "name": name,
            "code": code,
            "created_at": datetime.now().isoformat()
        }
        self._save_ads()
        
        return {"success": True, "ad_id": ad_id}
    
    def get_ad_blocks(self) -> Dict:
        """Получение рекламных блоков"""
        return self.ad_blocks
    
    async def inject_ads_to_site(self, site_id: str, ad_id: str, 
                                position: str = "top") -> Dict:
        """
        Внедрение рекламы во все посты сайта
        position: top, bottom, both
        """
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        ad_block = self.ad_blocks.get(ad_id)
        if not ad_block:
            return {"success": False, "error": "Рекламный блок не найден"}
        
        ad_code = ad_block.get("code", "")
        
        # Получаем все посты
        posts_result = await self.get_posts(site_id, per_page=100)
        if not posts_result.get("success"):
            return posts_result
        
        posts = posts_result.get("posts", [])
        updated = 0
        
        for post in posts:
            try:
                current_content = post.get('content', {}).get('rendered', '')
                
                if position == "top":
                    new_content = f"{ad_code}\n\n{current_content}"
                elif position == "bottom":
                    new_content = f"{current_content}\n\n{ad_code}"
                else:  # both
                    new_content = f"{ad_code}\n\n{current_content}\n\n{ad_code}"
                
                result = await self.update_post(
                    site_id=site_id,
                    post_id=post['id'],
                    content=new_content
                )
                
                if result.get("success"):
                    updated += 1
                
                await asyncio.sleep(0.5)
            
            except Exception as e:
                continue
        
        return {
            "success": True,
            "updated": updated,
            "total": len(posts)
        }
    
    # ═══════════════════════════════════════════════════════════════
    # СИНХРОНИЗАЦИЯ И СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    async def sync_site(self, site_id: str) -> Dict:
        """Синхронизация данных сайта"""
        site = self.sites.get(site_id)
        if not site:
            return {"success": False, "error": "Сайт не найден"}
        
        try:
            # Получаем количество постов
            posts_result = await self.get_posts(site_id, per_page=1)
            if posts_result.get("success"):
                site.posts_count = posts_result.get("total", 0)
            
            # Получаем количество страниц
            async with aiohttp.ClientSession() as session:
                headers = await self._get_wp_auth_headers(site)
                
                async with session.get(
                    f"{site.url}/wp-json/wp/v2/pages",
                    params={"per_page": 1},
                    headers=headers,
                    ssl=False
                ) as response:
                    if response.status == 200:
                        site.pages_count = int(response.headers.get('X-WP-Total', 0))
            
            site.last_sync = datetime.now().isoformat()
            site.status = "active"
            self._save_sites()
            
            return {
                "success": True,
                "posts_count": site.posts_count,
                "pages_count": site.pages_count,
                "last_sync": site.last_sync
            }
        
        except Exception as e:
            site.status = "error"
            self._save_sites()
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict:
        """Получение общей статистики"""
        total_sites = len(self.sites)
        active_sites = sum(1 for s in self.sites.values() if s.status == "active")
        total_posts = sum(s.posts_count for s in self.sites.values())
        total_pages = sum(s.pages_count for s in self.sites.values())
        
        return {
            "total_sites": total_sites,
            "active_sites": active_sites,
            "error_sites": total_sites - active_sites,
            "total_posts": total_posts,
            "total_pages": total_pages,
            "content_templates": len(self.content_templates),
            "ad_blocks": len(self.ad_blocks)
        }


# Singleton
_wordpress_manager = None

def get_wordpress_manager() -> WordPressManager:
    """Получение экземпляра WordPress Manager"""
    global _wordpress_manager
    if _wordpress_manager is None:
        _wordpress_manager = WordPressManager()
    return _wordpress_manager
