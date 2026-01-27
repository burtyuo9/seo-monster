# Антидетект браузеры и прокси 2026

## Антидетект браузеры

### Популярные решения

| Браузер | Цена | Особенности |
|---------|------|-------------|
| Multilogin | от $99/мес | Лидер рынка, Mimic/Stealthfox |
| GoLogin | от $49/мес | Бюджетный, облачные профили |
| Dolphin Anty | от $89/мес | Для арбитража, командная работа |
| AdsPower | от $9/мес | Дешёвый, много профилей |
| Incogniton | от $29/мес | Простой интерфейс |
| Octo Browser | от $29/мес | Быстрый, API |
| Undetectable | от $49/мес | Хорошая маскировка |

### Что маскируют антидетекты

1. **User-Agent** — строка браузера
2. **Canvas fingerprint** — отпечаток canvas
3. **WebGL fingerprint** — отпечаток видеокарты
4. **Audio fingerprint** — аудио отпечаток
5. **Fonts** — список шрифтов
6. **Screen resolution** — разрешение экрана
7. **Timezone** — часовой пояс
8. **Language** — язык браузера
9. **Plugins** — список плагинов
10. **WebRTC** — утечка реального IP

### Настройка профиля

```python
# Пример конфигурации профиля
profile_config = {
    "name": "Profile_1",
    "os": "Windows",  # Windows, macOS, Linux
    "browser": "Chrome",
    "version": "120",
    
    # Fingerprint
    "canvas": "noise",  # noise, off, real
    "webgl": "noise",
    "audio": "noise",
    "fonts": "mask",
    
    # Геолокация
    "timezone": "Europe/Moscow",
    "language": "ru-RU",
    "geolocation": {
        "latitude": 55.7558,
        "longitude": 37.6173
    },
    
    # Прокси
    "proxy": {
        "type": "http",  # http, socks5
        "host": "proxy.example.com",
        "port": 8080,
        "username": "user",
        "password": "pass"
    },
    
    # WebRTC
    "webrtc": "disabled",  # disabled, fake, real
    
    # Cookies
    "cookies": [],
    
    # User-Agent
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

## Типы прокси

### По протоколу

| Тип | Описание | Скорость | Анонимность |
|-----|----------|----------|-------------|
| HTTP | Базовый протокол | Высокая | Низкая |
| HTTPS | Шифрованный HTTP | Высокая | Средняя |
| SOCKS4 | Без аутентификации | Высокая | Средняя |
| SOCKS5 | С аутентификацией, UDP | Высокая | Высокая |

### По источнику

| Тип | Описание | Цена | Качество |
|-----|----------|------|----------|
| Datacenter | Серверные прокси | $1-5/IP | Среднее |
| Residential | Домашние IP | $5-15/GB | Высокое |
| Mobile | Мобильные IP | $20-50/GB | Очень высокое |
| ISP | Статические резидентные | $2-5/IP | Высокое |

### Провайдеры прокси

```python
PROXY_PROVIDERS = {
    # Резидентные
    'bright_data': {
        'type': 'residential',
        'price': '$8.4/GB',
        'pool': '72M IPs',
        'features': ['geo-targeting', 'sticky sessions']
    },
    'smartproxy': {
        'type': 'residential',
        'price': '$7/GB',
        'pool': '55M IPs',
        'features': ['unlimited threads', 'city targeting']
    },
    'oxylabs': {
        'type': 'residential',
        'price': '$10/GB',
        'pool': '100M IPs',
        'features': ['enterprise', 'dedicated support']
    },
    
    # Мобильные
    'proxyrack': {
        'type': 'mobile',
        'price': '$14.95/GB',
        'features': ['4G/LTE', 'rotation']
    },
    
    # Датацентр
    'proxy_cheap': {
        'type': 'datacenter',
        'price': '$0.5/IP/month',
        'features': ['unlimited bandwidth']
    }
}
```

## Ротация прокси

### Стратегии ротации

```python
import random
import time
from itertools import cycle

class ProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.current_index = 0
        self.failed_proxies = set()
        
    def get_next_sequential(self):
        """Последовательная ротация"""
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_random(self):
        """Случайная ротация"""
        available = [p for p in self.proxies if p not in self.failed_proxies]
        if not available:
            self.failed_proxies.clear()
            available = self.proxies
        return random.choice(available)
    
    def get_sticky(self, session_id, duration=600):
        """Sticky session - один прокси на сессию"""
        # Используйте hash для привязки сессии к прокси
        index = hash(session_id) % len(self.proxies)
        return self.proxies[index]
    
    def mark_failed(self, proxy):
        """Пометить прокси как нерабочий"""
        self.failed_proxies.add(proxy)
    
    def get_with_retry(self, test_url='https://httpbin.org/ip', max_retries=3):
        """Получить рабочий прокси с проверкой"""
        import requests
        
        for _ in range(max_retries):
            proxy = self.get_random()
            try:
                response = requests.get(
                    test_url,
                    proxies={'http': proxy, 'https': proxy},
                    timeout=10
                )
                if response.status_code == 200:
                    return proxy
            except:
                self.mark_failed(proxy)
        
        return None
```

### Формат прокси

```python
# Форматы прокси строк
PROXY_FORMATS = {
    'basic': 'host:port',
    'auth': 'host:port:username:password',
    'url_http': 'http://username:password@host:port',
    'url_socks5': 'socks5://username:password@host:port'
}

