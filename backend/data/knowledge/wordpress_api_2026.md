# WordPress REST API - Полное руководство 2026

## Аутентификация

### Application Passwords (встроено в WordPress 5.6+)
```php
$login = 'username';
$password = 'xxxx xxxx xxxx xxxx xxxx xxxx'; // Application Password

$headers = array(
    'Authorization' => 'Basic ' . base64_encode("$login:$password")
);
```

### Для localhost добавить в wp-config.php:
```php
define('WP_ENVIRONMENT_TYPE', 'local');
```

## Создание поста через REST API

### Базовый пример (PHP):
```php
$response = wp_remote_post(
    'https://example.com/wp-json/wp/v2/posts',
    array(
        'headers' => array(
            'Authorization' => 'Basic ' . base64_encode("$login:$password")
        ),
        'body' => array(
            'title'   => 'Заголовок поста',
            'content' => 'Содержимое поста',
            'status'  => 'publish', // draft, publish, pending
        )
    )
);
```

### Пример на Python:
```python
import requests
import base64

url = "https://example.com/wp-json/wp/v2/posts"
user = "username"
password = "xxxx xxxx xxxx xxxx xxxx xxxx"

credentials = base64.b64encode(f"{user}:{password}".encode()).decode()

headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json"
}

data = {
    "title": "Заголовок поста",
    "content": "Содержимое поста",
    "status": "publish"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

## Параметры REST API для постов

| Параметр | Описание |
|----------|----------|
| `title` | Заголовок поста |
| `content` | Содержимое (HTML) |
| `status` | draft, publish, pending, private |
| `date` | Дата публикации (2026-01-27 12:00:00) |
| `slug` | URL-slug поста |
| `author` | ID автора |
| `excerpt` | Краткое описание |
| `featured_media` | ID изображения |
| `categories` | Массив ID категорий |
| `tags` | Массив ID тегов |
| `meta` | Массив мета-полей |
| `comment_status` | open / closed |
| `ping_status` | open / closed |
| `sticky` | true / false |
| `template` | Шаблон страницы |
| `password` | Пароль для защиты |

## Эндпоинты REST API

### Посты:
```
GET    /wp-json/wp/v2/posts          - список постов
GET    /wp-json/wp/v2/posts/{id}     - один пост
POST   /wp-json/wp/v2/posts          - создать пост
PUT    /wp-json/wp/v2/posts/{id}     - обновить пост
DELETE /wp-json/wp/v2/posts/{id}     - удалить пост
```

### Страницы:
```
GET    /wp-json/wp/v2/pages          - список страниц
POST   /wp-json/wp/v2/pages          - создать страницу
```

### Медиа:
```
GET    /wp-json/wp/v2/media          - список медиа
POST   /wp-json/wp/v2/media          - загрузить файл
```

### Категории и теги:
```
GET    /wp-json/wp/v2/categories     - список категорий
POST   /wp-json/wp/v2/categories     - создать категорию
GET    /wp-json/wp/v2/tags           - список тегов
POST   /wp-json/wp/v2/tags           - создать тег
```

### Пользователи:
```
GET    /wp-json/wp/v2/users          - список пользователей
GET    /wp-json/wp/v2/users/me       - текущий пользователь
```

## Загрузка изображений

### Python пример:
```python
import requests
import base64

url = "https://example.com/wp-json/wp/v2/media"
credentials = base64.b64encode(f"{user}:{password}".encode()).decode()

# Загрузка изображения
with open("image.jpg", "rb") as f:
    image_data = f.read()

headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "image/jpeg",
    "Content-Disposition": "attachment; filename=image.jpg"
}

response = requests.post(url, headers=headers, data=image_data)
media_id = response.json()["id"]

# Установка как featured image
post_url = f"https://example.com/wp-json/wp/v2/posts/{post_id}"
requests.post(post_url, headers={
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json"
}, json={"featured_media": media_id})
```

## Массовое создание постов

```python
import requests
import base64
import time

