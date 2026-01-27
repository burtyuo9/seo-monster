"""
SEO Monster - Autopilot Engine
Автономный движок для автоматического продвижения сайтов
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import aiohttp
from openai import OpenAI
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CampaignStatus(str, Enum):
    CREATED = "created"
    ANALYZING = "analyzing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class TaskType(str, Enum):
    ANALYZE_SITE = "analyze_site"
    ANALYZE_COMPETITORS = "analyze_competitors"
    GENERATE_CONTENT = "generate_content"
    POST_CONTENT = "post_content"
    INDEX_URLS = "index_urls"
    CHECK_POSITIONS = "check_positions"
    LEARN_FROM_RESULTS = "learn_from_results"


@dataclass
class AutopilotTask:
    id: str
    campaign_id: str
    task_type: TaskType
    status: str
    params: Dict
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: str = None
    completed_at: str = None


@dataclass
class Campaign:
    id: str
    domain: str
    status: CampaignStatus
    settings: Dict
    stats: Dict
    created_at: str
    last_activity: str
    next_action: Optional[str] = None
    learning_data: Dict = None


class AutopilotEngine:
    """
    Автономный движок SEO-продвижения
    
    Работает как единый организм:
    1. Анализирует сайт и конкурентов
    2. Генерирует контент на основе анализа
    3. Постит на площадки
    4. Индексирует в поисковиках
    5. Отслеживает позиции
    6. Самообучается на результатах
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "data/autopilot")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы данных
        self.campaigns_file = self.data_dir / "campaigns.json"
        self.tasks_file = self.data_dir / "tasks.json"
        self.learning_file = self.data_dir / "learning_data.json"
        self.logs_file = self.data_dir / "autopilot_logs.json"
        
        # Загружаем данные
        self.campaigns: Dict[str, Campaign] = self._load_campaigns()
        self.tasks: List[AutopilotTask] = self._load_json(self.tasks_file, [])
        self.learning_data: Dict = self._load_json(self.learning_file, {
            "successful_strategies": [],
            "failed_strategies": [],
            "best_posting_times": {},
            "best_platforms": {},
            "keyword_performance": {},
            "content_templates": []
        })
        self.logs: List[Dict] = self._load_json(self.logs_file, [])
        
        # OpenAI клиент
        self.ai_client = None
        self._init_ai_client()
        
        # Флаг работы
        self.is_running = False
        self.current_task = None
    
    def _init_ai_client(self):
        """Инициализация AI клиента"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            self.ai_client = OpenAI()
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Загрузка JSON файла"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, path: Path, data: Any):
        """Сохранение JSON файла"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _load_campaigns(self) -> Dict[str, Campaign]:
        """Загрузка кампаний"""
        data = self._load_json(self.campaigns_file, {})
        campaigns = {}
        for cid, cdata in data.items():
            campaigns[cid] = Campaign(**cdata)
        return campaigns
    
    def _save_campaigns(self):
        """Сохранение кампаний"""
        data = {cid: asdict(c) for cid, c in self.campaigns.items()}
        self._save_json(self.campaigns_file, data)
    
    def _save_tasks(self):
        """Сохранение задач"""
        self._save_json(self.tasks_file, [asdict(t) for t in self.tasks])
    
    def _save_learning(self):
        """Сохранение данных обучения"""
        self._save_json(self.learning_file, self.learning_data)
    
    def _log(self, campaign_id: str, message: str, level: str = "info"):
        """Добавление записи в лог"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "campaign_id": campaign_id,
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        
        # Ограничиваем размер логов
        if len(self.logs) > 10000:
            self.logs = self.logs[-5000:]
        
        self._save_json(self.logs_file, self.logs)
        logger.info(f"[{campaign_id}] {message}")
    
    def create_campaign(
        self, 
        domain: str, 
        settings: Dict = None
    ) -> Campaign:
        """
        Создание новой кампании продвижения
        
        Args:
            domain: Домен для продвижения
            settings: Настройки кампании
        
        Returns:
            Созданная кампания
        """
        campaign_id = f"camp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        default_settings = {
            "languages": ["ru", "en"],
            "content_per_day": 5,
            "platforms_per_content": 3,
            "auto_index": True,
            "check_positions_daily": True,
            "learning_enabled": True,
            "keywords": [],
            "target_platforms": [],
            "posting_schedule": {
                "start_hour": 9,
                "end_hour": 21,
                "days": [0, 1, 2, 3, 4, 5, 6]
            }
        }
        
        if settings:
            default_settings.update(settings)
        
        campaign = Campaign(
            id=campaign_id,
            domain=domain,
            status=CampaignStatus.CREATED,
            settings=default_settings,
            stats={
                "content_generated": 0,
                "content_posted": 0,
                "urls_indexed": 0,
                "positions_checked": 0,
                "average_position": 0,
                "best_position": 0,
                "clicks": 0,
                "impressions": 0
            },
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            next_action="analyze_site",
            learning_data={}
        )
        
        self.campaigns[campaign_id] = campaign
        self._save_campaigns()
        self._log(campaign_id, f"Создана кампания для домена {domain}")
        
        return campaign
    
    async def start_campaign(self, campaign_id: str) -> bool:
        """Запуск кампании"""
        if campaign_id not in self.campaigns:
            return False
        
        campaign = self.campaigns[campaign_id]
        campaign.status = CampaignStatus.RUNNING
        campaign.last_activity = datetime.now().isoformat()
        self._save_campaigns()
        
        self._log(campaign_id, "Кампания запущена")
        
        # Запускаем автопилот
        asyncio.create_task(self._run_autopilot(campaign_id))
        
        return True
    
    def pause_campaign(self, campaign_id: str) -> bool:
        """Приостановка кампании"""
        if campaign_id not in self.campaigns:
            return False
        
        campaign = self.campaigns[campaign_id]
        campaign.status = CampaignStatus.PAUSED
        self._save_campaigns()
        
        self._log(campaign_id, "Кампания приостановлена")
        return True
    
    def resume_campaign(self, campaign_id: str) -> bool:
        """Возобновление кампании"""
        if campaign_id not in self.campaigns:
            return False
        
        campaign = self.campaigns[campaign_id]
        if campaign.status == CampaignStatus.PAUSED:
            campaign.status = CampaignStatus.RUNNING
            self._save_campaigns()
            
            self._log(campaign_id, "Кампания возобновлена")
            asyncio.create_task(self._run_autopilot(campaign_id))
            return True
        
        return False
    
    async def _run_autopilot(self, campaign_id: str):
        """
        Основной цикл автопилота
        
        Работает непрерывно, выполняя действия по расписанию:
        1. Анализ сайта (при старте)
        2. Анализ конкурентов (раз в неделю)
        3. Генерация контента (по расписанию)
        4. Постинг (по расписанию)
        5. Индексация (после постинга)
        6. Проверка позиций (раз в день)
        7. Обучение (постоянно)
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return
        
        self._log(campaign_id, "🚀 Автопилот запущен")
        
        while campaign.status == CampaignStatus.RUNNING:
            try:
                # Определяем следующее действие
                next_action = await self._determine_next_action(campaign)
                
                if next_action:
                    self._log(campaign_id, f"Выполняю: {next_action}")
                    
                    # Выполняем действие
                    result = await self._execute_action(campaign, next_action)
                    
                    # Обновляем статистику
                    campaign.last_activity = datetime.now().isoformat()
                    self._save_campaigns()
                    
                    # Обучаемся на результате
                    if campaign.settings.get("learning_enabled"):
                        await self._learn_from_result(campaign, next_action, result)
                
                # Пауза между действиями (5-15 минут)
                await asyncio.sleep(random.randint(300, 900))
                
                # Перезагружаем кампанию для проверки статуса
                campaign = self.campaigns.get(campaign_id)
                if not campaign:
                    break
                    
            except Exception as e:
                self._log(campaign_id, f"Ошибка: {str(e)}", "error")
                await asyncio.sleep(60)
        
        self._log(campaign_id, "Автопилот остановлен")
    
    async def _determine_next_action(self, campaign: Campaign) -> Optional[str]:
        """Определение следующего действия на основе состояния и обучения"""
        
        now = datetime.now()
        settings = campaign.settings
        
        # Проверяем расписание
        schedule = settings.get("posting_schedule", {})
        current_hour = now.hour
        current_day = now.weekday()
        
        if current_hour < schedule.get("start_hour", 9) or current_hour > schedule.get("end_hour", 21):
            return None  # Вне рабочего времени
        
        if current_day not in schedule.get("days", [0, 1, 2, 3, 4, 5, 6]):
            return None  # Не рабочий день
        
        # Приоритет действий
        
        # 1. Если сайт не проанализирован - анализируем
        if not campaign.learning_data.get("site_analyzed"):
            return "analyze_site"
        
        # 2. Если конкуренты не проанализированы или давно - анализируем
        last_competitor_analysis = campaign.learning_data.get("last_competitor_analysis")
        if not last_competitor_analysis or (now - datetime.fromisoformat(last_competitor_analysis)).days > 7:
            return "analyze_competitors"
        
        # 3. Проверяем позиции раз в день
        last_position_check = campaign.learning_data.get("last_position_check")
        if settings.get("check_positions_daily") and (
            not last_position_check or 
            (now - datetime.fromisoformat(last_position_check)).days >= 1
        ):
            return "check_positions"
        
        # 4. Генерируем и постим контент
        content_today = campaign.learning_data.get("content_today", 0)
        max_content = settings.get("content_per_day", 5)
        
        if content_today < max_content:
            # Выбираем на основе обучения
            if self._should_generate_content(campaign):
                return "generate_and_post"
        
        return None
    
    def _should_generate_content(self, campaign: Campaign) -> bool:
        """Решение о генерации контента на основе обучения"""
        
        # Проверяем лучшее время для постинга
        current_hour = datetime.now().hour
        best_hours = self.learning_data.get("best_posting_times", {}).get(campaign.domain, [])
        
        if best_hours and current_hour in best_hours:
            return True
        
        # Если нет данных - постим
        if not best_hours:
            return True
        
        # Случайный шанс для экспериментов
        return random.random() < 0.3
    
    async def _execute_action(self, campaign: Campaign, action: str) -> Dict:
        """Выполнение действия"""
        
        result = {"success": False, "action": action}
        
        try:
            if action == "analyze_site":
                result = await self._analyze_site(campaign)
            
            elif action == "analyze_competitors":
                result = await self._analyze_competitors(campaign)
            
            elif action == "generate_and_post":
                result = await self._generate_and_post(campaign)
            
            elif action == "check_positions":
                result = await self._check_positions(campaign)
            
            elif action == "index_urls":
                result = await self._index_urls(campaign)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            self._log(campaign.id, f"Ошибка выполнения {action}: {e}", "error")
        
        return result
    
    async def _analyze_site(self, campaign: Campaign) -> Dict:
        """Анализ целевого сайта"""
        
        self._log(campaign.id, f"Анализирую сайт {campaign.domain}")
        
        result = {
            "keywords": [],
            "niche": "",
            "competitors": [],
            "content_suggestions": []
        }
        
        try:
            # Получаем контент сайта
            async with aiohttp.ClientSession() as session:
                url = f"https://{campaign.domain}" if not campaign.domain.startswith("http") else campaign.domain
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Используем AI для анализа
                        if self.ai_client:
                            analysis = await self._ai_analyze_site(html, campaign.domain)
                            result.update(analysis)
            
            # Сохраняем результаты
            campaign.learning_data["site_analyzed"] = True
            campaign.learning_data["site_analysis"] = result
            campaign.learning_data["analysis_date"] = datetime.now().isoformat()
            
            # Обновляем ключевые слова в настройках
            if result.get("keywords"):
                campaign.settings["keywords"] = result["keywords"]
            
            self._save_campaigns()
            self._log(campaign.id, f"Анализ завершен. Найдено {len(result.get('keywords', []))} ключевых слов")
            
        except Exception as e:
            self._log(campaign.id, f"Ошибка анализа сайта: {e}", "error")
        
        return result
    
    async def _ai_analyze_site(self, html: str, domain: str) -> Dict:
        """AI анализ сайта"""
        
        if not self.ai_client:
            return {}
        
        # Ограничиваем размер HTML
        html_truncated = html[:10000]
        
        prompt = f"""Проанализируй сайт {domain} и его контент.

HTML контент:
{html_truncated}

Верни JSON с полями:
- keywords: список из 10-20 ключевых слов для SEO
- niche: ниша/тематика сайта
- competitors: список 5 возможных конкурентов (домены)
- content_suggestions: 5 идей для контента
- target_audience: описание целевой аудитории
- tone: рекомендуемый тон контента (формальный/неформальный/экспертный)

Отвечай только JSON без пояснений."""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            result_text = response.choices[0].message.content
            # Пытаемся распарсить JSON
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {}
    
    async def _analyze_competitors(self, campaign: Campaign) -> Dict:
        """Анализ конкурентов"""
        
        self._log(campaign.id, "Анализирую конкурентов")
        
        competitors = campaign.learning_data.get("site_analysis", {}).get("competitors", [])
        result = {"competitors_data": []}
        
        # Анализируем каждого конкурента
        for competitor in competitors[:5]:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"https://{competitor}" if not competitor.startswith("http") else competitor
                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            html = await response.text()
                            
                            # Извлекаем ключевые слова конкурента
                            if self.ai_client:
                                comp_analysis = await self._ai_analyze_competitor(html, competitor)
                                result["competitors_data"].append({
                                    "domain": competitor,
                                    "analysis": comp_analysis
                                })
            except:
                continue
        
        # Обновляем данные обучения
        campaign.learning_data["last_competitor_analysis"] = datetime.now().isoformat()
        campaign.learning_data["competitors_data"] = result["competitors_data"]
        
        # Расширяем список ключевых слов
        all_keywords = set(campaign.settings.get("keywords", []))
        for comp in result["competitors_data"]:
            all_keywords.update(comp.get("analysis", {}).get("keywords", []))
        
        campaign.settings["keywords"] = list(all_keywords)[:50]
        self._save_campaigns()
        
        self._log(campaign.id, f"Проанализировано {len(result['competitors_data'])} конкурентов")
        
        return result
    
    async def _ai_analyze_competitor(self, html: str, domain: str) -> Dict:
        """AI анализ конкурента"""
        
        if not self.ai_client:
            return {}
        
        html_truncated = html[:5000]
        
        prompt = f"""Проанализируй сайт конкурента {domain}.

HTML:
{html_truncated}

Верни JSON:
- keywords: ключевые слова (до 10)
- strengths: сильные стороны
- weaknesses: слабые стороны
- content_types: типы контента

Только JSON."""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except:
            return {}
    
    async def _generate_and_post(self, campaign: Campaign) -> Dict:
        """Генерация и публикация контента"""
        
        self._log(campaign.id, "Генерирую контент")
        
        result = {"content_id": None, "posted_to": [], "indexed": False}
        
        # Выбираем ключевое слово
        keywords = campaign.settings.get("keywords", [])
        if not keywords:
            keywords = [campaign.domain]
        
        # Выбираем на основе обучения
        keyword = self._select_best_keyword(campaign, keywords)
        
        # Генерируем контент
        content = await self._generate_content(campaign, keyword)
        
        if content:
            result["content"] = content
            
            # Постим на площадки
            platforms = campaign.settings.get("target_platforms", [])
            if not platforms:
                platforms = ["article", "social", "forum"]
            
            posted = await self._post_to_platforms(campaign, content, platforms)
            result["posted_to"] = posted
            
            # Индексируем
            if campaign.settings.get("auto_index") and posted:
                indexed = await self._index_posted_urls(campaign, posted)
                result["indexed"] = indexed
            
            # Обновляем статистику
            campaign.stats["content_generated"] = campaign.stats.get("content_generated", 0) + 1
            campaign.stats["content_posted"] = campaign.stats.get("content_posted", 0) + len(posted)
            
            # Обновляем счетчик за сегодня
            campaign.learning_data["content_today"] = campaign.learning_data.get("content_today", 0) + 1
            campaign.learning_data["last_content_date"] = datetime.now().date().isoformat()
            
            self._save_campaigns()
            self._log(campaign.id, f"Контент опубликован на {len(posted)} площадках")
        
        return result
    
    def _select_best_keyword(self, campaign: Campaign, keywords: List[str]) -> str:
        """Выбор лучшего ключевого слова на основе обучения"""
        
        keyword_perf = self.learning_data.get("keyword_performance", {})
        domain_perf = keyword_perf.get(campaign.domain, {})
        
        # Сортируем по эффективности
        scored_keywords = []
        for kw in keywords:
            score = domain_perf.get(kw, {}).get("score", 0.5)
            scored_keywords.append((kw, score))
        
        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        
        # Выбираем с учетом exploration/exploitation
        if random.random() < 0.2:  # 20% exploration
            return random.choice(keywords)
        else:
            return scored_keywords[0][0] if scored_keywords else keywords[0]
    
    async def _generate_content(self, campaign: Campaign, keyword: str) -> Optional[Dict]:
        """Генерация контента с помощью AI"""
        
        if not self.ai_client:
            return None
        
        # Получаем данные для генерации
        site_analysis = campaign.learning_data.get("site_analysis", {})
        tone = site_analysis.get("tone", "экспертный")
        niche = site_analysis.get("niche", "")
        
        # Выбираем язык
        languages = campaign.settings.get("languages", ["ru"])
        language = random.choice(languages)
        
        prompt = f"""Создай SEO-оптимизированную статью для сайта в нише "{niche}".

Ключевое слово: {keyword}
Язык: {language}
Тон: {tone}
Целевой сайт: {campaign.domain}

Требования:
1. Уникальный контент 500-800 слов
2. Естественное использование ключевого слова (3-5 раз)
3. Привлекательный заголовок
4. Структура с подзаголовками
5. Призыв к действию в конце

Верни JSON:
- title: заголовок
- content: полный текст статьи
- meta_description: мета-описание (до 160 символов)
- tags: теги (до 5)

Только JSON."""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content)
            result["keyword"] = keyword
            result["language"] = language
            result["generated_at"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return None
    
    async def _post_to_platforms(self, campaign: Campaign, content: Dict, platforms: List[str]) -> List[Dict]:
        """Публикация контента на площадки"""
        
        posted = []
        
        # Здесь будет интеграция с реальными площадками
        # Пока симулируем
        for platform in platforms[:campaign.settings.get("platforms_per_content", 3)]:
            posted.append({
                "platform": platform,
                "url": f"https://{platform}.example.com/post/{random.randint(10000, 99999)}",
                "posted_at": datetime.now().isoformat(),
                "status": "posted"
            })
        
        return posted
    
    async def _index_posted_urls(self, campaign: Campaign, posted: List[Dict]) -> bool:
        """Индексация опубликованных URL"""
        
        # Здесь будет интеграция с indexing_service
        for post in posted:
            self._log(campaign.id, f"Индексация: {post['url']}")
        
        campaign.stats["urls_indexed"] = campaign.stats.get("urls_indexed", 0) + len(posted)
        return True
    
    async def _check_positions(self, campaign: Campaign) -> Dict:
        """Проверка позиций в поисковиках"""
        
        self._log(campaign.id, "Проверяю позиции")
        
        result = {"positions": []}
        keywords = campaign.settings.get("keywords", [])[:10]
        
        # Здесь будет реальная проверка позиций
        # Пока симулируем
        for kw in keywords:
            position = random.randint(1, 100)
            result["positions"].append({
                "keyword": kw,
                "position": position,
                "change": random.randint(-5, 5),
                "checked_at": datetime.now().isoformat()
            })
        
        # Обновляем статистику
        if result["positions"]:
            avg_pos = sum(p["position"] for p in result["positions"]) / len(result["positions"])
            best_pos = min(p["position"] for p in result["positions"])
            
            campaign.stats["average_position"] = round(avg_pos, 1)
            campaign.stats["best_position"] = best_pos
            campaign.stats["positions_checked"] = campaign.stats.get("positions_checked", 0) + 1
        
        campaign.learning_data["last_position_check"] = datetime.now().isoformat()
        campaign.learning_data["positions_history"] = campaign.learning_data.get("positions_history", [])
        campaign.learning_data["positions_history"].append(result)
        
        # Ограничиваем историю
        if len(campaign.learning_data["positions_history"]) > 30:
            campaign.learning_data["positions_history"] = campaign.learning_data["positions_history"][-30:]
        
        self._save_campaigns()
        self._log(campaign.id, f"Средняя позиция: {campaign.stats['average_position']}")
        
        return result
    
    async def _index_urls(self, campaign: Campaign) -> Dict:
        """Индексация URL"""
        # Интеграция с indexing_service
        return {"indexed": 0}
    
    async def _learn_from_result(self, campaign: Campaign, action: str, result: Dict):
        """Обучение на результатах"""
        
        if not result.get("success"):
            return
        
        # Записываем успешные стратегии
        strategy = {
            "action": action,
            "campaign_id": campaign.id,
            "domain": campaign.domain,
            "timestamp": datetime.now().isoformat(),
            "result_summary": str(result)[:500]
        }
        
        self.learning_data["successful_strategies"].append(strategy)
        
        # Обновляем лучшее время для постинга
        if action == "generate_and_post" and result.get("posted_to"):
            hour = datetime.now().hour
            domain = campaign.domain
            
            if domain not in self.learning_data["best_posting_times"]:
                self.learning_data["best_posting_times"][domain] = []
            
            if hour not in self.learning_data["best_posting_times"][domain]:
                self.learning_data["best_posting_times"][domain].append(hour)
        
        # Ограничиваем размер данных
        if len(self.learning_data["successful_strategies"]) > 1000:
            self.learning_data["successful_strategies"] = self.learning_data["successful_strategies"][-500:]
        
        self._save_learning()
    
    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Получение кампании"""
        return self.campaigns.get(campaign_id)
    
    def get_all_campaigns(self) -> List[Campaign]:
        """Получение всех кампаний"""
        return list(self.campaigns.values())
    
    def get_campaign_logs(self, campaign_id: str, limit: int = 100) -> List[Dict]:
        """Получение логов кампании"""
        return [l for l in self.logs if l["campaign_id"] == campaign_id][-limit:]
    
    def get_stats(self) -> Dict:
        """Общая статистика"""
        return {
            "total_campaigns": len(self.campaigns),
            "running_campaigns": len([c for c in self.campaigns.values() if c.status == CampaignStatus.RUNNING]),
            "total_content_generated": sum(c.stats.get("content_generated", 0) for c in self.campaigns.values()),
            "total_urls_indexed": sum(c.stats.get("urls_indexed", 0) for c in self.campaigns.values()),
            "learning_strategies": len(self.learning_data.get("successful_strategies", []))
        }
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """Удаление кампании"""
        if campaign_id in self.campaigns:
            del self.campaigns[campaign_id]
            self._save_campaigns()
            return True
        return False


# Глобальный экземпляр
_autopilot_engine = None

def get_autopilot_engine() -> AutopilotEngine:
    """Получение глобального экземпляра"""
    global _autopilot_engine
    if _autopilot_engine is None:
        _autopilot_engine = AutopilotEngine()
    return _autopilot_engine
