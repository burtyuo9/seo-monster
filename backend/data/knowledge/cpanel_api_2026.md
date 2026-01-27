# cPanel UAPI - Полное руководство 2026

## Обзор

UAPI (Unified API) - основной API для работы с cPanel. Позволяет управлять аккаунтами, файлами, базами данных и настройками.

## Методы доступа к API

### 1. URL через браузер/HTTP
```
https://domain.com:2083/execute/Module/function?parameter=value
```

Порты:
- `2082` - HTTP (небезопасный)
- `2083` - HTTPS (безопасный)
- `2095` - Webmail HTTP
- `2096` - Webmail HTTPS

### 2. Командная строка
```bash
uapi --user=username --output=json Module function parameter=value
```

### 3. Python через HTTP API
```python
import requests
import base64

class CpanelAPI:
    def __init__(self, hostname, username, password, port=2083):
        self.base_url = f"https://{hostname}:{port}"
        self.auth = (username, password)
        
    def call(self, module, function, params=None):
        url = f"{self.base_url}/execute/{module}/{function}"
        response = requests.get(url, auth=self.auth, params=params, verify=False)
        return response.json()
```

## Основные модули UAPI

### Управление файлами (Fileman)

```python
# Получить содержимое директории
cpanel.call("Fileman", "list_files", {
    "dir": "/public_html",
    "include_mime": 1,
    "include_permissions": 1
})

# Получить содержимое файла
cpanel.call("Fileman", "get_file_content", {
    "dir": "/public_html",
    "file": "index.html"
})

# Сохранить файл
cpanel.call("Fileman", "save_file_content", {
    "dir": "/public_html",
    "file": "test.html",
    "content": "<html><body>Test</body></html>"
})

# Создать директорию
cpanel.call("Fileman", "mkdir", {
    "path": "/public_html/new_folder",
    "permissions": "0755"
})

# Удалить файл
cpanel.call("Fileman", "trash", {
    "files": "/public_html/old_file.html"
})

# Копировать файл
cpanel.call("Fileman", "copy", {
    "source": "/public_html/file.html",
    "dest": "/public_html/backup/file.html"
})

# Переместить файл
cpanel.call("Fileman", "move", {
    "source": "/public_html/old.html",
    "dest": "/public_html/new.html"
})
```

### Управление базами данных (Mysql)

```python
# Список баз данных
cpanel.call("Mysql", "list_databases")

# Создать базу данных
cpanel.call("Mysql", "create_database", {
    "name": "mydb"
})

# Создать пользователя БД
cpanel.call("Mysql", "create_user", {
    "name": "myuser",
    "password": "SecurePass123!"
})

# Дать права пользователю
cpanel.call("Mysql", "set_privileges_on_database", {
    "user": "myuser",
    "database": "mydb",
    "privileges": "ALL PRIVILEGES"
})

# Удалить базу данных
cpanel.call("Mysql", "delete_database", {
    "name": "mydb"
})
```

### Управление доменами (DomainInfo)

```python
# Список доменов
cpanel.call("DomainInfo", "list_domains")

# Информация о домене
cpanel.call("DomainInfo", "single_domain_data", {
    "domain": "example.com"
})

# Добавить поддомен
cpanel.call("SubDomain", "addsubdomain", {
    "domain": "sub",
    "rootdomain": "example.com",
    "dir": "/public_html/sub"
})

# Удалить поддомен
cpanel.call("SubDomain", "delsubdomain", {
    "domain": "sub.example.com"
})

# Добавить addon домен
cpanel.call("AddonDomain", "addaddondomain", {
    "newdomain": "addon.com",
    "subdomain": "addon",
    "dir": "/public_html/addon"
})
```

### Управление Email

```python
# Создать email аккаунт
cpanel.call("Email", "add_pop", {
    "email": "user",
    "domain": "example.com",
    "password": "SecurePass123!",
    "quota": 1024  # MB
})

# Список email аккаунтов
cpanel.call("Email", "list_pops")

# Удалить email аккаунт
cpanel.call("Email", "delete_pop", {
    "email": "user@example.com"
})

# Создать форвардер
cpanel.call("Email", "add_forwarder", {
    "email": "user@example.com",
    "fwdopt": "fwd",
    "fwdemail": "forward@gmail.com"
})
```

