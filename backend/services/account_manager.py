"""
SEO Monster - Account Manager
Расширенный менеджер аккаунтов с поддержкой баз данных и cookies
"""

import json
import csv
import base64
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    NEEDS_VERIFICATION = "needs_verification"
    COOLDOWN = "cooldown"
    ERROR = "error"


class AccountType(str, Enum):
    SOCIAL = "social"
    FORUM = "forum"
    BLOG = "blog"
    DIRECTORY = "directory"
    COMMENT = "comment"
    OTHER = "other"


@dataclass
class Account:
    id: str
    platform: str
    username: str
    password: str  # Зашифрованный
    email: Optional[str] = None
    phone: Optional[str] = None
    status: AccountStatus = AccountStatus.ACTIVE
    account_type: AccountType = AccountType.OTHER
    cookies: Optional[str] = None  # Зашифрованные cookies в JSON
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = None
    last_used: Optional[str] = None
    last_login: Optional[str] = None
    posts_count: int = 0
    success_rate: float = 100.0
    cooldown_until: Optional[str] = None
    extra_data: Optional[Dict] = None


class AccountManager:
    """
    Расширенный менеджер аккаунтов
    
    Возможности:
    - Импорт из различных форматов (TXT, CSV, JSON)
    - Работа с cookies (загрузка/сохранение/экспорт)
    - Шифрование паролей и cookies
    - Ротация аккаунтов
    - Управление cooldown
    - Статистика использования
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "data/accounts")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Директории
        self.cookies_dir = self.data_dir / "cookies"
        self.cookies_dir.mkdir(exist_ok=True)
        
        self.imports_dir = self.data_dir / "imports"
        self.imports_dir.mkdir(exist_ok=True)
        
        # Файлы данных
        self.accounts_file = self.data_dir / "accounts.json"
        self.stats_file = self.data_dir / "stats.json"
        
        # Ключ шифрования
        self.key_file = self.data_dir / ".encryption_key"
        self.cipher = self._init_encryption()
        
        # Загружаем данные
        self.accounts: Dict[str, Account] = self._load_accounts()
        self.stats: Dict = self._load_json(self.stats_file, {
            "total_imports": 0,
            "total_accounts": 0,
            "total_posts": 0,
            "platforms": {}
        })
    
    def _init_encryption(self) -> Fernet:
        """Инициализация шифрования"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        return Fernet(key)
    
    def _encrypt(self, data: str) -> str:
        """Шифрование данных"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """Расшифровка данных"""
        try:
            return self.cipher.decrypt(data.encode()).decode()
        except:
            return data  # Возвращаем как есть если не зашифровано
    
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
    
    def _load_accounts(self) -> Dict[str, Account]:
        """Загрузка аккаунтов"""
        data = self._load_json(self.accounts_file, {})
        accounts = {}
        for aid, adata in data.items():
            accounts[aid] = Account(**adata)
        return accounts
    
    def _save_accounts(self):
        """Сохранение аккаунтов"""
        data = {aid: asdict(a) for aid, a in self.accounts.items()}
        self._save_json(self.accounts_file, data)
    
    def _generate_id(self, platform: str, username: str) -> str:
        """Генерация уникального ID"""
        raw = f"{platform}:{username}:{datetime.now().isoformat()}"
        return hashlib.md5(raw.encode()).hexdigest()[:16]
    
    # ==================== ИМПОРТ ====================
    
    def import_from_text(
        self, 
        content: str, 
        format_type: str = "platform:username:password",
        default_platform: str = None
    ) -> Tuple[int, int, List[str]]:
        """
        Импорт аккаунтов из текста
        
        Поддерживаемые форматы:
        - platform:username:password
        - username:password (требует default_platform)
        - platform:username:password:email
        - platform:username:password:email:proxy
        - JSON строки
        
        Returns:
            (imported, skipped, errors)
        """
        imported = 0
        skipped = 0
        errors = []
        
        lines = content.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                # Пробуем JSON
                if line.startswith('{'):
                    data = json.loads(line)
                    account = self._create_account_from_dict(data)
                else:
                    # Парсим по разделителю
                    parts = line.split(':')
                    
                    if len(parts) >= 3:
                        platform, username, password = parts[0], parts[1], parts[2]
                        email = parts[3] if len(parts) > 3 else None
                        proxy = parts[4] if len(parts) > 4 else None
                    elif len(parts) == 2 and default_platform:
                        platform = default_platform
                        username, password = parts[0], parts[1]
                        email = None
                        proxy = None
                    else:
                        errors.append(f"Строка {line_num}: неверный формат")
                        skipped += 1
                        continue
                    
                    account = Account(
                        id=self._generate_id(platform, username),
                        platform=platform.lower(),
                        username=username,
                        password=self._encrypt(password),
                        email=email,
                        proxy=proxy,
                        created_at=datetime.now().isoformat()
                    )
                
                # Проверяем дубликаты
                existing = self._find_account(account.platform, account.username)
                if existing:
                    skipped += 1
                    continue
                
                self.accounts[account.id] = account
                imported += 1
                
            except Exception as e:
                errors.append(f"Строка {line_num}: {str(e)}")
                skipped += 1
        
        self._save_accounts()
        self._update_stats("import", imported)
        
        return imported, skipped, errors
    
    def import_from_csv(self, file_path: str) -> Tuple[int, int, List[str]]:
        """
        Импорт из CSV файла
        
        Ожидаемые колонки: platform, username, password, email, proxy, cookies
        """
        imported = 0
        skipped = 0
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        platform = row.get('platform', '').lower()
                        username = row.get('username', '')
                        password = row.get('password', '')
                        
                        if not platform or not username:
                            errors.append(f"Строка {row_num}: отсутствует platform или username")
                            skipped += 1
                            continue
                        
                        # Проверяем дубликаты
                        if self._find_account(platform, username):
                            skipped += 1
                            continue
                        
                        account = Account(
                            id=self._generate_id(platform, username),
                            platform=platform,
                            username=username,
                            password=self._encrypt(password) if password else "",
                            email=row.get('email'),
                            proxy=row.get('proxy'),
                            cookies=self._encrypt(row.get('cookies', '')) if row.get('cookies') else None,
                            created_at=datetime.now().isoformat()
                        )
                        
                        self.accounts[account.id] = account
                        imported += 1
                        
                    except Exception as e:
                        errors.append(f"Строка {row_num}: {str(e)}")
                        skipped += 1
        
        except Exception as e:
            errors.append(f"Ошибка чтения файла: {str(e)}")
        
        self._save_accounts()
        self._update_stats("import", imported)
        
        return imported, skipped, errors
    
    def import_from_json(self, file_path: str) -> Tuple[int, int, List[str]]:
        """Импорт из JSON файла"""
        imported = 0
        skipped = 0
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Поддерживаем массив или объект
            if isinstance(data, list):
                accounts_data = data
            elif isinstance(data, dict):
                accounts_data = data.get('accounts', [data])
            else:
                errors.append("Неверный формат JSON")
                return 0, 0, errors
            
            for idx, acc_data in enumerate(accounts_data):
                try:
                    account = self._create_account_from_dict(acc_data)
                    
                    if self._find_account(account.platform, account.username):
                        skipped += 1
                        continue
                    
                    self.accounts[account.id] = account
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Запись {idx}: {str(e)}")
                    skipped += 1
        
        except Exception as e:
            errors.append(f"Ошибка чтения файла: {str(e)}")
        
        self._save_accounts()
        self._update_stats("import", imported)
        
        return imported, skipped, errors
    
    def _create_account_from_dict(self, data: Dict) -> Account:
        """Создание аккаунта из словаря"""
        platform = data.get('platform', 'unknown').lower()
        username = data.get('username', data.get('login', data.get('user', '')))
        password = data.get('password', data.get('pass', ''))
        
        return Account(
            id=self._generate_id(platform, username),
            platform=platform,
            username=username,
            password=self._encrypt(password),
            email=data.get('email'),
            phone=data.get('phone'),
            proxy=data.get('proxy'),
            cookies=self._encrypt(json.dumps(data.get('cookies', {}))) if data.get('cookies') else None,
            user_agent=data.get('user_agent'),
            notes=data.get('notes'),
            created_at=datetime.now().isoformat(),
            extra_data=data.get('extra_data')
        )
    
    def _find_account(self, platform: str, username: str) -> Optional[Account]:
        """Поиск аккаунта по платформе и username"""
        for account in self.accounts.values():
            if account.platform == platform.lower() and account.username == username:
                return account
        return None
    
    # ==================== COOKIES ====================
    
    def import_cookies_from_file(self, account_id: str, file_path: str) -> bool:
        """
        Импорт cookies из файла
        
        Поддерживаемые форматы:
        - JSON (Netscape/Chrome формат)
        - Текстовый Netscape формат
        """
        if account_id not in self.accounts:
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Пробуем JSON
            try:
                cookies = json.loads(content)
                if isinstance(cookies, list):
                    # Chrome/Netscape JSON формат
                    cookies_dict = {c.get('name', c.get('Name', '')): c.get('value', c.get('Value', '')) for c in cookies}
                else:
                    cookies_dict = cookies
            except json.JSONDecodeError:
                # Netscape текстовый формат
                cookies_dict = self._parse_netscape_cookies(content)
            
            # Сохраняем
            self.accounts[account_id].cookies = self._encrypt(json.dumps(cookies_dict))
            self._save_accounts()
            
            # Сохраняем копию в файл
            cookie_file = self.cookies_dir / f"{account_id}.json"
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error importing cookies: {e}")
            return False
    
    def import_cookies_from_text(self, account_id: str, cookies_text: str) -> bool:
        """Импорт cookies из текста"""
        if account_id not in self.accounts:
            return False
        
        try:
            # Пробуем JSON
            try:
                cookies = json.loads(cookies_text)
                if isinstance(cookies, list):
                    cookies_dict = {c.get('name', ''): c.get('value', '') for c in cookies}
                else:
                    cookies_dict = cookies
            except:
                # Пробуем key=value формат
                cookies_dict = {}
                for part in cookies_text.split(';'):
                    if '=' in part:
                        key, value = part.strip().split('=', 1)
                        cookies_dict[key] = value
            
            self.accounts[account_id].cookies = self._encrypt(json.dumps(cookies_dict))
            self._save_accounts()
            
            return True
            
        except Exception as e:
            logger.error(f"Error importing cookies from text: {e}")
            return False
    
    def _parse_netscape_cookies(self, content: str) -> Dict:
        """Парсинг Netscape формата cookies"""
        cookies = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('\t')
            if len(parts) >= 7:
                name = parts[5]
                value = parts[6]
                cookies[name] = value
        
        return cookies
    
    def get_cookies(self, account_id: str) -> Optional[Dict]:
        """Получение cookies аккаунта"""
        if account_id not in self.accounts:
            return None
        
        cookies_encrypted = self.accounts[account_id].cookies
        if not cookies_encrypted:
            return None
        
        try:
            return json.loads(self._decrypt(cookies_encrypted))
        except:
            return None
    
    def export_cookies(self, account_id: str, format_type: str = "json") -> Optional[str]:
        """
        Экспорт cookies
        
        Форматы: json, netscape, header
        """
        cookies = self.get_cookies(account_id)
        if not cookies:
            return None
        
        if format_type == "json":
            return json.dumps(cookies, indent=2)
        
        elif format_type == "netscape":
            lines = ["# Netscape HTTP Cookie File"]
            for name, value in cookies.items():
                lines.append(f".domain.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}")
            return '\n'.join(lines)
        
        elif format_type == "header":
            return '; '.join([f"{k}={v}" for k, v in cookies.items()])
        
        return None
    
    def bulk_import_cookies(self, cookies_dir: str) -> Tuple[int, int]:
        """
        Массовый импорт cookies из директории
        
        Ожидает файлы в формате: platform_username.json или account_id.json
        """
        imported = 0
        failed = 0
        
        path = Path(cookies_dir)
        if not path.exists():
            return 0, 0
        
        for cookie_file in path.glob("*.json"):
            try:
                # Пытаемся найти аккаунт по имени файла
                filename = cookie_file.stem
                
                # Формат: platform_username
                if '_' in filename:
                    platform, username = filename.split('_', 1)
                    account = self._find_account(platform, username)
                else:
                    # Формат: account_id
                    account = self.accounts.get(filename)
                
                if account:
                    if self.import_cookies_from_file(account.id, str(cookie_file)):
                        imported += 1
                    else:
                        failed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Error importing {cookie_file}: {e}")
                failed += 1
        
        return imported, failed
    
    # ==================== УПРАВЛЕНИЕ ====================
    
    def get_account(self, account_id: str, decrypt: bool = False) -> Optional[Dict]:
        """Получение аккаунта"""
        if account_id not in self.accounts:
            return None
        
        account = self.accounts[account_id]
        data = asdict(account)
        
        if decrypt:
            data['password'] = self._decrypt(account.password)
            if account.cookies:
                data['cookies'] = json.loads(self._decrypt(account.cookies))
        
        return data
    
    def get_accounts(
        self, 
        platform: str = None, 
        status: str = None,
        account_type: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Получение списка аккаунтов с фильтрацией"""
        
        filtered = list(self.accounts.values())
        
        if platform:
            filtered = [a for a in filtered if a.platform == platform.lower()]
        
        if status:
            filtered = [a for a in filtered if a.status.value == status]
        
        if account_type:
            filtered = [a for a in filtered if a.account_type.value == account_type]
        
        # Сортируем по дате создания
        filtered.sort(key=lambda x: x.created_at or "", reverse=True)
        
        # Пагинация
        paginated = filtered[offset:offset + limit]
        
        # Возвращаем без паролей
        return [
            {
                "id": a.id,
                "platform": a.platform,
                "username": a.username,
                "email": a.email,
                "status": a.status.value if hasattr(a.status, 'value') else a.status,
                "account_type": a.account_type.value if hasattr(a.account_type, 'value') else a.account_type,
                "has_cookies": bool(a.cookies),
                "has_proxy": bool(a.proxy),
                "posts_count": a.posts_count,
                "success_rate": a.success_rate,
                "last_used": a.last_used,
                "created_at": a.created_at
            }
            for a in paginated
        ]
    
    def get_next_account(self, platform: str) -> Optional[Dict]:
        """
        Получение следующего доступного аккаунта для использования
        
        Учитывает:
        - Статус (только active)
        - Cooldown
        - Ротацию (выбирает наименее использованный)
        """
        now = datetime.now()
        
        available = []
        for account in self.accounts.values():
            if account.platform != platform.lower():
                continue
            
            if account.status != AccountStatus.ACTIVE:
                continue
            
            # Проверяем cooldown
            if account.cooldown_until:
                cooldown_end = datetime.fromisoformat(account.cooldown_until)
                if now < cooldown_end:
                    continue
            
            available.append(account)
        
        if not available:
            return None
        
        # Сортируем по количеству использований (меньше = лучше)
        available.sort(key=lambda x: (x.posts_count, x.last_used or ""))
        
        account = available[0]
        
        # Возвращаем с расшифрованными данными
        return {
            "id": account.id,
            "platform": account.platform,
            "username": account.username,
            "password": self._decrypt(account.password),
            "email": account.email,
            "proxy": account.proxy,
            "user_agent": account.user_agent,
            "cookies": json.loads(self._decrypt(account.cookies)) if account.cookies else None
        }
    
    def mark_used(self, account_id: str, success: bool = True):
        """Отметка использования аккаунта"""
        if account_id not in self.accounts:
            return
        
        account = self.accounts[account_id]
        account.last_used = datetime.now().isoformat()
        account.posts_count += 1
        
        # Обновляем success rate
        total = account.posts_count
        if success:
            account.success_rate = ((account.success_rate * (total - 1)) + 100) / total
        else:
            account.success_rate = ((account.success_rate * (total - 1)) + 0) / total
        
        self._save_accounts()
        self._update_stats("post", 1)
    
    def set_cooldown(self, account_id: str, minutes: int):
        """Установка cooldown для аккаунта"""
        if account_id not in self.accounts:
            return
        
        from datetime import timedelta
        cooldown_end = datetime.now() + timedelta(minutes=minutes)
        self.accounts[account_id].cooldown_until = cooldown_end.isoformat()
        self.accounts[account_id].status = AccountStatus.COOLDOWN
        self._save_accounts()
    
    def set_status(self, account_id: str, status: str):
        """Установка статуса аккаунта"""
        if account_id not in self.accounts:
            return False
        
        try:
            self.accounts[account_id].status = AccountStatus(status)
            self._save_accounts()
            return True
        except:
            return False
    
    def delete_account(self, account_id: str) -> bool:
        """Удаление аккаунта"""
        if account_id in self.accounts:
            del self.accounts[account_id]
            self._save_accounts()
            
            # Удаляем cookies файл
            cookie_file = self.cookies_dir / f"{account_id}.json"
            if cookie_file.exists():
                cookie_file.unlink()
            
            return True
        return False
    
    def delete_by_platform(self, platform: str) -> int:
        """Удаление всех аккаунтов платформы"""
        to_delete = [aid for aid, a in self.accounts.items() if a.platform == platform.lower()]
        
        for aid in to_delete:
            self.delete_account(aid)
        
        return len(to_delete)
    
    # ==================== ЭКСПОРТ ====================
    
    def export_accounts(self, format_type: str = "json", platform: str = None) -> str:
        """
        Экспорт аккаунтов
        
        Форматы: json, csv, text
        """
        accounts = list(self.accounts.values())
        
        if platform:
            accounts = [a for a in accounts if a.platform == platform.lower()]
        
        if format_type == "json":
            data = []
            for a in accounts:
                data.append({
                    "platform": a.platform,
                    "username": a.username,
                    "password": self._decrypt(a.password),
                    "email": a.email,
                    "proxy": a.proxy,
                    "cookies": json.loads(self._decrypt(a.cookies)) if a.cookies else None
                })
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        elif format_type == "csv":
            lines = ["platform,username,password,email,proxy"]
            for a in accounts:
                lines.append(f"{a.platform},{a.username},{self._decrypt(a.password)},{a.email or ''},{a.proxy or ''}")
            return '\n'.join(lines)
        
        elif format_type == "text":
            lines = []
            for a in accounts:
                lines.append(f"{a.platform}:{a.username}:{self._decrypt(a.password)}")
            return '\n'.join(lines)
        
        return ""
    
    # ==================== СТАТИСТИКА ====================
    
    def _update_stats(self, action: str, count: int):
        """Обновление статистики"""
        if action == "import":
            self.stats["total_imports"] += 1
            self.stats["total_accounts"] = len(self.accounts)
        elif action == "post":
            self.stats["total_posts"] += count
        
        # Обновляем статистику по платформам
        for account in self.accounts.values():
            platform = account.platform
            if platform not in self.stats["platforms"]:
                self.stats["platforms"][platform] = {"count": 0, "posts": 0}
            self.stats["platforms"][platform]["count"] = len([a for a in self.accounts.values() if a.platform == platform])
        
        self._save_json(self.stats_file, self.stats)
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        return {
            "total_accounts": len(self.accounts),
            "total_imports": self.stats.get("total_imports", 0),
            "total_posts": self.stats.get("total_posts", 0),
            "platforms": self.stats.get("platforms", {}),
            "by_status": {
                "active": len([a for a in self.accounts.values() if a.status == AccountStatus.ACTIVE]),
                "inactive": len([a for a in self.accounts.values() if a.status == AccountStatus.INACTIVE]),
                "banned": len([a for a in self.accounts.values() if a.status == AccountStatus.BANNED]),
                "cooldown": len([a for a in self.accounts.values() if a.status == AccountStatus.COOLDOWN])
            },
            "with_cookies": len([a for a in self.accounts.values() if a.cookies]),
            "with_proxy": len([a for a in self.accounts.values() if a.proxy])
        }


# Глобальный экземпляр
_account_manager = None

def get_account_manager() -> AccountManager:
    """Получение глобального экземпляра"""
    global _account_manager
    if _account_manager is None:
        _account_manager = AccountManager()
    return _account_manager
