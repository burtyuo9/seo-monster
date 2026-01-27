"""
Browser Session Handler - Управление браузерными сессиями через Playwright
Позволяет открывать браузер для ручного входа и сохранять сессии
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, List, Callable
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Run: pip install playwright && playwright install chromium")

from .session_manager import session_manager


class BrowserSessionHandler:
    """Обработчик браузерных сессий для ручного входа и автоматизации"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        
        # Настройки браузера
        self.browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]
        
        # User agents для разных платформ
        self.user_agents = {
            "desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        }
        
        # Callback для уведомлений
        self.on_login_complete: Optional[Callable] = None
    
    async def initialize(self, headless: bool = False):
        """Инициализация Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=self.browser_args
        )
        print("Browser initialized")
    
    async def close(self):
        """Закрытие браузера"""
        for context in self.contexts.values():
            await context.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
    
    async def open_login_page(self, account_id: str, url: str, 
                             device_type: str = "desktop") -> Dict:
        """
        Открытие страницы для ручного входа
        
        Args:
            account_id: ID аккаунта для привязки сессии
            url: URL страницы входа
            device_type: Тип устройства (desktop/mobile)
        
        Returns:
            Информация о сессии
        """
        if not self.browser:
            await self.initialize(headless=False)
        
        # Создаем новый контекст
        context = await self.browser.new_context(
            user_agent=self.user_agents.get(device_type, self.user_agents["desktop"]),
            viewport={"width": 1280, "height": 720} if device_type == "desktop" else {"width": 375, "height": 812},
            locale="ru-RU",
            timezone_id="Europe/Moscow"
        )
        
        # Создаем страницу
        page = await context.new_page()
        
        # Скрываем признаки автоматизации
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Скрываем Playwright
            delete window.__playwright;
            delete window.__pw_manual;
        """)
        
        # Переходим на страницу
        await page.goto(url, wait_until="networkidle")
        
        # Сохраняем контекст и страницу
        self.contexts[account_id] = context
        self.pages[account_id] = page
        
        return {
            "account_id": account_id,
            "url": url,
            "status": "waiting_for_login",
            "message": "Пожалуйста, выполните вход вручную. После успешного входа нажмите 'Сохранить сессию'"
        }
    
    async def save_browser_session(self, account_id: str) -> Dict:
        """
        Сохранение сессии после успешного входа
        
        Args:
            account_id: ID аккаунта
        
        Returns:
            Результат сохранения
        """
        if account_id not in self.contexts:
            return {"success": False, "error": "Session not found"}
        
        context = self.contexts[account_id]
        page = self.pages.get(account_id)
        
        try:
            # Получаем cookies
            cookies = await context.cookies()
            
            # Получаем localStorage и sessionStorage
            local_storage = {}
            session_storage = {}
            
            if page:
                try:
                    local_storage = await page.evaluate("""
                        () => {
                            const items = {};
                            for (let i = 0; i < localStorage.length; i++) {
                                const key = localStorage.key(i);
                                items[key] = localStorage.getItem(key);
                            }
                            return items;
                        }
                    """)
                    
                    session_storage = await page.evaluate("""
                        () => {
                            const items = {};
                            for (let i = 0; i < sessionStorage.length; i++) {
                                const key = sessionStorage.key(i);
                                items[key] = sessionStorage.getItem(key);
                            }
                            return items;
                        }
                    """)
                except Exception as e:
                    print(f"Warning: Could not get storage: {e}")
            
            # Сохраняем сессию
            success = await session_manager.save_session(
                account_id=account_id,
                cookies=cookies,
                local_storage=local_storage,
                session_storage=session_storage
            )
            
            if success:
                # Закрываем страницу
                await page.close()
                await context.close()
                
                del self.contexts[account_id]
                del self.pages[account_id]
                
                return {
                    "success": True,
                    "account_id": account_id,
                    "cookies_count": len(cookies),
                    "message": "Сессия успешно сохранена"
                }
            else:
                return {"success": False, "error": "Failed to save session"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def use_saved_session(self, account_id: str, url: str,
                               headless: bool = True) -> Optional[Page]:
        """
        Использование сохраненной сессии для автоматизации
        
        Args:
            account_id: ID аккаунта
            url: URL для перехода
            headless: Запускать в фоновом режиме
        
        Returns:
            Page объект или None
        """
        # Загружаем сессию
        session = await session_manager.load_session(account_id)
        
        if not session:
            print(f"No valid session for account {account_id}")
            return None
        
        if not self.browser:
            await self.initialize(headless=headless)
        
        # Создаем контекст с сохраненными cookies
        context = await self.browser.new_context(
            user_agent=self.user_agents["desktop"],
            viewport={"width": 1280, "height": 720},
            locale="ru-RU"
        )
        
        # Добавляем cookies
        await context.add_cookies(session["cookies"])
        
        # Создаем страницу
        page = await context.new_page()
        
        # Восстанавливаем localStorage
        if session.get("local_storage"):
            await page.add_init_script(f"""
                const storage = {json.dumps(session['local_storage'])};
                for (const [key, value] of Object.entries(storage)) {{
                    localStorage.setItem(key, value);
                }}
            """)
        
        # Скрываем автоматизацию
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Переходим на URL
        await page.goto(url, wait_until="networkidle")
        
        return page
    
    async def check_session_valid(self, account_id: str, check_url: str,
                                 success_indicator: str) -> bool:
        """
        Проверка валидности сессии
        
        Args:
            account_id: ID аккаунта
            check_url: URL для проверки
            success_indicator: Текст/элемент, указывающий на успешный вход
        
        Returns:
            True если сессия валидна
        """
        page = await self.use_saved_session(account_id, check_url, headless=True)
        
        if not page:
            return False
        
        try:
            # Ждем загрузки
            await page.wait_for_load_state("networkidle")
            
            # Проверяем наличие индикатора
            content = await page.content()
            is_valid = success_indicator.lower() in content.lower()
            
            await page.close()
            
            return is_valid
            
        except Exception as e:
            print(f"Session check error: {e}")
            return False


# Глобальный экземпляр
browser_handler = BrowserSessionHandler()


# Предустановленные URL для входа на популярные платформы
LOGIN_URLS = {
    "google": "https://accounts.google.com/signin",
    "youtube": "https://accounts.google.com/signin?service=youtube",
    "tiktok": "https://www.tiktok.com/login",
    "facebook": "https://www.facebook.com/login",
    "instagram": "https://www.instagram.com/accounts/login",
    "twitter": "https://twitter.com/i/flow/login",
    "linkedin": "https://www.linkedin.com/login",
    "reddit": "https://www.reddit.com/login",
    "pinterest": "https://www.pinterest.com/login",
    "vk": "https://vk.com/login",
    "ok": "https://ok.ru/",
    "yandex": "https://passport.yandex.ru/auth",
    "mailru": "https://account.mail.ru/login",
    "telegram": "https://web.telegram.org/",
    "discord": "https://discord.com/login",
    "github": "https://github.com/login",
    "wordpress": "https://wordpress.com/log-in",
    "medium": "https://medium.com/m/signin",
    "quora": "https://www.quora.com/",
    "tumblr": "https://www.tumblr.com/login",
}