def parse_proxy(proxy_string):
    """Парсинг строки прокси"""
    if '://' in proxy_string:
        # URL формат
        from urllib.parse import urlparse
        parsed = urlparse(proxy_string)
        return {
            'type': parsed.scheme,
            'host': parsed.hostname,
            'port': parsed.port,
            'username': parsed.username,
            'password': parsed.password
        }
    else:
        # Простой формат
        parts = proxy_string.split(':')
        if len(parts) == 2:
            return {'host': parts[0], 'port': int(parts[1])}
        elif len(parts) == 4:
            return {
                'host': parts[0],
                'port': int(parts[1]),
                'username': parts[2],
                'password': parts[3]
            }
    return None

def format_proxy(proxy_dict, format_type='url_http'):
    """Форматирование прокси в строку"""
    if format_type == 'url_http':
        if proxy_dict.get('username'):
            return f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['host']}:{proxy_dict['port']}"
        return f"http://{proxy_dict['host']}:{proxy_dict['port']}"
    elif format_type == 'url_socks5':
        if proxy_dict.get('username'):
            return f"socks5://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['host']}:{proxy_dict['port']}"
        return f"socks5://{proxy_dict['host']}:{proxy_dict['port']}"
    return f"{proxy_dict['host']}:{proxy_dict['port']}"
```

## Проверка прокси

```python
import requests
import concurrent.futures
import time

class ProxyChecker:
    def __init__(self):
        self.test_urls = [
            'https://httpbin.org/ip',
            'https://api.ipify.org?format=json',
            'https://ifconfig.me/ip'
        ]
    
    def check_single(self, proxy, timeout=10):
        """Проверка одного прокси"""
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        
        for url in self.test_urls:
            try:
                start = time.time()
                response = requests.get(url, proxies=proxy_dict, timeout=timeout)
                latency = time.time() - start
                
                if response.status_code == 200:
                    return {
                        'proxy': proxy,
                        'working': True,
                        'latency': round(latency * 1000),  # ms
                        'ip': response.text.strip()
                    }
            except:
                continue
        
        return {'proxy': proxy, 'working': False}
    
    def check_bulk(self, proxies, max_workers=50):
        """Массовая проверка прокси"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.check_single, p): p for p in proxies}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
        
        return results
    
    def check_anonymity(self, proxy):
        """Проверка уровня анонимности"""
        try:
            # Проверяем утечку реального IP
            response = requests.get(
                'https://httpbin.org/headers',
                proxies={'http': proxy, 'https': proxy},
                timeout=10
            )
            headers = response.json()['headers']
            
            # Проверяем заголовки
            suspicious_headers = [
                'X-Forwarded-For',
                'X-Real-Ip',
                'Via',
                'X-Proxy-Id'
            ]
            
            found_headers = [h for h in suspicious_headers if h in headers]
            
            if not found_headers:
                return 'elite'  # Высокая анонимность
            elif 'X-Forwarded-For' in found_headers:
                return 'anonymous'  # Средняя анонимность
            else:
                return 'transparent'  # Низкая анонимность
                
        except:
            return 'unknown'
```

## Интеграция с Playwright/Selenium

### Playwright с прокси
```python
from playwright.sync_api import sync_playwright

def create_browser_with_proxy(proxy_config):
    """Создание браузера с прокси"""
    playwright = sync_playwright().start()
    
    proxy = {
        'server': f"{proxy_config['host']}:{proxy_config['port']}"
    }
    
    if proxy_config.get('username'):
        proxy['username'] = proxy_config['username']
        proxy['password'] = proxy_config['password']
    
    browser = playwright.chromium.launch(
        headless=True,
        proxy=proxy
    )
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        locale='ru-RU',
        timezone_id='Europe/Moscow'
    )
    
    return browser, context
```

### Selenium с прокси
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def create_driver_with_proxy(proxy_string):
    """Создание WebDriver с прокси"""
    options = Options()
    options.add_argument(f'--proxy-server={proxy_string}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    
    driver = webdriver.Chrome(options=options)
    
    # Скрыть признаки автоматизации
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return driver
```

## Обход защиты от ботов

### Cloudflare
```python
import cloudscraper

def bypass_cloudflare(url):
    """Обход Cloudflare защиты"""
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    response = scraper.get(url)
    return response.text
```

### reCAPTCHA
- Используйте сервисы решения капчи:
  - 2Captcha
  - Anti-Captcha
  - CapMonster

```python
import requests

def solve_recaptcha(site_key, page_url, api_key):
    """Решение reCAPTCHA через 2Captcha"""
    # Отправить задачу
    response = requests.post('http://2captcha.com/in.php', data={
        'key': api_key,
        'method': 'userrecaptcha',
        'googlekey': site_key,
        'pageurl': page_url
    })
    
    captcha_id = response.text.split('|')[1]
    
    # Ждать решения
    import time
    for _ in range(30):
        time.sleep(5)
        result = requests.get(f'http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}')
        if 'OK' in result.text:
            return result.text.split('|')[1]
    
    return None
```

## Лучшие практики

1. **Ротация User-Agent** вместе с прокси
2. **Соответствие гео** прокси и языка браузера
3. **Задержки между запросами** — имитация человека
4. **Разогрев аккаунтов** перед активной работой
5. **Мониторинг банов** и автоматическая замена прокси
6. **Разделение профилей** по задачам

Источники: Multilogin, GoLogin, BrightData, 2024-2026
