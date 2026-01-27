"""
SEO Monster - Автономный движок генерации контента
Генерирует SEO-оптимизированный контент без внешних AI API
"""

import json
import random
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class AutonomousContentEngine:
    """
    Автономный движок для генерации SEO-контента.
    Работает полностью локально без внешних API.
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.templates_dir = self.data_dir / "content_templates"
        self.generated_dir = self.data_dir / "generated_content"
        
        # Создаем директории
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        
        # Загружаем базу знаний
        self.knowledge_base = self._load_knowledge_base()
        self.templates = self._load_templates()
        self.synonyms = self._load_synonyms()
        
    def _load_knowledge_base(self) -> Dict:
        """Загрузка базы знаний для генерации контента"""
        kb_file = self.data_dir / "knowledge_base.json"
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Базовая база знаний
        default_kb = {
            "industries": {
                "crypto": {
                    "terms": ["blockchain", "cryptocurrency", "Bitcoin", "Ethereum", "wallet", "exchange", "token", "DeFi", "NFT", "mining"],
                    "benefits": ["decentralization", "security", "transparency", "fast transactions", "low fees", "global access"],
                    "pain_points": ["volatility", "complexity", "security concerns", "regulation", "scams"],
                    "cta_phrases": ["Get started today", "Join now", "Start trading", "Create account", "Learn more"]
                },
                "fintech": {
                    "terms": ["payment", "transaction", "card", "account", "transfer", "deposit", "withdrawal", "balance"],
                    "benefits": ["convenience", "speed", "security", "accessibility", "cost-effective"],
                    "pain_points": ["fees", "delays", "verification", "limits", "support"],
                    "cta_phrases": ["Open account", "Get your card", "Start saving", "Try free", "Apply now"]
                },
                "ecommerce": {
                    "terms": ["shopping", "cart", "checkout", "delivery", "product", "order", "discount", "promotion"],
                    "benefits": ["convenience", "variety", "competitive prices", "home delivery", "easy returns"],
                    "pain_points": ["shipping costs", "delivery time", "product quality", "returns", "trust"],
                    "cta_phrases": ["Shop now", "Add to cart", "Buy today", "Get discount", "Free shipping"]
                },
                "saas": {
                    "terms": ["software", "platform", "tool", "automation", "integration", "dashboard", "analytics", "API"],
                    "benefits": ["efficiency", "automation", "scalability", "cost savings", "insights"],
                    "pain_points": ["learning curve", "integration", "pricing", "support", "customization"],
                    "cta_phrases": ["Start free trial", "Book demo", "Get started", "See pricing", "Contact sales"]
                }
            },
            "article_structures": {
                "how_to": {
                    "intro_templates": [
                        "In this comprehensive guide, we'll walk you through {topic} step by step.",
                        "Looking to {action}? You've come to the right place.",
                        "Many people struggle with {topic}. This guide will make it simple.",
                        "{Topic} doesn't have to be complicated. Here's how to do it right."
                    ],
                    "section_templates": [
                        "Step {n}: {action}",
                        "Phase {n}: {action}",
                        "{n}. {action}",
                        "Part {n}: {action}"
                    ],
                    "conclusion_templates": [
                        "Now you know how to {topic}. Start implementing these steps today!",
                        "Following these steps will help you {benefit}.",
                        "With this knowledge, you're ready to {action} like a pro.",
                        "Take action now and {benefit}."
                    ]
                },
                "listicle": {
                    "intro_templates": [
                        "Here are the top {n} {items} you need to know about.",
                        "Discover {n} {items} that will {benefit}.",
                        "We've compiled {n} essential {items} for {audience}.",
                        "Looking for the best {items}? Here are our top {n} picks."
                    ],
                    "item_templates": [
                        "{n}. {item} - {description}",
                        "#{n}: {item}",
                        "{item}: {description}",
                        "**{item}** - {description}"
                    ],
                    "conclusion_templates": [
                        "These {n} {items} will help you {benefit}.",
                        "Start with any of these {items} and see the difference.",
                        "Which {item} will you try first?",
                        "Implement these {items} to {benefit}."
                    ]
                },
                "comparison": {
                    "intro_templates": [
                        "Choosing between {option1} and {option2}? Let's compare them.",
                        "In this comparison, we'll analyze {option1} vs {option2}.",
                        "Which is better: {option1} or {option2}? Find out here.",
                        "A detailed comparison of {option1} and {option2}."
                    ],
                    "section_templates": [
                        "## {aspect}\n\n**{option1}:** {description1}\n\n**{option2}:** {description2}",
                        "### {aspect} Comparison",
                        "When it comes to {aspect}..."
                    ],
                    "conclusion_templates": [
                        "The winner depends on your specific needs.",
                        "Choose {option1} if you need {benefit1}. Choose {option2} for {benefit2}.",
                        "Both options have their strengths. Consider your priorities.",
                        "Make your decision based on {criteria}."
                    ]
                },
                "guide": {
                    "intro_templates": [
                        "This complete guide covers everything you need to know about {topic}.",
                        "Welcome to the ultimate guide to {topic}.",
                        "Everything about {topic} explained in simple terms.",
                        "Your comprehensive resource for understanding {topic}."
                    ],
                    "section_templates": [
                        "## What is {topic}?",
                        "## Why {topic} Matters",
                        "## How {topic} Works",
                        "## Benefits of {topic}",
                        "## Common Mistakes with {topic}",
                        "## Best Practices for {topic}",
                        "## FAQ about {topic}"
                    ],
                    "conclusion_templates": [
                        "You now have a solid understanding of {topic}.",
                        "Use this knowledge to {benefit}.",
                        "Start applying these concepts today.",
                        "Ready to take the next step with {topic}?"
                    ]
                }
            },
            "seo_elements": {
                "meta_templates": [
                    "{keyword} - Complete Guide [{year}]",
                    "How to {action}: Step-by-Step Guide",
                    "Top {n} {items} for {audience} [{year}]",
                    "{keyword}: Everything You Need to Know",
                    "Best {items} - Expert Recommendations"
                ],
                "heading_modifiers": [
                    "Complete", "Ultimate", "Essential", "Comprehensive", "Expert",
                    "Proven", "Effective", "Simple", "Quick", "Best"
                ],
                "power_words": [
                    "discover", "unlock", "master", "transform", "boost",
                    "maximize", "optimize", "streamline", "accelerate", "revolutionize"
                ]
            }
        }
        
        # Сохраняем базу знаний
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(default_kb, f, indent=2, ensure_ascii=False)
        
        return default_kb
    
    def _load_templates(self) -> Dict:
        """Загрузка шаблонов контента"""
        templates_file = self.templates_dir / "article_templates.json"
        if templates_file.exists():
            with open(templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_synonyms(self) -> Dict:
        """Загрузка словаря синонимов для вариативности"""
        return {
            "important": ["crucial", "essential", "vital", "critical", "key"],
            "good": ["excellent", "great", "outstanding", "superior", "exceptional"],
            "bad": ["poor", "inadequate", "subpar", "inferior", "unsatisfactory"],
            "fast": ["quick", "rapid", "swift", "speedy", "instant"],
            "easy": ["simple", "straightforward", "effortless", "convenient", "user-friendly"],
            "help": ["assist", "support", "aid", "facilitate", "enable"],
            "use": ["utilize", "employ", "leverage", "apply", "implement"],
            "get": ["obtain", "acquire", "receive", "gain", "secure"],
            "make": ["create", "build", "develop", "produce", "generate"],
            "show": ["demonstrate", "illustrate", "reveal", "display", "present"]
        }
    
    def analyze_topic(self, topic: str, url: str = None) -> Dict:
        """Анализ темы и определение индустрии"""
        topic_lower = topic.lower()
        
        # Определяем индустрию
        industry = "general"
        industry_score = 0
        
        for ind, data in self.knowledge_base.get("industries", {}).items():
            score = sum(1 for term in data.get("terms", []) if term.lower() in topic_lower)
            if score > industry_score:
                industry_score = score
                industry = ind
        
        # Извлекаем ключевые слова
        keywords = self._extract_keywords(topic)
        
        # Определяем тип контента
        content_type = self._determine_content_type(topic)
        
        return {
            "topic": topic,
            "industry": industry,
            "keywords": keywords,
            "content_type": content_type,
            "suggested_structure": self._suggest_structure(content_type),
            "related_terms": self._get_related_terms(industry),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов из текста"""
        # Удаляем стоп-слова
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
            "be", "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare", "ought",
            "used", "this", "that", "these", "those", "i", "you", "he", "she", "it",
            "we", "they", "what", "which", "who", "whom", "whose", "where", "when",
            "why", "how", "all", "each", "every", "both", "few", "more", "most",
            "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
            "than", "too", "very", "just", "also", "now", "here", "there", "then"
        }
        
        # Токенизация
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Фильтрация и подсчет
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Сортировка по частоте
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:10]]
    
    def _determine_content_type(self, topic: str) -> str:
        """Определение типа контента на основе темы"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ["how to", "guide", "tutorial", "steps"]):
            return "how_to"
        elif any(word in topic_lower for word in ["top", "best", "list", "ways", "tips", "reasons"]):
            return "listicle"
        elif any(word in topic_lower for word in ["vs", "versus", "comparison", "compare", "difference"]):
            return "comparison"
        else:
            return "guide"
    
    def _suggest_structure(self, content_type: str) -> Dict:
        """Предложение структуры статьи"""
        structures = {
            "how_to": {
                "sections": ["Introduction", "Prerequisites", "Step 1", "Step 2", "Step 3", "Step 4", "Step 5", "Tips", "Conclusion"],
                "word_count": 1000,
                "images": 3
            },
            "listicle": {
                "sections": ["Introduction", "Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8", "Item 9", "Item 10", "Conclusion"],
                "word_count": 1200,
                "images": 5
            },
            "comparison": {
                "sections": ["Introduction", "Overview", "Features", "Pricing", "Pros and Cons", "Use Cases", "Verdict", "Conclusion"],
                "word_count": 1500,
                "images": 4
            },
            "guide": {
                "sections": ["Introduction", "What is", "Why it Matters", "How it Works", "Benefits", "Best Practices", "Common Mistakes", "FAQ", "Conclusion"],
                "word_count": 2000,
                "images": 6
            }
        }
        return structures.get(content_type, structures["guide"])
    
    def _get_related_terms(self, industry: str) -> List[str]:
        """Получение связанных терминов для индустрии"""
        industry_data = self.knowledge_base.get("industries", {}).get(industry, {})
        return industry_data.get("terms", [])[:10]
    
    def generate_article(self, topic: str, keywords: List[str] = None, 
                        content_type: str = None, word_count: int = 1000,
                        language: str = "en") -> Dict:
        """
        Генерация полной SEO-статьи
        
        Args:
            topic: Тема статьи
            keywords: Список ключевых слов
            content_type: Тип контента (how_to, listicle, comparison, guide)
            word_count: Целевое количество слов
            language: Язык статьи (en/ru)
        
        Returns:
            Dict с сгенерированной статьей
        """
        # Анализируем тему
        analysis = self.analyze_topic(topic)
        
        if not content_type:
            content_type = analysis["content_type"]
        
        if not keywords:
            keywords = analysis["keywords"]
        
        # Получаем структуру
        structure = self.knowledge_base.get("article_structures", {}).get(content_type, {})
        
        # Генерируем контент
        if language == "ru":
            article = self._generate_russian_article(topic, keywords, content_type, word_count, analysis)
        else:
            article = self._generate_english_article(topic, keywords, content_type, word_count, analysis, structure)
        
        # Сохраняем статью
        article_id = hashlib.md5(f"{topic}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        article_data = {
            "id": article_id,
            "topic": topic,
            "keywords": keywords,
            "content_type": content_type,
            "language": language,
            "title": article["title"],
            "meta_description": article["meta_description"],
            "content": article["content"],
            "word_count": len(article["content"].split()),
            "sections": article.get("sections", []),
            "generated_at": datetime.now().isoformat(),
            "analysis": analysis
        }
        
        # Сохраняем в файл
        output_file = self.generated_dir / f"article_{article_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, indent=2, ensure_ascii=False)
        
        return article_data
    
    def _generate_english_article(self, topic: str, keywords: List[str], 
                                  content_type: str, word_count: int,
                                  analysis: Dict, structure: Dict) -> Dict:
        """Генерация статьи на английском языке"""
        
        industry = analysis.get("industry", "general")
        industry_data = self.knowledge_base.get("industries", {}).get(industry, {})
        
        # Генерируем заголовок
        title = self._generate_title(topic, content_type, keywords)
        
        # Генерируем мета-описание
        meta_description = self._generate_meta_description(topic, keywords)
        
        # Генерируем контент по секциям
        sections = []
        content_parts = []
        
        # Введение
        intro = self._generate_intro(topic, content_type, structure, industry_data)
        content_parts.append(intro)
        sections.append({"title": "Introduction", "content": intro})
        
        # Основные секции
        if content_type == "how_to":
            main_content = self._generate_how_to_content(topic, keywords, industry_data, word_count)
        elif content_type == "listicle":
            main_content = self._generate_listicle_content(topic, keywords, industry_data, word_count)
        elif content_type == "comparison":
            main_content = self._generate_comparison_content(topic, keywords, industry_data, word_count)
        else:
            main_content = self._generate_guide_content(topic, keywords, industry_data, word_count)
        
        for section in main_content:
            content_parts.append(f"## {section['title']}\n\n{section['content']}")
            sections.append(section)
        
        # Заключение
        conclusion = self._generate_conclusion(topic, content_type, structure, industry_data)
        content_parts.append(f"## Conclusion\n\n{conclusion}")
        sections.append({"title": "Conclusion", "content": conclusion})
        
        # Собираем полный контент
        full_content = f"# {title}\n\n" + "\n\n".join(content_parts)
        
        return {
            "title": title,
            "meta_description": meta_description,
            "content": full_content,
            "sections": sections
        }
    
    def _generate_russian_article(self, topic: str, keywords: List[str],
                                  content_type: str, word_count: int,
                                  analysis: Dict) -> Dict:
        """Генерация статьи на русском языке"""
        
        # Русские шаблоны
        ru_templates = {
            "how_to": {
                "title_templates": [
                    "Как {topic}: Полное руководство",
                    "{Topic}: Пошаговая инструкция",
                    "Как правильно {topic} в {year} году",
                    "{Topic} для начинающих: Подробный гайд"
                ],
                "intro_templates": [
                    "В этом руководстве мы подробно рассмотрим, как {topic}. Вы узнаете все необходимые шаги и получите практические советы.",
                    "Хотите узнать, как {topic}? Вы попали по адресу. Это руководство поможет вам разобраться во всех тонкостях.",
                    "Многие сталкиваются с трудностями, когда дело касается {topic}. Наше руководство сделает этот процесс простым и понятным."
                ],
                "step_template": "### Шаг {n}: {action}\n\n{description}",
                "conclusion_templates": [
                    "Теперь вы знаете, как {topic}. Применяйте эти знания на практике и достигайте результатов!",
                    "Следуя этим шагам, вы сможете успешно {topic}. Начните прямо сейчас!",
                    "Мы рассмотрели все аспекты {topic}. Пора переходить к действиям!"
                ]
            },
            "listicle": {
                "title_templates": [
                    "Топ-{n} {items}: Полный обзор",
                    "{N} лучших {items} в {year} году",
                    "{N} способов {action}",
                    "Лучшие {items}: Рейтинг {year}"
                ],
                "intro_templates": [
                    "Представляем вам подборку лучших {items}. Мы отобрали самые эффективные варианты.",
                    "Ищете лучшие {items}? Мы составили список из {n} проверенных вариантов.",
                    "В этой статье вы найдете {n} {items}, которые помогут вам достичь цели."
                ],
                "item_template": "### {n}. {item}\n\n{description}",
                "conclusion_templates": [
                    "Эти {n} {items} помогут вам достичь желаемого результата.",
                    "Выберите подходящий вариант из нашего списка и начните действовать.",
                    "Какой из этих {items} вы попробуете первым?"
                ]
            },
            "guide": {
                "title_templates": [
                    "{Topic}: Полное руководство",
                    "Всё о {topic}: Подробный гайд",
                    "{Topic} от А до Я",
                    "Полный гайд по {topic} [{year}]"
                ],
                "intro_templates": [
                    "Это руководство охватывает всё, что вам нужно знать о {topic}.",
                    "Добро пожаловать в полное руководство по {topic}.",
                    "Всё о {topic} простым языком."
                ],
                "section_templates": [
                    "## Что такое {topic}?",
                    "## Почему {topic} важен",
                    "## Как работает {topic}",
                    "## Преимущества {topic}",
                    "## Частые ошибки",
                    "## Лучшие практики",
                    "## FAQ"
                ],
                "conclusion_templates": [
                    "Теперь у вас есть полное понимание {topic}.",
                    "Используйте эти знания для достижения ваших целей.",
                    "Готовы применить полученные знания на практике?"
                ]
            }
        }
        
        templates = ru_templates.get(content_type, ru_templates["guide"])
        year = datetime.now().year
        
        # Генерируем заголовок
        title_template = random.choice(templates["title_templates"])
        title = title_template.format(topic=topic, Topic=topic.capitalize(), n=10, N=10, 
                                     items=topic, year=year, action=topic)
        
        # Генерируем мета-описание
        meta_description = f"{topic.capitalize()} - подробное руководство с практическими советами. Узнайте всё о {topic} в нашей статье."
        
        # Генерируем введение
        intro_template = random.choice(templates["intro_templates"])
        intro = intro_template.format(topic=topic, n=10, items=topic)
        
        # Генерируем основной контент
        content_parts = [f"# {title}\n\n{intro}"]
        sections = [{"title": "Введение", "content": intro}]
        
        if content_type == "how_to":
            steps = [
                ("Подготовка", f"Прежде чем приступить к {topic}, необходимо подготовиться. Убедитесь, что у вас есть все необходимые инструменты и ресурсы."),
                ("Анализ", f"Проанализируйте текущую ситуацию. Определите ваши цели и задачи в контексте {topic}."),
                ("Планирование", f"Составьте план действий. Разбейте процесс {topic} на конкретные этапы."),
                ("Реализация", f"Приступайте к выполнению плана. Следуйте намеченным шагам для успешного {topic}."),
                ("Проверка", f"Проверьте результаты. Убедитесь, что {topic} выполнен правильно и соответствует вашим ожиданиям."),
                ("Оптимизация", f"Оптимизируйте процесс. Найдите способы улучшить {topic} на основе полученного опыта.")
            ]
            for i, (step_title, step_desc) in enumerate(steps, 1):
                section_content = f"### Шаг {i}: {step_title}\n\n{step_desc}"
                content_parts.append(section_content)
                sections.append({"title": f"Шаг {i}: {step_title}", "content": step_desc})
        
        elif content_type == "listicle":
            items = [
                ("Эффективность", f"Повышение эффективности - ключевой аспект {topic}. Это позволяет достигать лучших результатов."),
                ("Простота использования", f"Простота - важный фактор при работе с {topic}. Чем проще процесс, тем лучше результат."),
                ("Надежность", f"Надежность гарантирует стабильную работу {topic} в любых условиях."),
                ("Масштабируемость", f"Возможность масштабирования позволяет расширять {topic} по мере роста потребностей."),
                ("Безопасность", f"Безопасность - приоритет при работе с {topic}. Защита данных и ресурсов критически важна."),
                ("Поддержка", f"Качественная поддержка обеспечивает решение любых вопросов, связанных с {topic}."),
                ("Интеграция", f"Возможности интеграции расширяют функционал {topic} и повышают его ценность."),
                ("Аналитика", f"Аналитические инструменты помогают отслеживать эффективность {topic}."),
                ("Автоматизация", f"Автоматизация процессов экономит время и ресурсы при работе с {topic}."),
                ("Стоимость", f"Оптимальное соотношение цены и качества делает {topic} доступным для всех.")
            ]
            for i, (item_title, item_desc) in enumerate(items, 1):
                section_content = f"### {i}. {item_title}\n\n{item_desc}"
                content_parts.append(section_content)
                sections.append({"title": f"{i}. {item_title}", "content": item_desc})
        
        else:  # guide
            guide_sections = [
                (f"Что такое {topic}?", f"{topic.capitalize()} - это важный инструмент/процесс, который позволяет достигать конкретных целей. В этом разделе мы рассмотрим основные понятия и определения."),
                (f"Почему {topic} важен", f"Понимание важности {topic} поможет вам эффективнее использовать его возможности. Рассмотрим ключевые преимущества и выгоды."),
                (f"Как работает {topic}", f"Механизм работы {topic} основан на проверенных принципах. Разберем основные этапы и процессы."),
                ("Преимущества", f"Использование {topic} дает множество преимуществ: экономия времени, повышение эффективности, улучшение результатов."),
                ("Лучшие практики", f"Следуйте лучшим практикам для максимальной эффективности {topic}. Мы собрали проверенные рекомендации экспертов."),
                ("Частые ошибки", f"Избегайте распространенных ошибок при работе с {topic}. Знание типичных проблем поможет их предотвратить."),
                ("FAQ", f"Ответы на часто задаваемые вопросы о {topic}. Здесь вы найдете решения типичных проблем.")
            ]
            for section_title, section_desc in guide_sections:
                section_content = f"## {section_title}\n\n{section_desc}"
                content_parts.append(section_content)
                sections.append({"title": section_title, "content": section_desc})
        
        # Заключение
        conclusion_template = random.choice(templates["conclusion_templates"])
        conclusion = conclusion_template.format(topic=topic, n=10, items=topic)
        content_parts.append(f"## Заключение\n\n{conclusion}")
        sections.append({"title": "Заключение", "content": conclusion})
        
        full_content = "\n\n".join(content_parts)
        
        return {
            "title": title,
            "meta_description": meta_description,
            "content": full_content,
            "sections": sections
        }
    
    def _generate_title(self, topic: str, content_type: str, keywords: List[str]) -> str:
        """Генерация SEO-заголовка"""
        year = datetime.now().year
        modifiers = self.knowledge_base.get("seo_elements", {}).get("heading_modifiers", [])
        modifier = random.choice(modifiers) if modifiers else "Complete"
        
        templates = {
            "how_to": [
                f"How to {topic.capitalize()}: {modifier} Guide [{year}]",
                f"{modifier} Guide to {topic.capitalize()}",
                f"How to {topic.capitalize()} Step by Step"
            ],
            "listicle": [
                f"Top 10 {topic.capitalize()} Tips [{year}]",
                f"10 {modifier} {topic.capitalize()} Strategies",
                f"Best {topic.capitalize()}: {modifier} List"
            ],
            "comparison": [
                f"{topic.capitalize()}: {modifier} Comparison [{year}]",
                f"Comparing {topic.capitalize()} Options",
                f"{topic.capitalize()} Comparison Guide"
            ],
            "guide": [
                f"{modifier} Guide to {topic.capitalize()} [{year}]",
                f"{topic.capitalize()}: Everything You Need to Know",
                f"The {modifier} {topic.capitalize()} Guide"
            ]
        }
        
        return random.choice(templates.get(content_type, templates["guide"]))
    
    def _generate_meta_description(self, topic: str, keywords: List[str]) -> str:
        """Генерация мета-описания"""
        year = datetime.now().year
        keyword_str = ", ".join(keywords[:3]) if keywords else topic
        
        templates = [
            f"Learn everything about {topic} in our comprehensive guide. Discover {keyword_str} and more. Updated for {year}.",
            f"Complete guide to {topic}. Expert tips on {keyword_str}. Start improving today!",
            f"Discover how to master {topic}. Covers {keyword_str}. Free guide with actionable tips."
        ]
        
        return random.choice(templates)
    
    def _generate_intro(self, topic: str, content_type: str, structure: Dict, industry_data: Dict) -> str:
        """Генерация введения"""
        templates = structure.get("intro_templates", [])
        if not templates:
            templates = [f"This article covers everything you need to know about {topic}."]
        
        template = random.choice(templates)
        
        # Заполняем шаблон
        intro = template.format(
            topic=topic,
            Topic=topic.capitalize(),
            action=topic,
            n=10,
            items=topic,
            benefit="achieve your goals",
            audience="everyone"
        )
        
        # Добавляем дополнительный контекст
        benefits = industry_data.get("benefits", [])
        if benefits:
            benefit_text = f" You'll learn about {', '.join(benefits[:3])} and more."
            intro += benefit_text
        
        return intro
    
    def _generate_conclusion(self, topic: str, content_type: str, structure: Dict, industry_data: Dict) -> str:
        """Генерация заключения"""
        templates = structure.get("conclusion_templates", [])
        if not templates:
            templates = [f"Now you have a solid understanding of {topic}."]
        
        template = random.choice(templates)
        
        cta_phrases = industry_data.get("cta_phrases", ["Get started today"])
        cta = random.choice(cta_phrases)
        
        conclusion = template.format(
            topic=topic,
            benefit="achieve better results",
            action=topic,
            n=10,
            items=topic
        )
        
        conclusion += f"\n\n**{cta}!**"
        
        return conclusion
    
    def _generate_how_to_content(self, topic: str, keywords: List[str], 
                                 industry_data: Dict, word_count: int) -> List[Dict]:
        """Генерация контента типа how-to"""
        sections = []
        
        steps = [
            ("Understanding the Basics", f"Before diving into {topic}, it's essential to understand the fundamentals. This foundation will help you make better decisions throughout the process."),
            ("Preparation", f"Proper preparation is key to success with {topic}. Gather all necessary resources and tools before you begin."),
            ("Getting Started", f"Now it's time to take action. Follow these initial steps to begin your journey with {topic}."),
            ("Implementation", f"This is where the real work happens. Implement the strategies we've discussed to achieve results with {topic}."),
            ("Optimization", f"Once you've completed the basic implementation, focus on optimization. Fine-tune your approach to {topic} for maximum effectiveness."),
            ("Monitoring and Adjustment", f"Success with {topic} requires ongoing monitoring. Track your progress and make adjustments as needed.")
        ]
        
        for title, content in steps:
            # Расширяем контент
            expanded_content = content
            
            # Добавляем списки
            benefits = industry_data.get("benefits", [])
            if benefits and random.random() > 0.5:
                benefit_list = "\n".join([f"- {b.capitalize()}" for b in benefits[:4]])
                expanded_content += f"\n\nKey benefits to consider:\n\n{benefit_list}"
            
            # Добавляем советы
            expanded_content += f"\n\n**Pro tip:** Focus on consistency when working with {topic}. Small, regular improvements lead to significant results over time."
            
            sections.append({"title": title, "content": expanded_content})
        
        return sections
    
    def _generate_listicle_content(self, topic: str, keywords: List[str],
                                   industry_data: Dict, word_count: int) -> List[Dict]:
        """Генерация контента типа listicle"""
        sections = []
        
        items = [
            ("Efficiency", "Maximize your efficiency", "Improving efficiency is crucial for success. Focus on streamlining processes and eliminating waste."),
            ("Quality", "Maintain high quality", "Never compromise on quality. It's the foundation of long-term success and customer satisfaction."),
            ("Innovation", "Embrace innovation", "Stay ahead of the curve by embracing new technologies and approaches."),
            ("Scalability", "Plan for scalability", "Build systems that can grow with your needs. Scalability ensures long-term viability."),
            ("Security", "Prioritize security", "In today's digital world, security is non-negotiable. Protect your assets and data."),
            ("User Experience", "Focus on user experience", "A great user experience drives engagement and loyalty."),
            ("Analytics", "Leverage analytics", "Data-driven decisions lead to better outcomes. Use analytics to guide your strategy."),
            ("Automation", "Implement automation", "Automate repetitive tasks to free up time for strategic activities."),
            ("Integration", "Enable integration", "Seamless integration with other tools and systems multiplies your effectiveness."),
            ("Support", "Provide excellent support", "Great support builds trust and ensures customer success.")
        ]
        
        for i, (title, subtitle, description) in enumerate(items, 1):
            content = f"**{subtitle}**\n\n{description}"
            
            # Добавляем контекст индустрии
            terms = industry_data.get("terms", [])
            if terms and i % 3 == 0:
                term = random.choice(terms)
                content += f"\n\nThis is especially important when dealing with {term}."
            
            sections.append({"title": f"{i}. {title}", "content": content})
        
        return sections
    
    def _generate_comparison_content(self, topic: str, keywords: List[str],
                                     industry_data: Dict, word_count: int) -> List[Dict]:
        """Генерация контента типа comparison"""
        sections = []
        
        aspects = [
            ("Overview", f"Let's start with a general overview of the options available for {topic}. Understanding the landscape helps make informed decisions."),
            ("Features", f"When comparing {topic} options, features are often the first consideration. Look for the capabilities that matter most to your use case."),
            ("Pricing", f"Cost is always a factor. Compare pricing models to find the best value for your budget and requirements."),
            ("Ease of Use", f"User-friendliness can make or break your experience. Consider the learning curve and daily usability."),
            ("Performance", f"Performance matters. Evaluate speed, reliability, and consistency across different scenarios."),
            ("Support", f"Quality support can save you time and frustration. Compare support options and response times."),
            ("Verdict", f"Based on our analysis, the best choice depends on your specific needs. Consider your priorities and constraints.")
        ]
        
        for title, content in aspects:
            sections.append({"title": title, "content": content})
        
        return sections
    
    def _generate_guide_content(self, topic: str, keywords: List[str],
                                industry_data: Dict, word_count: int) -> List[Dict]:
        """Генерация контента типа guide"""
        sections = []
        
        guide_sections = [
            (f"What is {topic.capitalize()}?", f"{topic.capitalize()} refers to the process or system that enables specific outcomes. Understanding the definition is the first step to mastery."),
            (f"Why {topic.capitalize()} Matters", f"The importance of {topic} cannot be overstated. It impacts efficiency, results, and overall success in numerous ways."),
            (f"How {topic.capitalize()} Works", f"Understanding the mechanics of {topic} helps you use it more effectively. Let's break down the key components and processes."),
            ("Key Benefits", f"Implementing {topic} properly brings numerous advantages. From improved efficiency to better outcomes, the benefits are substantial."),
            ("Best Practices", f"Follow these proven best practices to maximize your success with {topic}. These recommendations come from industry experts and real-world experience."),
            ("Common Mistakes to Avoid", f"Avoid these common pitfalls when working with {topic}. Learning from others' mistakes saves time and resources."),
            ("Frequently Asked Questions", f"Here are answers to the most common questions about {topic}. If you have additional questions, don't hesitate to reach out.")
        ]
        
        for title, content in guide_sections:
            # Расширяем контент
            expanded = content
            
            # Добавляем списки для некоторых секций
            if "Benefits" in title:
                benefits = industry_data.get("benefits", ["efficiency", "effectiveness", "savings"])
                benefit_list = "\n".join([f"- **{b.capitalize()}**: Significant improvement in this area" for b in benefits[:5]])
                expanded += f"\n\n{benefit_list}"
            
            if "Mistakes" in title:
                pain_points = industry_data.get("pain_points", ["complexity", "cost", "time"])
                mistake_list = "\n".join([f"- Underestimating {p}" for p in pain_points[:4]])
                expanded += f"\n\nCommon mistakes include:\n\n{mistake_list}"
            
            sections.append({"title": title, "content": expanded})
        
        return sections
    
    def get_generated_articles(self) -> List[Dict]:
        """Получение списка сгенерированных статей"""
        articles = []
        for file in self.generated_dir.glob("article_*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                articles.append(json.load(f))
        return sorted(articles, key=lambda x: x.get("generated_at", ""), reverse=True)


# Создаем глобальный экземпляр
autonomous_content_engine = AutonomousContentEngine()
