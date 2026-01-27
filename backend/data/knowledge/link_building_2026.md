# Link Building (Построение ссылок) 2026

## Типы ссылок

### По атрибуту
| Тип | Описание | SEO-ценность |
|-----|----------|--------------|
| DoFollow | Передаёт вес | Высокая |
| NoFollow | Не передаёт вес | Низкая (но полезна для разнообразия) |
| Sponsored | Платная ссылка | Низкая |
| UGC | Пользовательский контент | Низкая |

### По источнику
- **Editorial** — естественные ссылки из контента
- **Guest Post** — гостевые посты
- **Directory** — каталоги и справочники
- **Social** — социальные сети
- **Forum/Comment** — форумы и комментарии
- **PBN** — частные сети блогов (рискованно)

## Стратегии линкбилдинга 2026

### 1. Гостевой постинг (Guest Posting)

**Поиск площадок:**
```
"ключевое слово" + "написать для нас"
"ключевое слово" + "гостевой пост"
"ключевое слово" + "стать автором"
"ключевое слово" + inurl:write-for-us
"ключевое слово" + inurl:guest-post
```

**Шаблон outreach письма:**
```
Тема: Идея статьи для [Название сайта]

Здравствуйте, [Имя]!

Я [Имя], [должность] в [компания]. Давно слежу за вашим блогом и особенно понравилась статья о [тема].

У меня есть идея для статьи, которая может быть интересна вашим читателям:

"[Заголовок статьи]"

В статье я раскрою:
- [Пункт 1]
- [Пункт 2]
- [Пункт 3]

Вот примеры моих работ:
- [Ссылка 1]
- [Ссылка 2]

Буду рад обсудить детали!

С уважением,
[Имя]
```

### 2. Broken Link Building

**Процесс:**
1. Найти страницы с битыми ссылками
2. Создать контент на замену
3. Предложить владельцу заменить ссылку

**Поиск битых ссылок:**
```python
import requests
from bs4 import BeautifulSoup

def find_broken_links(url):
    broken = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                try:
                    r = requests.head(href, timeout=5)
                    if r.status_code >= 400:
                        broken.append({
                            'url': href,
                            'anchor': link.text,
                            'status': r.status_code
                        })
                except:
                    broken.append({
                        'url': href,
                        'anchor': link.text,
                        'status': 'timeout'
                    })
    except Exception as e:
        print(f"Error: {e}")
    
    return broken
```

### 3. Skyscraper Technique

**Шаги:**
1. Найти популярный контент в нише
2. Создать лучшую версию (длиннее, актуальнее, красивее)
3. Связаться с теми, кто ссылался на оригинал

**Поиск популярного контента:**
- Ahrefs Content Explorer
- BuzzSumo
- Google: "ключевое слово" + "ссылок"

### 4. Resource Page Link Building

**Поиск ресурсных страниц:**
```
"ключевое слово" + "полезные ссылки"
"ключевое слово" + "ресурсы"
"ключевое слово" + inurl:resources
"ключевое слово" + inurl:links
```

### 5. HARO (Help A Reporter Out)

**Платформы:**
- HARO (helpareporter.com)
- SourceBottle
- JournoRequests
- Qwoted

**Советы:**
- Отвечайте быстро (в течение часа)
- Давайте экспертные ответы
- Включайте цитаты и статистику

### 6. Инфографики

**Процесс:**
1. Создать качественную инфографику
2. Разместить на своём сайте
3. Предложить другим сайтам для публикации

**Outreach:**
```
Тема: Бесплатная инфографика для вашего блога

Здравствуйте!

Я создал инфографику на тему "[тема]", которая может быть интересна вашим читателям.

[Превью инфографики]

Вы можете бесплатно использовать её в своём блоге. 
Я предоставлю embed-код со ссылкой на источник.

Хотите получить полную версию?
```

## Web 2.0 и Social Bookmarking

### Web 2.0 платформы
```python
WEB_2_0_SITES = [
    # Высокий DA
    {'name': 'Medium', 'da': 95, 'dofollow': False},
    {'name': 'WordPress.com', 'da': 93, 'dofollow': False},
    {'name': 'Blogger', 'da': 89, 'dofollow': False},
    {'name': 'Tumblr', 'da': 86, 'dofollow': False},
    {'name': 'Wix', 'da': 94, 'dofollow': False},
    
    # Средний DA
    {'name': 'LiveJournal', 'da': 86, 'dofollow': True},
    {'name': 'Weebly', 'da': 89, 'dofollow': False},
    {'name': 'Jimdo', 'da': 84, 'dofollow': False},
    {'name': 'Site123', 'da': 78, 'dofollow': False},
    
    # Русскоязычные
    {'name': 'VC.ru', 'da': 75, 'dofollow': True},
    {'name': 'Habr', 'da': 82, 'dofollow': True},
    {'name': 'Pikabu', 'da': 78, 'dofollow': False},
    {'name': 'Яндекс.Дзен', 'da': 90, 'dofollow': False},
]
```

