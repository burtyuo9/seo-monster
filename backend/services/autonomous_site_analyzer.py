"""
SEO Monster - Автономный анализатор сайтов
Анализирует сайты, извлекает ключевые слова и определяет темы для контента
"""

import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse, urljoin
from collections import Counter
import asyncio
import aiohttp
from bs4 import BeautifulSoup


class AutonomousSiteAnalyzer:
    """
    Автономный анализатор сайтов для SEO Monster.
    Работает полностью локально без внешних API.
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.analysis_dir = self.data_dir / "site_analysis"
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Стоп-слова для разных языков
        self.stop_words = self._load_stop_words()
        
        # SEO-метрики и правила
        self.seo_rules = self._load_seo_rules()
        
    def _load_stop_words(self) -> Dict[str, set]:
        """Загрузка стоп-слов для разных языков"""
        return {
            "en": {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
                "be", "have", "has", "had", "do", "does", "did", "will", "would", "could",
                "should", "may", "might", "must", "shall", "can", "need", "this", "that",
                "these", "those", "i", "you", "he", "she", "it", "we", "they", "what",
                "which", "who", "whom", "whose", "where", "when", "why", "how", "all",
                "each", "every", "both", "few", "more", "most", "other", "some", "such",
                "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
                "just", "also", "now", "here", "there", "then", "your", "our", "their",
                "my", "his", "her", "its", "about", "into", "through", "during", "before",
                "after", "above", "below", "between", "under", "again", "further", "once"
            },
            "ru": {
                "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то",
                "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
                "бы", "по", "только", "её", "мне", "было", "вот", "от", "меня", "ещё",
                "нет", "о", "из", "ему", "теперь", "когда", "уже", "вам", "ни", "быть",
                "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь", "там",
                "потом", "себя", "ничего", "ей", "может", "они", "тут", "где", "есть",
                "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб",
                "без", "будто", "чего", "раз", "тоже", "себе", "под", "будет", "ж", "тогда",
                "кто", "этот", "того", "потому", "этого", "какой", "совсем", "ним", "здесь",
                "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас", "были",
                "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", "два", "об",
                "другой", "хоть", "после", "над", "больше", "тот", "через", "эти", "нас",
                "про", "всего", "них", "какая", "много", "разве", "три", "эту", "моя",
                "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше", "чуть",
                "том", "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между"
            }
        }
    
    def _load_seo_rules(self) -> Dict:
        """Загрузка правил SEO-анализа"""
        return {
            "title": {
                "min_length": 30,
                "max_length": 60,
                "required": True
            },
            "meta_description": {
                "min_length": 120,
                "max_length": 160,
                "required": True
            },
            "h1": {
                "count": 1,
                "required": True
            },
            "h2": {
                "min_count": 2,
                "recommended": True
            },
            "images": {
                "alt_required": True,
                "max_size_kb": 200
            },
            "content": {
                "min_words": 300,
                "keyword_density_min": 1.0,
                "keyword_density_max": 3.0
            },
            "links": {
                "internal_min": 2,
                "external_max": 10
            }
        }
    
    async def analyze_site(self, url: str, depth: int = 2, max_pages: int = 10) -> Dict:
        """
        Полный анализ сайта
        
        Args:
            url: URL сайта для анализа
            depth: Глубина сканирования
            max_pages: Максимальное количество страниц
        
        Returns:
            Dict с результатами анализа
        """
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        analysis_result = {
            "url": url,
            "base_url": base_url,
            "analyzed_at": datetime.now().isoformat(),
            "pages_analyzed": 0,
            "pages": [],
            "keywords": {},
            "topics": [],
            "seo_score": 0,
            "issues": [],
            "recommendations": [],
            "content_suggestions": []
        }
        
        try:
            # Сканируем страницы
            pages_data = await self._crawl_site(url, base_url, depth, max_pages)
            analysis_result["pages"] = pages_data
            analysis_result["pages_analyzed"] = len(pages_data)
            
            # Извлекаем ключевые слова со всех страниц
            all_keywords = self._aggregate_keywords(pages_data)
            analysis_result["keywords"] = all_keywords
            
            # Определяем темы
            topics = self._identify_topics(all_keywords, pages_data)
            analysis_result["topics"] = topics
            
            # Рассчитываем SEO-оценку
            seo_score, issues = self._calculate_seo_score(pages_data)
            analysis_result["seo_score"] = seo_score
            analysis_result["issues"] = issues
            
            # Генерируем рекомендации
            recommendations = self._generate_recommendations(pages_data, all_keywords, issues)
            analysis_result["recommendations"] = recommendations
            
            # Генерируем предложения по контенту
            content_suggestions = self._generate_content_suggestions(topics, all_keywords)
            analysis_result["content_suggestions"] = content_suggestions
            
        except Exception as e:
            analysis_result["error"] = str(e)
            analysis_result["issues"].append({
                "type": "error",
                "message": f"Failed to analyze site: {str(e)}"
            })
        
        # Сохраняем результаты
        self._save_analysis(analysis_result)
        
        return analysis_result
    
    async def _crawl_site(self, start_url: str, base_url: str, 
                          depth: int, max_pages: int) -> List[Dict]:
        """Сканирование сайта"""
        visited = set()
        to_visit = [(start_url, 0)]
        pages_data = []
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "SEO Monster Bot/1.0"}
        ) as session:
            while to_visit and len(pages_data) < max_pages:
                url, current_depth = to_visit.pop(0)
                
                if url in visited:
                    continue
                
                visited.add(url)
                
                try:
                    page_data = await self._analyze_page(session, url)
                    if page_data:
                        pages_data.append(page_data)
                        
                        # Добавляем ссылки для сканирования
                        if current_depth < depth:
                            for link in page_data.get("internal_links", []):
                                if link not in visited and link.startswith(base_url):
                                    to_visit.append((link, current_depth + 1))
                
                except Exception as e:
                    print(f"Error analyzing {url}: {e}")
                    continue
        
        return pages_data
    
    async def _analyze_page(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        """Анализ отдельной страницы"""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Извлекаем данные
                page_data = {
                    "url": url,
                    "status_code": response.status,
                    "title": self._extract_title(soup),
                    "meta_description": self._extract_meta_description(soup),
                    "h1": self._extract_headings(soup, "h1"),
                    "h2": self._extract_headings(soup, "h2"),
                    "h3": self._extract_headings(soup, "h3"),
                    "content": self._extract_content(soup),
                    "word_count": 0,
                    "keywords": {},
                    "images": self._extract_images(soup, url),
                    "internal_links": self._extract_links(soup, url, internal=True),
                    "external_links": self._extract_links(soup, url, internal=False),
                    "seo_issues": [],
                    "language": self._detect_language(soup)
                }
                
                # Подсчет слов
                page_data["word_count"] = len(page_data["content"].split())
                
                # Извлечение ключевых слов
                page_data["keywords"] = self._extract_keywords(
                    page_data["content"],
                    page_data["language"]
                )
                
                # Проверка SEO-проблем
                page_data["seo_issues"] = self._check_page_seo(page_data)
                
                return page_data
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Извлечение заголовка страницы"""
        title_tag = soup.find("title")
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Извлечение мета-описания"""
        meta = soup.find("meta", attrs={"name": "description"})
        return meta.get("content", "").strip() if meta else ""
    
    def _extract_headings(self, soup: BeautifulSoup, tag: str) -> List[str]:
        """Извлечение заголовков"""
        headings = soup.find_all(tag)
        return [h.get_text().strip() for h in headings]
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Извлечение текстового контента"""
        # Удаляем скрипты и стили
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Получаем текст
        text = soup.get_text(separator=" ")
        
        # Очищаем
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Извлечение информации об изображениях"""
        images = []
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src:
                images.append({
                    "src": urljoin(base_url, src),
                    "alt": img.get("alt", ""),
                    "has_alt": bool(img.get("alt"))
                })
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str, internal: bool = True) -> List[str]:
        """Извлечение ссылок"""
        parsed_base = urlparse(base_url)
        links = []
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)
            parsed_link = urlparse(full_url)
            
            is_internal = parsed_link.netloc == parsed_base.netloc
            
            if internal and is_internal:
                links.append(full_url)
            elif not internal and not is_internal and parsed_link.scheme in ["http", "https"]:
                links.append(full_url)
        
        return list(set(links))
    
    def _detect_language(self, soup: BeautifulSoup) -> str:
        """Определение языка страницы"""
        # Проверяем атрибут lang
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            lang = html_tag.get("lang", "").lower()[:2]
            if lang in ["ru", "en"]:
                return lang
        
        # Анализируем контент
        text = self._extract_content(soup).lower()
        
        # Подсчитываем русские и английские символы
        ru_chars = len(re.findall(r'[а-яё]', text))
        en_chars = len(re.findall(r'[a-z]', text))
        
        return "ru" if ru_chars > en_chars else "en"
    
    def _extract_keywords(self, text: str, language: str = "en") -> Dict[str, int]:
        """Извлечение ключевых слов из текста"""
        # Токенизация
        if language == "ru":
            words = re.findall(r'[а-яёА-ЯЁ]{3,}', text.lower())
        else:
            words = re.findall(r'[a-zA-Z]{3,}', text.lower())
        
        # Фильтрация стоп-слов
        stop_words = self.stop_words.get(language, set())
        filtered_words = [w for w in words if w not in stop_words]
        
        # Подсчет частоты
        word_freq = Counter(filtered_words)
        
        # Возвращаем топ-50
        return dict(word_freq.most_common(50))
    
    def _check_page_seo(self, page_data: Dict) -> List[Dict]:
        """Проверка SEO-проблем на странице"""
        issues = []
        rules = self.seo_rules
        
        # Проверка title
        title = page_data.get("title", "")
        if not title:
            issues.append({"type": "error", "element": "title", "message": "Missing page title"})
        elif len(title) < rules["title"]["min_length"]:
            issues.append({"type": "warning", "element": "title", "message": f"Title too short ({len(title)} chars)"})
        elif len(title) > rules["title"]["max_length"]:
            issues.append({"type": "warning", "element": "title", "message": f"Title too long ({len(title)} chars)"})
        
        # Проверка meta description
        meta_desc = page_data.get("meta_description", "")
        if not meta_desc:
            issues.append({"type": "error", "element": "meta_description", "message": "Missing meta description"})
        elif len(meta_desc) < rules["meta_description"]["min_length"]:
            issues.append({"type": "warning", "element": "meta_description", "message": f"Meta description too short ({len(meta_desc)} chars)"})
        elif len(meta_desc) > rules["meta_description"]["max_length"]:
            issues.append({"type": "warning", "element": "meta_description", "message": f"Meta description too long ({len(meta_desc)} chars)"})
        
        # Проверка H1
        h1_count = len(page_data.get("h1", []))
        if h1_count == 0:
            issues.append({"type": "error", "element": "h1", "message": "Missing H1 heading"})
        elif h1_count > 1:
            issues.append({"type": "warning", "element": "h1", "message": f"Multiple H1 headings ({h1_count})"})
        
        # Проверка H2
        h2_count = len(page_data.get("h2", []))
        if h2_count < rules["h2"]["min_count"]:
            issues.append({"type": "info", "element": "h2", "message": f"Few H2 headings ({h2_count})"})
        
        # Проверка контента
        word_count = page_data.get("word_count", 0)
        if word_count < rules["content"]["min_words"]:
            issues.append({"type": "warning", "element": "content", "message": f"Thin content ({word_count} words)"})
        
        # Проверка изображений
        images = page_data.get("images", [])
        images_without_alt = [img for img in images if not img.get("has_alt")]
        if images_without_alt:
            issues.append({"type": "warning", "element": "images", "message": f"{len(images_without_alt)} images without alt text"})
        
        return issues
    
    def _aggregate_keywords(self, pages_data: List[Dict]) -> Dict[str, Dict]:
        """Агрегация ключевых слов со всех страниц"""
        all_keywords = Counter()
        keyword_pages = {}
        
        for page in pages_data:
            page_keywords = page.get("keywords", {})
            for keyword, count in page_keywords.items():
                all_keywords[keyword] += count
                if keyword not in keyword_pages:
                    keyword_pages[keyword] = []
                keyword_pages[keyword].append(page["url"])
        
        # Формируем результат
        result = {}
        for keyword, count in all_keywords.most_common(100):
            result[keyword] = {
                "count": count,
                "pages": keyword_pages.get(keyword, [])[:5],
                "density": round(count / sum(all_keywords.values()) * 100, 2) if all_keywords else 0
            }
        
        return result
    
    def _identify_topics(self, keywords: Dict, pages_data: List[Dict]) -> List[Dict]:
        """Определение тем на основе ключевых слов"""
        # Группируем ключевые слова по семантике
        topics = []
        
        # Берем топ ключевые слова как темы
        top_keywords = list(keywords.keys())[:20]
        
        for keyword in top_keywords:
            keyword_data = keywords[keyword]
            
            # Находим связанные ключевые слова
            related = []
            for other_kw in top_keywords:
                if other_kw != keyword:
                    # Проверяем, встречаются ли на тех же страницах
                    common_pages = set(keyword_data["pages"]) & set(keywords.get(other_kw, {}).get("pages", []))
                    if common_pages:
                        related.append(other_kw)
            
            topics.append({
                "keyword": keyword,
                "count": keyword_data["count"],
                "density": keyword_data["density"],
                "related_keywords": related[:5],
                "pages": keyword_data["pages"]
            })
        
        return topics[:10]
    
    def _calculate_seo_score(self, pages_data: List[Dict]) -> Tuple[int, List[Dict]]:
        """Расчет общей SEO-оценки"""
        if not pages_data:
            return 0, [{"type": "error", "message": "No pages analyzed"}]
        
        total_score = 0
        all_issues = []
        
        for page in pages_data:
            page_score = 100
            page_issues = page.get("seo_issues", [])
            
            for issue in page_issues:
                if issue["type"] == "error":
                    page_score -= 15
                elif issue["type"] == "warning":
                    page_score -= 5
                elif issue["type"] == "info":
                    page_score -= 2
                
                all_issues.append({
                    **issue,
                    "page": page["url"]
                })
            
            total_score += max(0, page_score)
        
        avg_score = round(total_score / len(pages_data))
        
        return avg_score, all_issues
    
    def _generate_recommendations(self, pages_data: List[Dict], 
                                  keywords: Dict, issues: List[Dict]) -> List[Dict]:
        """Генерация рекомендаций по улучшению"""
        recommendations = []
        
        # Анализируем проблемы
        issue_types = Counter(issue["element"] for issue in issues if "element" in issue)
        
        if issue_types.get("title", 0) > 0:
            recommendations.append({
                "priority": "high",
                "category": "title",
                "recommendation": "Optimize page titles",
                "description": "Ensure all pages have unique, descriptive titles between 30-60 characters with target keywords.",
                "affected_pages": issue_types["title"]
            })
        
        if issue_types.get("meta_description", 0) > 0:
            recommendations.append({
                "priority": "high",
                "category": "meta_description",
                "recommendation": "Add/improve meta descriptions",
                "description": "Write compelling meta descriptions (120-160 chars) for all pages with call-to-action.",
                "affected_pages": issue_types["meta_description"]
            })
        
        if issue_types.get("h1", 0) > 0:
            recommendations.append({
                "priority": "high",
                "category": "h1",
                "recommendation": "Fix H1 headings",
                "description": "Each page should have exactly one H1 heading containing the primary keyword.",
                "affected_pages": issue_types["h1"]
            })
        
        if issue_types.get("content", 0) > 0:
            recommendations.append({
                "priority": "medium",
                "category": "content",
                "recommendation": "Expand thin content",
                "description": "Pages with less than 300 words should be expanded with valuable, keyword-rich content.",
                "affected_pages": issue_types["content"]
            })
        
        if issue_types.get("images", 0) > 0:
            recommendations.append({
                "priority": "medium",
                "category": "images",
                "recommendation": "Add alt text to images",
                "description": "All images should have descriptive alt text for accessibility and SEO.",
                "affected_pages": issue_types["images"]
            })
        
        # Рекомендации по контенту
        top_keywords = list(keywords.keys())[:5]
        if top_keywords:
            recommendations.append({
                "priority": "medium",
                "category": "content_strategy",
                "recommendation": "Create content for top keywords",
                "description": f"Focus content creation on: {', '.join(top_keywords)}",
                "keywords": top_keywords
            })
        
        return recommendations
    
    def _generate_content_suggestions(self, topics: List[Dict], 
                                      keywords: Dict) -> List[Dict]:
        """Генерация предложений по созданию контента"""
        suggestions = []
        
        for topic in topics[:5]:
            keyword = topic["keyword"]
            related = topic.get("related_keywords", [])
            
            # Предлагаем разные типы контента
            suggestions.append({
                "topic": keyword,
                "type": "guide",
                "title_suggestion": f"Complete Guide to {keyword.capitalize()}",
                "keywords": [keyword] + related[:3],
                "estimated_words": 1500,
                "priority": "high" if topic["count"] > 10 else "medium"
            })
            
            if related:
                suggestions.append({
                    "topic": keyword,
                    "type": "how_to",
                    "title_suggestion": f"How to {keyword.capitalize()}: Step-by-Step",
                    "keywords": [keyword] + related[:3],
                    "estimated_words": 1000,
                    "priority": "medium"
                })
        
        return suggestions
    
    def _save_analysis(self, analysis: Dict) -> str:
        """Сохранение результатов анализа"""
        url_hash = hashlib.md5(analysis["url"].encode()).hexdigest()[:8]
        filename = f"analysis_{url_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.analysis_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def get_analysis_history(self) -> List[Dict]:
        """Получение истории анализов"""
        analyses = []
        for file in self.analysis_dir.glob("analysis_*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                analyses.append({
                    "url": data.get("url"),
                    "analyzed_at": data.get("analyzed_at"),
                    "seo_score": data.get("seo_score"),
                    "pages_analyzed": data.get("pages_analyzed"),
                    "file": str(file)
                })
        return sorted(analyses, key=lambda x: x.get("analyzed_at", ""), reverse=True)
    
    def quick_analyze(self, url: str) -> Dict:
        """Быстрый синхронный анализ одной страницы"""
        import requests
        
        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "SEO Monster Bot/1.0"})
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            page_data = {
                "url": url,
                "status_code": response.status_code,
                "title": self._extract_title(soup),
                "meta_description": self._extract_meta_description(soup),
                "h1": self._extract_headings(soup, "h1"),
                "h2": self._extract_headings(soup, "h2"),
                "content": self._extract_content(soup),
                "language": self._detect_language(soup)
            }
            
            page_data["word_count"] = len(page_data["content"].split())
            page_data["keywords"] = self._extract_keywords(page_data["content"], page_data["language"])
            page_data["seo_issues"] = self._check_page_seo(page_data)
            
            # Рассчитываем оценку
            score = 100
            for issue in page_data["seo_issues"]:
                if issue["type"] == "error":
                    score -= 15
                elif issue["type"] == "warning":
                    score -= 5
            
            page_data["seo_score"] = max(0, score)
            page_data["analyzed_at"] = datetime.now().isoformat()
            
            return page_data
            
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "seo_score": 0,
                "analyzed_at": datetime.now().isoformat()
            }


# Создаем глобальный экземпляр
autonomous_site_analyzer = AutonomousSiteAnalyzer()
