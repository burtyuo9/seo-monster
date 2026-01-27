"""
Recipient Manager - Управление базами получателей для рассылок
"""

import json
import os
import re
import hashlib
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


@dataclass
class RecipientList:
    id: str
    name: str
    description: str
    file_type: str
    file_path: str
    total_count: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    fields: List[str]
    sample_data: List[Dict]
    created_at: str
    last_used: str
    status: str


class RecipientManager:
    def __init__(self):
        self.data_dir = "/home/ubuntu/seo_monster/backend/data"
        self.lists_file = f"{self.data_dir}/recipient_lists.json"
        self.uploads_dir = f"{self.data_dir}/recipient_uploads"
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        self.lists: Dict[str, RecipientList] = {}
        self._load_data()
        
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def _load_data(self):
        if os.path.exists(self.lists_file):
            with open(self.lists_file, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    self.lists[k] = RecipientList(**v)
    
    def _save_data(self):
        with open(self.lists_file, 'w') as f:
            data = {k: asdict(v) for k, v in self.lists.items()}
            json.dump(data, f, indent=2)
    
    def _generate_id(self) -> str:
        return hashlib.md5(f"{datetime.now().isoformat()}{os.urandom(8).hex()}".encode()).hexdigest()[:12]
    
    def _validate_email(self, email: str) -> bool:
        if not email:
            return False
        return bool(self.email_pattern.match(str(email).strip().lower()))
    
    def _detect_file_type(self, filename: str) -> str:
        ext = filename.lower().split('.')[-1]
        return {'csv': 'csv', 'txt': 'txt', 'xlsx': 'xlsx', 'xls': 'xlsx', 'json': 'json'}.get(ext, 'unknown')
    
    def upload_list(self, file_path: str, name: str, description: str = "",
                    email_column: str = "email", delimiter: str = ",") -> Dict:
        """Загрузка базы получателей из файла"""
        
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        
        file_type = self._detect_file_type(file_path)
        if file_type == 'unknown':
            return {"success": False, "error": "Unsupported file format"}
        
        try:
            recipients = []
            fields = []
            
            if file_type == 'csv' or file_type == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    fields = reader.fieldnames or []
                    for row in reader:
                        recipients.append(row)
            
            elif file_type == 'xlsx' and PANDAS_AVAILABLE:
                df = pd.read_excel(file_path)
                fields = list(df.columns)
                recipients = df.to_dict('records')
            
            elif file_type == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        recipients = data
                        if recipients:
                            fields = list(recipients[0].keys())
            
            # Validate emails
            valid_count = 0
            invalid_count = 0
            seen_emails = set()
            duplicate_count = 0
            
            email_col = email_column if email_column in fields else (fields[0] if fields else 'email')
            
            for r in recipients:
                email = str(r.get(email_col, '')).strip().lower()
                if email in seen_emails:
                    duplicate_count += 1
                elif self._validate_email(email):
                    valid_count += 1
                    seen_emails.add(email)
                else:
                    invalid_count += 1
            
            # Save to uploads dir
            list_id = self._generate_id()
            saved_path = f"{self.uploads_dir}/{list_id}_{os.path.basename(file_path)}"
            
            import shutil
            shutil.copy(file_path, saved_path)
            
            recipient_list = RecipientList(
                id=list_id,
                name=name,
                description=description,
                file_type=file_type,
                file_path=saved_path,
                total_count=len(recipients),
                valid_count=valid_count,
                invalid_count=invalid_count,
                duplicate_count=duplicate_count,
                fields=fields,
                sample_data=recipients[:5],
                created_at=datetime.now().isoformat(),
                last_used="",
                status="ready"
            )
            
            self.lists[list_id] = recipient_list
            self._save_data()
            
            return {"success": True, "list": asdict(recipient_list)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_list_manual(self, name: str, emails: List[str], description: str = "") -> Dict:
        """Создание списка вручную"""
        list_id = self._generate_id()
        
        valid_count = 0
        invalid_count = 0
        seen = set()
        duplicate_count = 0
        recipients = []
        
        for email in emails:
            email = email.strip().lower()
            if email in seen:
                duplicate_count += 1
            elif self._validate_email(email):
                valid_count += 1
                seen.add(email)
                recipients.append({"email": email})
            else:
                invalid_count += 1
        
        # Save to file
        file_path = f"{self.uploads_dir}/{list_id}_manual.json"
        with open(file_path, 'w') as f:
            json.dump(recipients, f)
        
        recipient_list = RecipientList(
            id=list_id,
            name=name,
            description=description,
            file_type="json",
            file_path=file_path,
            total_count=len(emails),
            valid_count=valid_count,
            invalid_count=invalid_count,
            duplicate_count=duplicate_count,
            fields=["email"],
            sample_data=recipients[:5],
            created_at=datetime.now().isoformat(),
            last_used="",
            status="ready"
        )
        
        self.lists[list_id] = recipient_list
        self._save_data()
        
        return {"success": True, "list": asdict(recipient_list)}
    
    def get_all_lists(self) -> List[Dict]:
        return [asdict(l) for l in self.lists.values()]
    
    def get_list(self, list_id: str) -> Optional[Dict]:
        if list_id in self.lists:
            return asdict(self.lists[list_id])
        return None
    
    def get_recipients(self, list_id: str, limit: int = 100, offset: int = 0) -> Dict:
        """Получение получателей из списка"""
        if list_id not in self.lists:
            return {"success": False, "error": "List not found"}
        
        lst = self.lists[list_id]
        
        try:
            recipients = []
            
            if lst.file_type == 'json':
                with open(lst.file_path, 'r') as f:
                    all_recipients = json.load(f)
                    recipients = all_recipients[offset:offset+limit]
            
            elif lst.file_type in ['csv', 'txt']:
                with open(lst.file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        if i >= offset and i < offset + limit:
                            recipients.append(row)
                        if i >= offset + limit:
                            break
            
            return {
                "success": True,
                "recipients": recipients,
                "total": lst.total_count,
                "offset": offset,
                "limit": limit
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_list(self, list_id: str) -> bool:
        if list_id in self.lists:
            lst = self.lists[list_id]
            if os.path.exists(lst.file_path):
                os.remove(lst.file_path)
            del self.lists[list_id]
            self._save_data()
            return True
        return False
    
    def get_stats(self) -> Dict:
        total_lists = len(self.lists)
        total_recipients = sum(l.valid_count for l in self.lists.values())
        return {
            "total_lists": total_lists,
            "total_recipients": total_recipients,
            "lists_by_type": {}
        }


# Глобальный экземпляр
recipient_manager = RecipientManager()
