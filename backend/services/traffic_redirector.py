"""
SEO Monster - Traffic Redirector
Система управления трафиком и редиректами

Возможности:
- Централизованное управление редиректами
- Автоматическое перенаправление трафика
- Ротация целевых доменов
- Статистика переходов
- Интеграция с WordPress и cPanel
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib
import random

# Импорт менеджеров
from services.wordpress_manager import get_wordpress_manager
from services.cpanel_manager import get_cpanel_manager

# Пути
DATA_DIR = Path("/home/ubuntu/seo_monster/backend/data/traffic")
DATA_DIR.mkdir(parents=True, exist_ok=True)

CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"
STATS_FILE = DATA_DIR / "stats.json"
ROTATION_FILE = DATA_DIR / "rotation.json"


@dataclass
class RedirectCampaign:
    """Кампания редиректов"""
    id: str
    name: str
    source_type: str  # wordpress, cpanel, both
    source_ids: List[str]  # ID сайтов/аккаунтов
    target_urls: List[str]  # Целевые URL для редиректа
    redirect_type: str  # 301, 302, js, meta
    rotation_mode: str  # single, random, weighted, sequential
    weights: Optional[Dict[str, int]] = None  # Веса для weighted ротации
    geo_targeting: Optional[Dict[str, str]] = None  # Гео-таргетинг
    device_targeting: Optional[Dict[str, str]] = None  # Таргетинг по устройствам
    schedule: Optional[Dict] = None  # Расписание
    status: str = "active"
    clicks: int = 0
    last_click: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.weights is None:
            self.weights = {}


class TrafficRedirector:
    """
    Система управления трафиком
    """
    
    def __init__(self):
        self.campaigns: Dict[str, RedirectCampaign] = {}
        self.stats: Dict[str, Dict] = {}
        self.rotation_state: Dict[str, int] = {}  # Для sequential ротации
        
        self.wp_manager = get_wordpress_manager()
        self.cpanel_manager = get_cpanel_manager()
        
        self._load_data()
    
    def _load_data(self):
        """Загрузка данных"""
        if CAMPAIGNS_FILE.exists():
            try:
                with open(CAMPAIGNS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for camp_data in data:
                        camp = RedirectCampaign(**camp_data)
                        self.campaigns[camp.id] = camp
            except Exception as e:
                print(f"Ошибка загрузки кампаний: {e}")
        
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except:
                pass
        
        if ROTATION_FILE.exists():
            try:
                with open(ROTATION_FILE, 'r', encoding='utf-8') as f:
                    self.rotation_state = json.load(f)
            except:
                pass
    
    def _save_campaigns(self):
        """Сохранение кампаний"""
        data = [asdict(camp) for camp in self.campaigns.values()]
        with open(CAMPAIGNS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_stats(self):
        """Сохранение статистики"""
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def _save_rotation(self):
        """Сохранение состояния ротации"""
        with open(ROTATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.rotation_state, f, indent=2, ensure_ascii=False)
    
    def _generate_id(self) -> str:
        """Генерация уникального ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{len(self.campaigns)}".encode()).hexdigest()[:12]
    
    # ═══════════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ КАМПАНИЯМИ
    # ═══════════════════════════════════════════════════════════════
    
    def create_campaign(self, name: str, source_type: str, source_ids: List[str],
                       target_urls: List[str], redirect_type: str = "301",
                       rotation_mode: str = "single",
                       weights: Optional[Dict[str, int]] = None,
                       geo_targeting: Optional[Dict[str, str]] = None,
                       device_targeting: Optional[Dict[str, str]] = None) -> Dict:
        """
        Создание кампании редиректов
        """
        campaign_id = self._generate_id()
        
        campaign = RedirectCampaign(
            id=campaign_id,
            name=name,
            source_type=source_type,
            source_ids=source_ids,
            target_urls=target_urls,
            redirect_type=redirect_type,
            rotation_mode=rotation_mode,
            weights=weights,
            geo_targeting=geo_targeting,
            device_targeting=device_targeting
        )
        
        self.campaigns[campaign_id] = campaign
        self._save_campaigns()
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "message": f"Кампания '{name}' создана"
        }
    
    def get_campaigns(self, status: Optional[str] = None) -> List[Dict]:
        """Получение списка кампаний"""
        campaigns = []
        for camp in self.campaigns.values():
            if status and camp.status != status:
                continue
            campaigns.append(asdict(camp))
        return campaigns
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict]:
        """Получение информации о кампании"""
        camp = self.campaigns.get(campaign_id)
        return asdict(camp) if camp else None
    
    def update_campaign(self, campaign_id: str, **kwargs) -> Dict:
        """Обновление кампании"""
        if campaign_id not in self.campaigns:
            return {"success": False, "error": "Кампания не найдена"}
        
        camp = self.campaigns[campaign_id]
        
        for key, value in kwargs.items():
            if hasattr(camp, key):
                setattr(camp, key, value)
        
        self._save_campaigns()
        
        return {"success": True, "message": "Кампания обновлена"}
    
    def delete_campaign(self, campaign_id: str) -> Dict:
        """Удаление кампании"""
        if campaign_id not in self.campaigns:
            return {"success": False, "error": "Кампания не найдена"}
        
        del self.campaigns[campaign_id]
        self._save_campaigns()
        
        return {"success": True, "message": "Кампания удалена"}
    
    # ═══════════════════════════════════════════════════════════════
    # РОТАЦИЯ URL
    # ═══════════════════════════════════════════════════════════════
    
    def get_target_url(self, campaign_id: str, 
                      geo: Optional[str] = None,
                      device: Optional[str] = None) -> Optional[str]:
        """
        Получение целевого URL с учётом ротации и таргетинга
        """
        camp = self.campaigns.get(campaign_id)
        if not camp or not camp.target_urls:
            return None
        
        # Гео-таргетинг
        if geo and camp.geo_targeting and geo in camp.geo_targeting:
            return camp.geo_targeting[geo]
        
        # Таргетинг по устройствам
        if device and camp.device_targeting and device in camp.device_targeting:
            return camp.device_targeting[device]
        
        # Ротация
        if camp.rotation_mode == "single" or len(camp.target_urls) == 1:
            return camp.target_urls[0]
        
        elif camp.rotation_mode == "random":
            return random.choice(camp.target_urls)
        
        elif camp.rotation_mode == "weighted" and camp.weights:
            # Взвешенный выбор
            urls = []
            weights = []
            for url in camp.target_urls:
                urls.append(url)
                weights.append(camp.weights.get(url, 1))
            
            return random.choices(urls, weights=weights)[0]
        
        elif camp.rotation_mode == "sequential":
            # Последовательная ротация
            current_idx = self.rotation_state.get(campaign_id, 0)
            url = camp.target_urls[current_idx % len(camp.target_urls)]
            
            self.rotation_state[campaign_id] = current_idx + 1
            self._save_rotation()
            
            return url
        
        return camp.target_urls[0]
    
    # ═══════════════════════════════════════════════════════════════
    # ГЕНЕРАЦИЯ КОДА РЕДИРЕКТА
    # ═══════════════════════════════════════════════════════════════
    
    def generate_redirect_code(self, campaign_id: str, 
                              code_type: Optional[str] = None) -> Dict:
        """
        Генерация кода редиректа для разных платформ
        """
        camp = self.campaigns.get(campaign_id)
        if not camp:
            return {"success": False, "error": "Кампания не найдена"}
        
        redirect_type = code_type or camp.redirect_type
        target_url = camp.target_urls[0] if camp.target_urls else ""
        
        codes = {}
        
        # .htaccess код
        if redirect_type in ["301", "302"]:
            codes["htaccess"] = f"""# SEO Monster Redirect - Campaign: {camp.name}
RewriteEngine On
RewriteRule ^(.*)$ {target_url} [R={redirect_type},L]
"""
        
        # JavaScript редирект
        codes["javascript"] = f"""<!-- SEO Monster Redirect - Campaign: {camp.name} -->
<script>
(function() {{
    var targets = {json.dumps(camp.target_urls)};
    var mode = "{camp.rotation_mode}";
    var url;
    
    if (mode === "random") {{
        url = targets[Math.floor(Math.random() * targets.length)];
    }} else if (mode === "sequential") {{
        var idx = parseInt(localStorage.getItem('seo_monster_idx') || '0');
        url = targets[idx % targets.length];
        localStorage.setItem('seo_monster_idx', idx + 1);
    }} else {{
        url = targets[0];
    }}
    
    setTimeout(function() {{
        window.location.href = url;
    }}, 100);
}})();
</script>
"""
        
        # Meta refresh
        codes["meta"] = f"""<!-- SEO Monster Redirect - Campaign: {camp.name} -->
<meta http-equiv="refresh" content="0;url={target_url}">
<script>window.location.href = "{target_url}";</script>
"""
        
        # PHP код
        codes["php"] = f"""<?php
// SEO Monster Redirect - Campaign: {camp.name}
$targets = {json.dumps(camp.target_urls)};
$mode = "{camp.rotation_mode}";

if ($mode === "random") {{
    $url = $targets[array_rand($targets)];
}} else {{
    $url = $targets[0];
}}

header("Location: $url", true, {redirect_type});
exit();
?>
"""
        
        # WordPress код (для functions.php или плагина)
        codes["wordpress"] = f"""<?php
// SEO Monster Redirect - Campaign: {camp.name}
// Добавьте в functions.php вашей темы

add_action('template_redirect', function() {{
    $targets = array({', '.join([f'"{u}"' for u in camp.target_urls])});
    $mode = "{camp.rotation_mode}";
    
    if ($mode === "random") {{
        $url = $targets[array_rand($targets)];
    }} else {{
        $url = $targets[0];
    }}
    
    wp_redirect($url, {redirect_type});
    exit();
}});
?>
"""
        
        return {
            "success": True,
            "codes": codes,
            "campaign": camp.name
        }
    
    # ═══════════════════════════════════════════════════════════════
    # ПРИМЕНЕНИЕ РЕДИРЕКТОВ
    # ═══════════════════════════════════════════════════════════════
    
    async def apply_campaign(self, campaign_id: str) -> Dict:
        """
        Применение кампании редиректов ко всем источникам
        """
        camp = self.campaigns.get(campaign_id)
        if not camp:
            return {"success": False, "error": "Кампания не найдена"}
        
        results = {
            "wordpress": {"success": 0, "failed": 0, "errors": []},
            "cpanel": {"success": 0, "failed": 0, "errors": []}
        }
        
        target_url = camp.target_urls[0] if camp.target_urls else ""
        
        # Применяем к WordPress сайтам
        if camp.source_type in ["wordpress", "both"]:
            for site_id in camp.source_ids:
                try:
                    # Генерируем код редиректа
                    codes = self.generate_redirect_code(campaign_id)
                    js_code = codes.get("codes", {}).get("javascript", "")
                    
                    # Создаём шаблон с редиректом
                    template_result = self.wp_manager.add_content_template(
                        name=f"Redirect - {camp.name}",
                        content_type="post",
                        template=f"<p>Перенаправление...</p>",
                        variables={},
                        redirect_url=target_url
                    )
                    
                    if template_result.get("success"):
                        # Применяем к сайту
                        apply_result = await self.wp_manager.mass_update_content(
                            site_id=site_id,
                            template_id=template_result.get("template_id")
                        )
                        
                        if apply_result.get("success"):
                            results["wordpress"]["success"] += 1
                        else:
                            results["wordpress"]["failed"] += 1
                            results["wordpress"]["errors"].append(
                                f"Site {site_id}: {apply_result.get('error')}"
                            )
                    else:
                        results["wordpress"]["failed"] += 1
                
                except Exception as e:
                    results["wordpress"]["failed"] += 1
                    results["wordpress"]["errors"].append(f"Site {site_id}: {str(e)}")
        
        # Применяем к cPanel аккаунтам
        if camp.source_type in ["cpanel", "both"]:
            for account_id in camp.source_ids:
                try:
                    result = await self.cpanel_manager.setup_redirect(
                        account_id=account_id,
                        target_url=target_url,
                        redirect_type=camp.redirect_type
                    )
                    
                    if result.get("success"):
                        results["cpanel"]["success"] += 1
                    else:
                        results["cpanel"]["failed"] += 1
                        results["cpanel"]["errors"].append(
                            f"Account {account_id}: {result.get('error')}"
                        )
                
                except Exception as e:
                    results["cpanel"]["failed"] += 1
                    results["cpanel"]["errors"].append(f"Account {account_id}: {str(e)}")
        
        # Обновляем статус кампании
        camp.status = "applied"
        self._save_campaigns()
        
        return {
            "success": True,
            "results": results,
            "message": "Кампания применена"
        }
    
    async def remove_campaign_redirects(self, campaign_id: str) -> Dict:
        """
        Удаление редиректов кампании со всех источников
        """
        camp = self.campaigns.get(campaign_id)
        if not camp:
            return {"success": False, "error": "Кампания не найдена"}
        
        results = {"success": 0, "failed": 0, "errors": []}
        
        # Для cPanel - очищаем .htaccess
        if camp.source_type in ["cpanel", "both"]:
            for account_id in camp.source_ids:
                try:
                    # Записываем пустой .htaccess
                    result = await self.cpanel_manager.update_htaccess(
                        account_id=account_id,
                        content="# Cleaned by SEO Monster"
                    )
                    
                    if result.get("success"):
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Account {account_id}: {result.get('error')}")
                
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Account {account_id}: {str(e)}")
        
        camp.status = "inactive"
        self._save_campaigns()
        
        return {
            "success": True,
            "results": results,
            "message": "Редиректы удалены"
        }
    
    # ═══════════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════════
    
    def record_click(self, campaign_id: str, 
                    source_url: Optional[str] = None,
                    target_url: Optional[str] = None,
                    geo: Optional[str] = None,
                    device: Optional[str] = None,
                    referrer: Optional[str] = None):
        """Запись клика/перехода"""
        camp = self.campaigns.get(campaign_id)
        if not camp:
            return
        
        # Обновляем счётчик кампании
        camp.clicks += 1
        camp.last_click = datetime.now().isoformat()
        self._save_campaigns()
        
        # Записываем детальную статистику
        today = datetime.now().strftime("%Y-%m-%d")
        
        if campaign_id not in self.stats:
            self.stats[campaign_id] = {}
        
        if today not in self.stats[campaign_id]:
            self.stats[campaign_id][today] = {
                "clicks": 0,
                "by_geo": {},
                "by_device": {},
                "by_target": {},
                "by_hour": {}
            }
        
        day_stats = self.stats[campaign_id][today]
        day_stats["clicks"] += 1
        
        if geo:
            day_stats["by_geo"][geo] = day_stats["by_geo"].get(geo, 0) + 1
        
        if device:
            day_stats["by_device"][device] = day_stats["by_device"].get(device, 0) + 1
        
        if target_url:
            day_stats["by_target"][target_url] = day_stats["by_target"].get(target_url, 0) + 1
        
        hour = datetime.now().strftime("%H")
        day_stats["by_hour"][hour] = day_stats["by_hour"].get(hour, 0) + 1
        
        self._save_stats()
    
    def get_campaign_stats(self, campaign_id: str, 
                          days: int = 7) -> Dict:
        """Получение статистики кампании"""
        camp = self.campaigns.get(campaign_id)
        if not camp:
            return {"success": False, "error": "Кампания не найдена"}
        
        campaign_stats = self.stats.get(campaign_id, {})
        
        # Собираем статистику за период
        total_clicks = 0
        by_day = {}
        by_geo = {}
        by_device = {}
        by_target = {}
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_data = campaign_stats.get(date, {})
            
            clicks = day_data.get("clicks", 0)
            total_clicks += clicks
            by_day[date] = clicks
            
            for geo, count in day_data.get("by_geo", {}).items():
                by_geo[geo] = by_geo.get(geo, 0) + count
            
            for device, count in day_data.get("by_device", {}).items():
                by_device[device] = by_device.get(device, 0) + count
            
            for target, count in day_data.get("by_target", {}).items():
                by_target[target] = by_target.get(target, 0) + count
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "campaign_name": camp.name,
            "period_days": days,
            "total_clicks": total_clicks,
            "all_time_clicks": camp.clicks,
            "by_day": by_day,
            "by_geo": by_geo,
            "by_device": by_device,
            "by_target": by_target
        }
    
    def get_overall_stats(self) -> Dict:
        """Общая статистика по всем кампаниям"""
        total_campaigns = len(self.campaigns)
        active_campaigns = sum(1 for c in self.campaigns.values() if c.status == "active")
        applied_campaigns = sum(1 for c in self.campaigns.values() if c.status == "applied")
        total_clicks = sum(c.clicks for c in self.campaigns.values())
        
        # Топ кампании
        top_campaigns = sorted(
            self.campaigns.values(),
            key=lambda c: c.clicks,
            reverse=True
        )[:5]
        
        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "applied_campaigns": applied_campaigns,
            "total_clicks": total_clicks,
            "top_campaigns": [
                {"id": c.id, "name": c.name, "clicks": c.clicks}
                for c in top_campaigns
            ]
        }


# Singleton
_traffic_redirector = None

def get_traffic_redirector() -> TrafficRedirector:
    """Получение экземпляра Traffic Redirector"""
    global _traffic_redirector
    if _traffic_redirector is None:
        _traffic_redirector = TrafficRedirector()
    return _traffic_redirector