### Управление FTP

```python
# Создать FTP аккаунт
cpanel.call("Ftp", "add_ftp", {
    "user": "ftpuser",
    "pass": "SecurePass123!",
    "homedir": "/public_html",
    "quota": 0  # unlimited
})

# Список FTP аккаунтов
cpanel.call("Ftp", "list_ftp")

# Удалить FTP аккаунт
cpanel.call("Ftp", "delete_ftp", {
    "user": "ftpuser",
    "destroy": 0
})
```

### Управление SSL

```python
# Список SSL сертификатов
cpanel.call("SSL", "list_certs")

# Установить SSL сертификат
cpanel.call("SSL", "install_ssl", {
    "domain": "example.com",
    "cert": "-----BEGIN CERTIFICATE-----...",
    "key": "-----BEGIN PRIVATE KEY-----...",
    "cabundle": "-----BEGIN CERTIFICATE-----..."
})

# Сгенерировать CSR
cpanel.call("SSL", "generate_csr", {
    "domains": "example.com",
    "city": "Moscow",
    "state": "Moscow",
    "country": "RU",
    "company": "Company Name",
    "email": "admin@example.com"
})
```

### Управление Cron

```python
# Список cron задач
cpanel.call("Cron", "list_cron")

# Добавить cron задачу
cpanel.call("Cron", "add_line", {
    "command": "/usr/bin/php /home/user/script.php",
    "minute": "0",
    "hour": "*/6",
    "day": "*",
    "month": "*",
    "weekday": "*"
})

# Удалить cron задачу
cpanel.call("Cron", "remove_line", {
    "linekey": "abc123..."  # из list_cron
})
```

## Работа с .htaccess

```python
def update_htaccess(cpanel, rules):
    """Обновить .htaccess файл"""
    # Получить текущий контент
    result = cpanel.call("Fileman", "get_file_content", {
        "dir": "/public_html",
        "file": ".htaccess"
    })
    
    current = result.get("data", {}).get("content", "")
    
    # Добавить правила
    new_content = rules + "\n" + current
    
    # Сохранить
    cpanel.call("Fileman", "save_file_content", {
        "dir": "/public_html",
        "file": ".htaccess",
        "content": new_content
    })

# Пример: добавить редирект
redirect_rules = """
# Redirect to new domain
RewriteEngine On
RewriteCond %{HTTP_HOST} ^olddomain\.com$ [NC]
RewriteRule ^(.*)$ https://newdomain.com/$1 [R=301,L]
"""
update_htaccess(cpanel, redirect_rules)
```

## Полный класс для работы с cPanel

