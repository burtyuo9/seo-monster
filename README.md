# SEO Monster - Autonomous AI SEO System

**SEO Monster** — это полностью автономная система на базе AI, предназначенная для комплексного SEO-продвижения сайтов. Она автоматизирует рутинные задачи, генерирует контент и самостоятельно принимает решения для улучшения позиций в поисковой выдаче.

![Dashboard Screenshot](https://raw.githubusercontent.com/burtyuo9/seo-monster/main/docs/images/dashboard_main.png)

---

## 🚀 Ключевые возможности

*   **Автономный режим (Autopilot):** Запустите систему, и она будет работать 24/7, выполняя полный цикл SEO-задач.
*   **AI-генерация контента:** Создание уникальных, SEO-оптимизированных статей, обзоров и FAQ на базе GPT-4.
*   **Анализ семантики:** Автоматический сбор и кластеризация ключевых слов (основные, long-tail, вопросы).
*   **Анализ конкурентов:** Изучение стратегий, ссылочного профиля и контента конкурентов.
*   **Технический SEO-аудит:** Проверка сайта на ошибки, скорость загрузки и другие критические параметры.
*   **Умная индексация:** Автоматическая отправка новых страниц в Google, Bing, Yandex через IndexNow и Sitemap Ping.
*   **Гео-таргетинг:** Настройка и фильтрация трафика по странам и регионам.
*   **AI-самообучение:** Система анализирует результаты, проводит SWOT-анализ и корректирует свою стратегию.
*   **Мультиязычный интерфейс:** Поддержка русского и английского языков.

---

## 🛠️ Стек технологий

*   **Backend:** Python, FastAPI, SQLAlchemy
*   **Frontend:** React, TypeScript, Vite, TailwindCSS, pnpm
*   **AI:** Groq, Together AI, HuggingFace, Ollama, Cohere, Mistral, DeepSeek, OpenRouter, Google Gemini, Cloudflare (OpenAI опционально)
*   **База данных:** SQLite
*   **Развёртывание:** Bash-скрипт

---

## ⚙️ Установка

Для быстрой установки на Ubuntu 20.04+ используйте наш скрипт:

```bash
wget https://raw.githubusercontent.com/burtyuo9/seo-monster/main/install.sh
chmod +x install.sh
./install.sh
```

После установки укажите API ключи в файле `seo-monster-app/backend/.env`. Система работает **без OpenAI** с бесплатными провайдерами!

Подробная инструкция доступна в файле [INSTALL.md](INSTALL.md).

---

## 🏁 Быстрый старт

1.  **Запустите Backend:**
    ```bash
    cd seo-monster-app/backend
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

2.  **Запустите Frontend (в новом терминале):**
    ```bash
    cd seo-monster-app/frontend
    pnpm preview --host 0.0.0.0 --port 5200
    ```

3.  Откройте `http://localhost:5200` в вашем браузере.

---

## 🤖 AI Providers (Бесплатные)

SEO Monster работает **полностью автономно без OpenAI**:

| Provider | Model | Free Tier |
|----------|-------|----------|
| **Groq** | Llama 3.3 70B | ✅ 30 req/min |
| **Together AI** | Llama 3.3 70B | ✅ 60 req/min |
| **HuggingFace** | Mixtral 8x7B | ✅ 30 req/min |
| **Ollama** | Llama 3.2 (local) | ✅ Unlimited |
| **Cohere** | Command R+ | ✅ 20 req/min |
| **Mistral AI** | Mistral Large | ✅ 30 req/min |
| **DeepSeek** | DeepSeek Chat | ✅ 60 req/min |
| **OpenRouter** | Free models | ✅ 20 req/min |
| **Google Gemini** | Gemini 1.5 Flash | ✅ 60 req/min |
| **Cloudflare** | Llama 3.1 8B | ✅ 50 req/min |

📖 Подробнее: [docs/AI_PROVIDERS.md](docs/AI_PROVIDERS.md)

---

## 🤝 Контрибьюторы

*   **burtyuo9** - Lead Developer
*   **Manus AI** - AI-ассистент, разработка и документация

---

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [Руководство по установке](docs/INSTALLATION.md) | Подробные инструкции для всех ОС |
| [Руководство пользователя](docs/USER_GUIDE.md) | Полное описание всех 11 модулей |
| [AI Провайдеры](docs/AI_PROVIDERS.md) | Настройка OpenAI, Anthropic, Google AI |

---

## 🐳 Docker

```bash
git clone https://github.com/burtyuo9/seo-monster.git
cd seo-monster
cp .env.example .env
docker compose up -d
```

---

## 📄 Лицензия

Этот проект является приватным. Все права защищены.
