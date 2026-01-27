"""
SEO Monster - Knowledge Loader
Загрузчик базы знаний для AI-агента
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeLoader:
    """
    Загрузчик базы знаний для AI-агента SEO Monster
    
    Загружает и индексирует все файлы знаний для использования в чате и автопилоте
    """
    
    def __init__(self, knowledge_dir: str = None):
        self.knowledge_dir = Path(knowledge_dir or "data/knowledge")
        self.knowledge_base: Dict[str, Any] = {}
        self.topics_index: Dict[str, List[str]] = {}
        self.prompts: Dict[str, str] = {}
        self.best_practices: Dict[str, List[str]] = {}
        
        # Загружаем базу знаний
        self._load_all()
    
    def _load_all(self):
        """Загрузка всех файлов знаний"""
        if not self.knowledge_dir.exists():
            logger.warning(f"Knowledge directory not found: {self.knowledge_dir}")
            return
        
        # Загружаем главный файл базы знаний
        kb_file = self.knowledge_dir / "ai_knowledge_base.json"
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
                
            # Извлекаем промпты и лучшие практики
            self.prompts = self.knowledge_base.get('prompts', {})
            self.best_practices = self.knowledge_base.get('best_practices', {})
        
        # Загружаем все markdown файлы
        self.knowledge_files = {}
        for md_file in self.knowledge_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.knowledge_files[md_file.stem] = content
                    
                    # Индексируем топики
                    self._index_topics(md_file.stem, content)
                    
            except Exception as e:
                logger.error(f"Error loading {md_file}: {e}")
        
        logger.info(f"Loaded {len(self.knowledge_files)} knowledge files")
    
    def _index_topics(self, file_name: str, content: str):
        """Индексация топиков из файла"""
        # Извлекаем заголовки
        import re
        headers = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        
        for header in headers:
            header_lower = header.lower()
            if header_lower not in self.topics_index:
                self.topics_index[header_lower] = []
            self.topics_index[header_lower].append(file_name)
    
    def get_knowledge_for_topic(self, topic: str) -> Optional[str]:
        """Получение знаний по топику"""
        topic_lower = topic.lower()
        
        # Поиск по индексу
        for indexed_topic, files in self.topics_index.items():
            if topic_lower in indexed_topic or indexed_topic in topic_lower:
                # Возвращаем контент первого найденного файла
                if files:
                    return self.knowledge_files.get(files[0])
        
        return None
    
    def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict]:
        """Поиск по базе знаний"""
        results = []
        query_lower = query.lower()
        query_words = query_lower.split()
        
        for file_name, content in self.knowledge_files.items():
            content_lower = content.lower()
            
            # Подсчет релевантности
            score = 0
            for word in query_words:
                score += content_lower.count(word)
            
            if score > 0:
                # Извлекаем релевантный фрагмент
                snippet = self._extract_snippet(content, query_words)
                
                results.append({
                    'file': file_name,
                    'score': score,
                    'snippet': snippet
                })
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:max_results]
    
    def _extract_snippet(self, content: str, query_words: List[str], context_chars: int = 200) -> str:
        """Извлечение релевантного фрагмента"""
        content_lower = content.lower()
        
        # Находим первое вхождение любого слова запроса
        best_pos = len(content)
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1 and pos < best_pos:
                best_pos = pos
        
        if best_pos == len(content):
            return content[:context_chars] + "..."
        
        # Извлекаем контекст вокруг найденного слова
        start = max(0, best_pos - context_chars // 2)
        end = min(len(content), best_pos + context_chars // 2)
        
        snippet = content[start:end]
        
        # Добавляем многоточия
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def get_prompt(self, prompt_name: str, **kwargs) -> Optional[str]:
        """Получение промпта по имени с подстановкой переменных"""
        prompt = self.prompts.get(prompt_name)
        if prompt and kwargs:
            try:
                prompt = prompt.format(**kwargs)
            except KeyError:
                pass
        return prompt
    
    def get_best_practices(self, area: str) -> List[str]:
        """Получение лучших практик для области"""
        return self.best_practices.get(area, [])
    
    def get_key_insights(self, area: str) -> List[str]:
        """Получение ключевых инсайтов для области"""
        knowledge_areas = self.knowledge_base.get('knowledge_areas', {})
        area_data = knowledge_areas.get(area, {})
        return area_data.get('key_insights', [])
    
    def get_api_endpoint(self, service: str) -> Optional[str]:
        """Получение API endpoint для сервиса"""
        endpoints = self.knowledge_base.get('api_endpoints', {})
        return endpoints.get(service)
    
    def get_rate_limit(self, service: str) -> Optional[str]:
        """Получение лимита запросов для сервиса"""
        limits = self.knowledge_base.get('rate_limits', {})
        return limits.get(service)
    
    def build_context_for_ai(self, task_type: str) -> str:
        """Построение контекста для AI на основе типа задачи"""
        context_parts = []
        
        # Определяем релевантные области знаний
        task_to_areas = {
            'seo': ['seo', 'content_marketing', 'indexing'],
            'content': ['content_marketing', 'seo'],
            'indexing': ['indexing', 'seo'],
            'traffic': ['traffic_arbitrage'],
            'wordpress': ['wordpress', 'cpanel'],
            'hosting': ['cpanel', 'wordpress'],
            'links': ['link_building', 'seo'],
            'automation': ['antidetect_proxy', 'traffic_arbitrage']
        }
        
        areas = task_to_areas.get(task_type, ['seo'])
        
        for area in areas:
            # Добавляем ключевые инсайты
            insights = self.get_key_insights(area)
            if insights:
                context_parts.append(f"\n### Ключевые знания по {area}:")
                for insight in insights[:5]:
                    context_parts.append(f"- {insight}")
            
            # Добавляем лучшие практики
            practices = self.get_best_practices(f"{area}_campaign")
            if practices:
                context_parts.append(f"\n### Лучшие практики:")
                for practice in practices[:5]:
                    context_parts.append(f"- {practice}")
        
        return "\n".join(context_parts)
    
    def get_full_knowledge_summary(self) -> Dict:
        """Получение полной сводки базы знаний"""
        return {
            'version': self.knowledge_base.get('version', 'unknown'),
            'last_updated': self.knowledge_base.get('last_updated', 'unknown'),
            'knowledge_areas': list(self.knowledge_base.get('knowledge_areas', {}).keys()),
            'files_loaded': list(self.knowledge_files.keys()),
            'total_topics': len(self.topics_index),
            'prompts_available': list(self.prompts.keys()),
            'best_practices_areas': list(self.best_practices.keys())
        }
    
    def reload(self):
        """Перезагрузка базы знаний"""
        self.knowledge_base = {}
        self.topics_index = {}
        self.prompts = {}
        self.best_practices = {}
        self.knowledge_files = {}
        self._load_all()
        logger.info("Knowledge base reloaded")


# Глобальный экземпляр
_knowledge_loader = None

def get_knowledge_loader(knowledge_dir: str = None) -> KnowledgeLoader:
    """Получение глобального экземпляра загрузчика знаний"""
    global _knowledge_loader
    if _knowledge_loader is None:
        _knowledge_loader = KnowledgeLoader(knowledge_dir)
    return _knowledge_loader