```python
import requests
import urllib3
urllib3.disable_warnings()

class CpanelManager:
    def __init__(self, hostname, username, password, port=2083):
        self.base_url = f"https://{hostname}:{port}"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False
        
    def call(self, module, function, params=None):
        """Вызов UAPI функции"""
        url = f"{self.base_url}/execute/{module}/{function}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            return response.json()
        except Exception as e:
            return {"status": 0, "errors": [str(e)]}
    
    # === Файловые операции ===
    
    def list_files(self, directory="/public_html"):
        return self.call("Fileman", "list_files", {"dir": directory})
    
    def read_file(self, filepath):
        dir_path = "/".join(filepath.split("/")[:-1])
        filename = filepath.split("/")[-1]
        return self.call("Fileman", "get_file_content", {
            "dir": dir_path,
            "file": filename
        })
    
    def write_file(self, filepath, content):
        dir_path = "/".join(filepath.split("/")[:-1])
        filename = filepath.split("/")[-1]
        return self.call("Fileman", "save_file_content", {
            "dir": dir_path,
            "file": filename,
            "content": content
        })
    
    def delete_file(self, filepath):
        return self.call("Fileman", "trash", {"files": filepath})
    
    def create_directory(self, path):
        return self.call("Fileman", "mkdir", {
            "path": path,
            "permissions": "0755"
        })
    
    # === Редиректы ===
    
    def add_redirect(self, from_url, to_url, redirect_type=301):
        """Добавить редирект через .htaccess"""
        htaccess = self.read_file("/public_html/.htaccess")
        current = htaccess.get("data", {}).get("content", "")
        
        rule = f"""
# Redirect added by SEO Monster
RewriteEngine On
RewriteRule ^{from_url}$ {to_url} [R={redirect_type},L]
"""
        new_content = rule + current
        return self.write_file("/public_html/.htaccess", new_content)
    
    def add_geo_redirect(self, country_codes, target_url):
        """Добавить гео-редирект"""
        countries = "|".join(country_codes)
        rule = f"""
# Geo redirect by SEO Monster
RewriteEngine On
RewriteCond %{{ENV:GEOIP_COUNTRY_CODE}} ^({countries})$
RewriteRule ^(.*)$ {target_url}$1 [R=302,L]
"""
        htaccess = self.read_file("/public_html/.htaccess")
        current = htaccess.get("data", {}).get("content", "")
        return self.write_file("/public_html/.htaccess", rule + current)
    
    # === Базы данных ===
    
    def list_databases(self):
        return self.call("Mysql", "list_databases")
    
    def create_database(self, name):
        return self.call("Mysql", "create_database", {"name": name})
    
    def create_db_user(self, username, password):
        return self.call("Mysql", "create_user", {
            "name": username,
            "password": password
        })
    
    # === Домены ===
    
    def list_domains(self):
        return self.call("DomainInfo", "list_domains")
    
    def add_subdomain(self, subdomain, root_domain, directory=None):
        if directory is None:
            directory = f"/public_html/{subdomain}"
        return self.call("SubDomain", "addsubdomain", {
            "domain": subdomain,
            "rootdomain": root_domain,
            "dir": directory
        })
    
    # === Cron ===
    
    def add_cron_job(self, command, schedule="0 * * * *"):
        parts = schedule.split()
        return self.call("Cron", "add_line", {
            "command": command,
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "weekday": parts[4]
        })
    
    def list_cron_jobs(self):
        return self.call("Cron", "list_cron")
```

## WHM API (для реселлеров)

```python
class WHMManager:
    def __init__(self, hostname, username, api_token, port=2087):
        self.base_url = f"https://{hostname}:{port}"
        self.headers = {
            "Authorization": f"whm {username}:{api_token}"
        }
        
    def call(self, function, params=None):
        url = f"{self.base_url}/json-api/{function}"
        response = requests.get(url, headers=self.headers, 
                               params=params, verify=False)
        return response.json()
    
    # Создать аккаунт
    def create_account(self, domain, username, password, plan="default"):
        return self.call("createacct", {
            "domain": domain,
            "username": username,
            "password": password,
            "plan": plan
        })
    
    # Список аккаунтов
    def list_accounts(self):
        return self.call("listaccts")
    
    # Приостановить аккаунт
    def suspend_account(self, username, reason=""):
        return self.call("suspendacct", {
            "user": username,
            "reason": reason
        })
    
    # Возобновить аккаунт
    def unsuspend_account(self, username):
        return self.call("unsuspendacct", {"user": username})
    
    # Удалить аккаунт
    def terminate_account(self, username):
        return self.call("removeacct", {"user": username})
```

## Обработка ошибок

```python
def safe_cpanel_call(cpanel, module, function, params=None):
    """Безопасный вызов cPanel API"""
    try:
        result = cpanel.call(module, function, params)
        
        if result.get("status") == 0:
            errors = result.get("errors", ["Unknown error"])
            print(f"cPanel Error: {errors}")
            return None
            
        return result.get("data")
        
    except requests.exceptions.ConnectionError:
        print("Connection error - check hostname and port")
        return None
    except requests.exceptions.Timeout:
        print("Request timeout")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
```

## Типичные коды ошибок

| Код | Описание |
|-----|----------|
| 0 | Ошибка выполнения |
| 1 | Успешно |
| 401 | Неверная аутентификация |
| 403 | Доступ запрещён |
| 404 | Функция не найдена |
| 500 | Внутренняя ошибка сервера |

Источники: api.docs.cpanel.net, cpanel.net/developers, 2024-2026
