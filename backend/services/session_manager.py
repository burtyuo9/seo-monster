"""
Session Manager - Управление сессиями и аккаунтами
Позволяет сохранять и переиспользовать сессии после ручного входа
"""

import json
import os
import pickle
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path
import aiofiles
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SessionManager:
    """Менеджер сессий для хранения и переиспользования авторизаций"""
    
    def __init__(self, data_dir: str = "data/sessions"):
        self.data_dir = Path(data_dir)
        self.accounts_dir = self.data_dir / "accounts"
        self.cookies_dir = self.data_dir / "cookies"
        self.tokens_dir = self.data_dir / "tokens"
        
        # Создаем директории
        for dir_path in [self.data_dir, self.accounts_dir, self.cookies_dir, self.tokens_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Ключ шифрования (в продакшене должен храниться безопасно)
        self._init_encryption()
        
        # Кэш активных сессий
        self.active_sessions: Dict[str, Dict] = {}
        
        # Статистика
        self.stats = {
            "total_accounts": 0,
            "active_sessions": 0,
            "successful_logins": 0,
            "failed_logins": 0,
            "last_activity": None
        }
    
    def _init_encryption(self):
        """Инициализация шифрования для безопасного хранения данных"""
        key_file = self.data_dir / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, "rb") as f:
                self.encryption_key = f.read()
        else:
            # Генерируем новый ключ
            self.encryption_key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self.encryption_key)
            os.chmod(key_file, 0o600)  # Только владелец может читать
        
        self.cipher = Fernet(self.encryption_key)
    
    def _encrypt(self, data: str) -> bytes:
        """Шифрование данных"""
        return self.cipher.encrypt(data.encode())
    
    def _decrypt(self, encrypted_data: bytes) -> str:
        """Расшифровка данных"""
        return self.cipher.decrypt(encrypted_data).decode()
    
    def _get_account_id(self, platform: str, username: str) -> str:
        """Генерация уникального ID аккаунта"""
        return hashlib.md5(f"{platform}:{username}".encode()).hexdigest()[:16]
    
    async def add_account(self, platform: str, username: str, password: str, 
                         metadata: Optional[Dict] = None) -> Dict:
        """
        Добавление нового аккаунта
        
        Args:
            platform: Название платформы (google, youtube, tiktok, etc.)
            username: Логин/email
            password: Пароль
            metadata: Дополнительные данные (proxy, notes, etc.)
        
        Returns:
            Dict с информацией о добавленном аккаунте
        """
        account_id = self._get_account_id(platform, username)
        
        account_data = {
            "id": account_id,
            "platform": platform.lower(),
            "username": username,
            "password": self._encrypt(password).decode(),  # Шифруем пароль
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "login_count": 0,
            "status": "new",  # new, active, expired, blocked
            "session_valid": False
        }
        
        # Сохраняем аккаунт
        account_file = self.accounts_dir / f"{account_id}.json"
        async with aiofiles.open(account_file, "w") as f:
            await f.write(json.dumps(account_data, indent=2, ensure_ascii=False))
        
        self.stats["total_accounts"] += 1
        
        return {
            "id": account_id,
            "platform": platform,
            "username": username,
            "status": "added"
        }
    
    async def import_accounts_bulk(self, accounts_text: str, default_platform: str = "auto") -> Dict:
        """
        Массовый импорт аккаунтов
        
        Форматы:
        - platform:username:password
        - username:password (platform определяется автоматически)
        - email:password
        
        Args:
            accounts_text: Текст с аккаунтами (по одному на строку)
            default_platform: Платформа по умолчанию
        
        Returns:
            Статистика импорта
        """
        lines = accounts_text.strip().split("\n")
        results = {
            "imported": 0,
            "skipped": 0,
            "errors": [],
            "accounts": []
        }
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            parts = line.split(":")
            
            try:
                if len(parts) >= 3:
                    # Формат: platform:username:password
                    platform = parts[0]
                    username = parts[1]
                    password = ":".join(parts[2:])  # Пароль может содержать :
                elif len(parts) == 2:
                    # Формат: username:password
                    username = parts[0]
                    password = parts[1]
                    platform = self._detect_platform(username) if default_platform == "auto" else default_platform
                else:
                    results["skipped"] += 1
                    results["errors"].append(f"Invalid format: {line[:30]}...")
                    continue
                
                result = await self.add_account(platform, username, password)
                results["imported"] += 1
                results["accounts"].append(result)
                
            except Exception as e:
                results["skipped"] += 1
                results["errors"].append(f"Error: {str(e)}")
        
        return results
    
    def _detect_platform(self, username: str) -> str:
        """Автоматическое определение платформы по username/email"""
        username_lower = username.lower()
        
        if "@gmail.com" in username_lower or "@google.com" in username_lower:
            return "google"
        elif "@yahoo.com" in username_lower:
            return "yahoo"
        elif "@mail.ru" in username_lower or "@inbox.ru" in username_lower:
            return "mailru"
        elif "@yandex.ru" in username_lower or "@ya.ru" in username_lower:
            return "yandex"
        elif "@outlook.com" in username_lower or "@hotmail.com" in username_lower:
            return "microsoft"
        else:
            return "generic"
    
    async def save_session(self, account_id: str, cookies: List[Dict], 
                          local_storage: Optional[Dict] = None,
                          session_storage: Optional[Dict] = None) -> bool:
        """
        Сохранение сессии после успешного входа
        
        Args:
            account_id: ID аккаунта
            cookies: Список cookies из браузера
            local_storage: Данные localStorage
            session_storage: Данные sessionStorage
        
        Returns:
            True если успешно сохранено
        """
        session_data = {
            "account_id": account_id,
            "cookies": cookies,
            "local_storage": local_storage or {},
            "session_storage": session_storage or {},
            "saved_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
            "valid": True
        }
        
        # Шифруем и сохраняем
        encrypted = self._encrypt(json.dumps(session_data))
        session_file = self.cookies_dir / f"{account_id}.session"
        
        async with aiofiles.open(session_file, "wb") as f:
            await f.write(encrypted)
        
        # Обновляем статус аккаунта
        await self._update_account_status(account_id, "active", session_valid=True)
        
        # Добавляем в кэш
        self.active_sessions[account_id] = session_data
        self.stats["active_sessions"] = len(self.active_sessions)
        self.stats["successful_logins"] += 1
        self.stats["last_activity"] = datetime.now().isoformat()
        
        return True
    
    async def load_session(self, account_id: str) -> Optional[Dict]:
        """
        Загрузка сохраненной сессии
        
        Args:
            account_id: ID аккаунта
        
        Returns:
            Данные сессии или None если не найдена/истекла
        """
        # Проверяем кэш
        if account_id in self.active_sessions:
            session = self.active_sessions[account_id]
            if datetime.fromisoformat(session["expires_at"]) > datetime.now():
                return session
        
        # Загружаем из файла
        session_file = self.cookies_dir / f"{account_id}.session"
        
        if not session_file.exists():
            return None
        
        try:
            async with aiofiles.open(session_file, "rb") as f:
                encrypted = await f.read()
            
            session_data = json.loads(self._decrypt(encrypted))
            
            # Проверяем срок действия
            if datetime.fromisoformat(session_data["expires_at"]) < datetime.now():
                session_data["valid"] = False
                await self._update_account_status(account_id, "expired", session_valid=False)
                return None
            
            # Добавляем в кэш
            self.active_sessions[account_id] = session_data
            
            return session_data
            
        except Exception as e:
            print(f"Error loading session {account_id}: {e}")
            return None
    
    async def get_account(self, account_id: str) -> Optional[Dict]:
        """Получение информации об аккаунте"""
        account_file = self.accounts_dir / f"{account_id}.json"
        
        if not account_file.exists():
            return None
        
        async with aiofiles.open(account_file, "r") as f:
            account_data = json.loads(await f.read())
        
        # Расшифровываем пароль для использования
        account_data["password"] = self._decrypt(account_data["password"].encode())
        
        return account_data
    
    async def list_accounts(self, platform: Optional[str] = None, 
                           status: Optional[str] = None) -> List[Dict]:
        """
        Получение списка аккаунтов
        
        Args:
            platform: Фильтр по платформе
            status: Фильтр по статусу
        
        Returns:
            Список аккаунтов (без паролей)
        """
        accounts = []
        
        for account_file in self.accounts_dir.glob("*.json"):
            async with aiofiles.open(account_file, "r") as f:
                account = json.loads(await f.read())
            
            # Применяем фильтры
            if platform and account["platform"] != platform.lower():
                continue
            if status and account["status"] != status:
                continue
            
            # Убираем пароль из вывода
            account.pop("password", None)
            accounts.append(account)
        
        return accounts
    
    async def _update_account_status(self, account_id: str, status: str, 
                                     session_valid: bool = None):
        """Обновление статуса аккаунта"""
        account_file = self.accounts_dir / f"{account_id}.json"
        
        if not account_file.exists():
            return
        
        async with aiofiles.open(account_file, "r") as f:
            account = json.loads(await f.read())
        
        account["status"] = status
        account["last_login"] = datetime.now().isoformat()
        account["login_count"] += 1
        
        if session_valid is not None:
            account["session_valid"] = session_valid
        
        async with aiofiles.open(account_file, "w") as f:
            await f.write(json.dumps(account, indent=2, ensure_ascii=False))
    
    async def delete_account(self, account_id: str) -> bool:
        """Удаление аккаунта и его сессии"""
        account_file = self.accounts_dir / f"{account_id}.json"
        session_file = self.cookies_dir / f"{account_id}.session"
        
        deleted = False
        
        if account_file.exists():
            os.remove(account_file)
            deleted = True
        
        if session_file.exists():
            os.remove(session_file)
        
        if account_id in self.active_sessions:
            del self.active_sessions[account_id]
        
        return deleted
    
    async def get_random_active_session(self, platform: str) -> Optional[Dict]:
        """
        Получение случайной активной сессии для платформы
        
        Args:
            platform: Название платформы
        
        Returns:
            Данные сессии с аккаунтом
        """
        import random
        
        accounts = await self.list_accounts(platform=platform, status="active")
        active_accounts = [a for a in accounts if a.get("session_valid")]
        
        if not active_accounts:
            return None
        
        account = random.choice(active_accounts)
        session = await self.load_session(account["id"])
        
        if session:
            return {
                "account": account,
                "session": session
            }
        
        return None
    
    async def export_sessions(self, output_file: str) -> str:
        """Экспорт всех сессий для бэкапа"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "accounts": [],
            "sessions": []
        }
        
        # Экспортируем аккаунты
        for account_file in self.accounts_dir.glob("*.json"):
            async with aiofiles.open(account_file, "r") as f:
                export_data["accounts"].append(json.loads(await f.read()))
        
        # Экспортируем сессии
        for session_file in self.cookies_dir.glob("*.session"):
            async with aiofiles.open(session_file, "rb") as f:
                export_data["sessions"].append({
                    "id": session_file.stem,
                    "data": base64.b64encode(await f.read()).decode()
                })
        
        # Сохраняем
        async with aiofiles.open(output_file, "w") as f:
            await f.write(json.dumps(export_data, indent=2, ensure_ascii=False))
        
        return output_file
    
    async def import_sessions(self, input_file: str) -> Dict:
        """Импорт сессий из бэкапа"""
        async with aiofiles.open(input_file, "r") as f:
            import_data = json.loads(await f.read())
        
        results = {"accounts": 0, "sessions": 0}
        
        # Импортируем аккаунты
        for account in import_data.get("accounts", []):
            account_file = self.accounts_dir / f"{account['id']}.json"
            async with aiofiles.open(account_file, "w") as f:
                await f.write(json.dumps(account, indent=2, ensure_ascii=False))
            results["accounts"] += 1
        
        # Импортируем сессии
        for session in import_data.get("sessions", []):
            session_file = self.cookies_dir / f"{session['id']}.session"
            async with aiofiles.open(session_file, "wb") as f:
                await f.write(base64.b64decode(session["data"]))
            results["sessions"] += 1
        
        return results
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        self.stats["total_accounts"] = len(list(self.accounts_dir.glob("*.json")))
        self.stats["active_sessions"] = len(list(self.cookies_dir.glob("*.session")))
        return self.stats


# Глобальный экземпляр
session_manager = SessionManager()
