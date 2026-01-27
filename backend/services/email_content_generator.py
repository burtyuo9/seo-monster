"""
Email Content Generator - Генератор контента для email рассылок
"""

import json
import os
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    from openai import OpenAI
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


@dataclass
class EmailContent:
    id: str
    name: str
    subject: str
    preheader: str
    html_body: str
    text_body: str
    amp_body: Optional[str]
    format: str
    variables: List[str]
    attachments: List[Dict]
    created_at: str
    updated_at: str
    generated_by: str


class EmailContentGenerator:
    def __init__(self):
        self.data_dir = "/home/ubuntu/seo_monster/backend/data"
        self.content_file = f"{self.data_dir}/email_contents.json"
        self.uploads_dir = f"{self.data_dir}/email_uploads"
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        self.contents: Dict[str, EmailContent] = {}
        self._load_data()
        
        self.ai_client = None
        if AI_AVAILABLE:
            try:
                self.ai_client = OpenAI()
            except:
                pass
    
    def _load_data(self):
        if os.path.exists(self.content_file):
            with open(self.content_file, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    self.contents[k] = EmailContent(**v)
    
    def _save_data(self):
        with open(self.content_file, 'w') as f:
            data = {k: asdict(v) for k, v in self.contents.items()}
            json.dump(data, f, indent=2)
    
    def _generate_id(self) -> str:
        return hashlib.md5(f"{datetime.now().isoformat()}{os.urandom(8).hex()}".encode()).hexdigest()[:12]
    
    def _extract_variables(self, text: str) -> List[str]:
        pattern = r'\{\{(\w+)\}\}'
        return list(set(re.findall(pattern, text)))
    
    async def generate_content_ai(self, task: str, format_type: str = "html", 
                                   language: str = "ru", tone: str = "professional") -> Dict:
        """Генерация контента письма с помощью AI"""
        if not self.ai_client:
            return {"success": False, "error": "AI not available"}
        
        prompt = f"""Создай email письмо для рассылки:
Задание: {task}
Язык: {language}, Тон: {tone}, Формат: {format_type}

JSON ответ:
{{"subject": "Тема", "preheader": "Превью", "html_body": "HTML", "text_body": "Текст"}}
Используй {{{{name}}}}, {{{{email}}}} для персонализации."""

        try:
            response = self.ai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Эксперт по email маркетингу."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{[\s\S]*\}', content)
            
            if json_match:
                email_data = json.loads(json_match.group())
                content_id = self._generate_id()
                variables = self._extract_variables(
                    email_data.get('html_body', '') + email_data.get('text_body', '') + email_data.get('subject', '')
                )
                
                email_content = EmailContent(
                    id=content_id,
                    name=f"AI Generated - {task[:30]}",
                    subject=email_data.get('subject', ''),
                    preheader=email_data.get('preheader', ''),
                    html_body=email_data.get('html_body', ''),
                    text_body=email_data.get('text_body', ''),
                    amp_body=None,
                    format=format_type,
                    variables=variables,
                    attachments=[],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    generated_by="ai"
                )
                
                self.contents[content_id] = email_content
                self._save_data()
                
                return {"success": True, "content": asdict(email_content)}
            
            return {"success": False, "error": "Failed to parse AI response"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_content_manual(self, name: str, subject: str, html_body: str = "",
                              text_body: str = "", preheader: str = "",
                              format_type: str = "html") -> Dict:
        """Создание контента вручную"""
        content_id = self._generate_id()
        variables = self._extract_variables(html_body + text_body + subject)
        
        email_content = EmailContent(
            id=content_id,
            name=name,
            subject=subject,
            preheader=preheader,
            html_body=html_body,
            text_body=text_body,
            amp_body=None,
            format=format_type,
            variables=variables,
            attachments=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            generated_by="manual"
        )
        
        self.contents[content_id] = email_content
        self._save_data()
        
        return {"success": True, "content": asdict(email_content)}
    
    def upload_html_file(self, file_path: str, name: str) -> Dict:
        """Загрузка готового HTML файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Извлекаем subject из title если есть
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
            subject = title_match.group(1) if title_match else name
            
            # Создаем текстовую версию
            text_body = re.sub(r'<[^>]+>', '', html_content)
            text_body = re.sub(r'\s+', ' ', text_body).strip()
            
            return self.create_content_manual(
                name=name,
                subject=subject,
                html_body=html_content,
                text_body=text_body[:500],
                format_type="html"
            )
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_contents(self) -> List[Dict]:
        """Получение всех контентов"""
        return [asdict(c) for c in self.contents.values()]
    
    def get_content(self, content_id: str) -> Optional[Dict]:
        """Получение контента по ID"""
        if content_id in self.contents:
            return asdict(self.contents[content_id])
        return None
    
    def delete_content(self, content_id: str) -> bool:
        """Удаление контента"""
        if content_id in self.contents:
            del self.contents[content_id]
            self._save_data()
            return True
        return False
    
    def update_content(self, content_id: str, **kwargs) -> Dict:
        """Обновление контента"""
        if content_id not in self.contents:
            return {"success": False, "error": "Content not found"}
        
        content = self.contents[content_id]
        for key, value in kwargs.items():
            if hasattr(content, key):
                setattr(content, key, value)
        
        content.updated_at = datetime.now().isoformat()
        content.variables = self._extract_variables(
            content.html_body + content.text_body + content.subject
        )
        
        self._save_data()
        return {"success": True, "content": asdict(content)}
    
    def get_builtin_templates(self) -> List[Dict]:
        """Встроенные шаблоны писем"""
        return [
            {
                "id": "promo_sale",
                "name": "Промо - Распродажа",
                "category": "promotional",
                "preview": "Скидки до 50%! Только сегодня..."
            },
            {
                "id": "newsletter",
                "name": "Новостная рассылка",
                "category": "newsletter",
                "preview": "Последние новости и обновления"
            },
            {
                "id": "welcome",
                "name": "Приветственное письмо",
                "category": "transactional",
                "preview": "Добро пожаловать в нашу команду!"
            },
            {
                "id": "abandoned_cart",
                "name": "Брошенная корзина",
                "category": "promotional",
                "preview": "Вы забыли товары в корзине"
            },
            {
                "id": "feedback",
                "name": "Запрос отзыва",
                "category": "transactional",
                "preview": "Как вам наш сервис?"
            }
        ]


# Глобальный экземпляр
email_generator = EmailContentGenerator()