class WordPressAPI:
    def __init__(self, url, username, app_password):
        self.url = url.rstrip('/')
        credentials = f"{username}:{app_password}"
        self.auth = base64.b64encode(credentials.encode()).decode()
        
    def create_post(self, title, content, status="draft", categories=None, tags=None):
        endpoint = f"{self.url}/wp-json/wp/v2/posts"
        headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }
        data = {
            "title": title,
            "content": content,
            "status": status
        }
        if categories:
            data["categories"] = categories
        if tags:
            data["tags"] = tags
            
        response = requests.post(endpoint, headers=headers, json=data)
        return response.json()
    
    def bulk_create_posts(self, posts, delay=1):
        """Массовое создание постов с задержкой"""
        results = []
        for post in posts:
            result = self.create_post(**post)
            results.append(result)
            time.sleep(delay)  # Избегаем rate limiting
        return results
    
    def update_post(self, post_id, **kwargs):
        endpoint = f"{self.url}/wp-json/wp/v2/posts/{post_id}"
        headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }
        response = requests.post(endpoint, headers=headers, json=kwargs)
        return response.json()
    
    def get_posts(self, per_page=100, page=1, status="any"):
        endpoint = f"{self.url}/wp-json/wp/v2/posts"
        params = {
            "per_page": per_page,
            "page": page,
            "status": status
        }
        headers = {"Authorization": f"Basic {self.auth}"}
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()
```

## Работа с категориями

```python
def get_or_create_category(wp, name, parent=0):
    """Получить или создать категорию"""
    # Поиск существующей
    endpoint = f"{wp.url}/wp-json/wp/v2/categories"
    params = {"search": name}
    headers = {"Authorization": f"Basic {wp.auth}"}
    
    response = requests.get(endpoint, headers=headers, params=params)
    categories = response.json()
    
    for cat in categories:
        if cat["name"].lower() == name.lower():
            return cat["id"]
    
    # Создание новой
    data = {"name": name, "parent": parent}
    response = requests.post(endpoint, headers=headers, json=data)
    return response.json()["id"]
```

## Вставка редиректов через .htaccess

### Через wp-config.php или плагин:
```php
// Добавление редиректа
function add_custom_redirect($from, $to) {
    $htaccess = ABSPATH . '.htaccess';
    $content = file_get_contents($htaccess);
    
    $redirect = "Redirect 301 $from $to\n";
    
    if (strpos($content, $redirect) === false) {
        $content = $redirect . $content;
        file_put_contents($htaccess, $content);
    }
}
```

## Внедрение рекламы в контент

```python
def inject_ads_into_content(content, ad_code, position="middle"):
    """Вставка рекламы в контент"""
    paragraphs = content.split("</p>")
    
    if position == "top":
        return ad_code + content
    elif position == "bottom":
        return content + ad_code
    elif position == "middle":
        mid = len(paragraphs) // 2
        paragraphs.insert(mid, ad_code)
        return "</p>".join(paragraphs)
    elif position == "every_n":
        n = 3  # Каждые 3 параграфа
        result = []
        for i, p in enumerate(paragraphs):
            result.append(p)
            if (i + 1) % n == 0:
                result.append(ad_code)
        return "</p>".join(result)
```

## Автоматическое обновление контента

```python
def auto_update_posts(wp, keyword_replacements):
    """Автоматическая замена ключевых слов в постах"""
    posts = wp.get_posts(per_page=100, status="publish")
    
    for post in posts:
        content = post["content"]["rendered"]
        updated = False
        
        for old, new in keyword_replacements.items():
            if old in content:
                content = content.replace(old, new)
                updated = True
        
        if updated:
            wp.update_post(post["id"], content=content)
```

## Обработка ошибок

```python
def safe_api_call(func):
    """Декоратор для безопасных API вызовов"""
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            if isinstance(response, dict) and "code" in response:
                # Ошибка API
                print(f"API Error: {response.get('message', 'Unknown error')}")
                return None
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    return wrapper
```

## Коды ответов REST API

| Код | Описание |
|-----|----------|
| 200 | OK - успешный GET запрос |
| 201 | Created - успешное создание |
| 400 | Bad Request - неверные параметры |
| 401 | Unauthorized - ошибка аутентификации |
| 403 | Forbidden - нет прав доступа |
| 404 | Not Found - ресурс не найден |
| 500 | Server Error - ошибка сервера |

## WP-CLI для автоматизации

```bash
# Создание поста
wp post create --post_title="Title" --post_content="Content" --post_status=publish

# Обновление поста
wp post update 123 --post_title="New Title"

# Массовое обновление
wp post list --format=ids | xargs -I {} wp post update {} --post_status=draft

# Экспорт постов
wp post list --format=json > posts.json

# Импорт
wp import file.xml --authors=create
```

Источники: WordPress Developer Documentation, rudrastyh.com, 2024-2026