### Social Bookmarking
```python
SOCIAL_BOOKMARKS = [
    {'name': 'Reddit', 'da': 99},
    {'name': 'Mix', 'da': 91},
    {'name': 'Flipboard', 'da': 92},
    {'name': 'Pocket', 'da': 93},
    {'name': 'Digg', 'da': 90},
    {'name': 'Slashdot', 'da': 91},
    {'name': 'Scoop.it', 'da': 92},
]
```

## Каталоги и справочники

### Бизнес-каталоги
```python
BUSINESS_DIRECTORIES = [
    # Международные
    {'name': 'Google Business', 'da': 100, 'type': 'local'},
    {'name': 'Bing Places', 'da': 99, 'type': 'local'},
    {'name': 'Yelp', 'da': 94, 'type': 'reviews'},
    {'name': 'Yellow Pages', 'da': 91, 'type': 'directory'},
    {'name': 'Foursquare', 'da': 92, 'type': 'local'},
    
    # Русскоязычные
    {'name': 'Яндекс.Бизнес', 'da': 95, 'type': 'local'},
    {'name': '2GIS', 'da': 78, 'type': 'local'},
    {'name': 'Zoon', 'da': 65, 'type': 'reviews'},
    {'name': 'Yell.ru', 'da': 55, 'type': 'directory'},
]
```

### Нишевые каталоги
- Отраслевые справочники
- Профессиональные ассоциации
- Местные бизнес-палаты
- Тематические агрегаторы

## Анализ ссылочного профиля

### Метрики для оценки
| Метрика | Описание | Целевое значение |
|---------|----------|------------------|
| DA/DR | Авторитет домена | > 30 |
| PA | Авторитет страницы | > 20 |
| Trust Flow | Качество ссылок | > 15 |
| Citation Flow | Количество ссылок | > 20 |
| Spam Score | Спамность | < 5% |

### Инструменты анализа
- Ahrefs
- Moz
- Majestic
- SEMrush
- Serpstat

## Автоматизация линкбилдинга

### Скрипт для outreach
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

class OutreachAutomation:
    def __init__(self, smtp_server, smtp_port, email, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
    
    def send_email(self, to_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending to {to_email}: {e}")
            return False
    
    def bulk_outreach(self, contacts, template, delay=60):
        """
        contacts: [{'email': '', 'name': '', 'site': ''}]
        template: строка с {name}, {site} плейсхолдерами
        """
        results = []
        for contact in contacts:
            personalized = template.format(**contact)
            subject = f"Предложение о сотрудничестве для {contact['site']}"
            
            success = self.send_email(contact['email'], subject, personalized)
            results.append({
                'email': contact['email'],
                'success': success
            })
            
            time.sleep(delay)  # Задержка между письмами
        
        return results
```

### Скрипт для постинга на Web 2.0
```python
import requests
from bs4 import BeautifulSoup

class Web20Poster:
    def __init__(self):
        self.session = requests.Session()
    
    def post_to_medium(self, token, title, content, tags=[]):
        """Публикация на Medium через API"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Получить user_id
        user_response = self.session.get(
            'https://api.medium.com/v1/me',
            headers=headers
        )
        user_id = user_response.json()['data']['id']
        
        # Создать пост
        post_data = {
            'title': title,
            'contentFormat': 'html',
            'content': content,
            'tags': tags,
            'publishStatus': 'public'
        }
        
        response = self.session.post(
            f'https://api.medium.com/v1/users/{user_id}/posts',
            headers=headers,
            json=post_data
        )
        
        return response.json()
    
    def post_to_wordpress_com(self, site, token, title, content):
        """Публикация на WordPress.com"""
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish'
        }
        
        response = self.session.post(
            f'https://public-api.wordpress.com/rest/v1.1/sites/{site}/posts/new',
            headers=headers,
            data=post_data
        )
        
        return response.json()
```

## Риски и предостережения

### Что избегать
- ❌ Покупка ссылок на биржах (риск санкций)
- ❌ Массовый спам комментариями
- ❌ PBN низкого качества
- ❌ Ссылки с сайтов для взрослых/казино (если не в теме)
- ❌ Автоматический постинг без модерации

### Признаки плохих ссылок
- Сайт с DA < 10
- Много исходящих ссылок (> 100)
- Нерелевантная тематика
- Сайт под санкциями
- Китайские/индийские спам-сайты

## Мониторинг ссылок

```python
def monitor_backlinks(domain, api_key):
    """Мониторинг новых и потерянных ссылок"""
    # Используйте Ahrefs/Moz API
    pass

def check_link_status(url, target_url):
    """Проверка наличия ссылки на странице"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            if target_url in link['href']:
                return {
                    'found': True,
                    'anchor': link.text,
                    'nofollow': 'nofollow' in link.get('rel', [])
                }
        
        return {'found': False}
    except Exception as e:
        return {'error': str(e)}
```

Источники: Ahrefs, Moz, Backlinko, Search Engine Journal, 2024-2026
