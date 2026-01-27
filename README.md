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
*   **Развёртывание:** Bash/CMD/PowerShell скрипты, GUI приложение

---

## ⚙️ Установка

### 🐧 Linux / Ubuntu

```bash
wget https://raw.githubusercontent.com/burtyuo9/seo-monster/main/install.sh
chmod +x install.sh
./install.sh
```

### 🪟 Windows (PowerShell - Рекомендуется)

Откройте PowerShell **от имени администратора** и выполните:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
irm https://raw.githubusercontent.com/burtyuo9/seo-monster/main/windows-installer/install.ps1 | iex
```

### 🪟 Windows (CMD)

1. Скачайте [install.bat](windows-installer/install.bat)
2. Запустите **от имени администратора**
3. Следуйте инструкциям

### 🖥️ Windows GUI

1. Скачайте `SEO Monster.exe` из [Releases](https://github.com/burtyuo9/seo-monster/releases)
2. Запустите приложение
3. Нажмите "▶️ Запустить всё"

📖 Подробная инструкция: [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)

---

## 🏁 Быстрый старт

### Linux / macOS

```bash
cd seo-monster-app
./start.sh  # или вручную:
# Terminal 1: cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000
# Terminal 2: cd frontend && pnpm preview --host 0.0.0.0 --port 5200
```

### Windows

```cmd
cd seo-monster-app
start.bat
```

Или через PowerShell:
```powershell
.\Start-SEOMonster.ps1
```

Откройте `http://localhost:5200` в браузере.

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

## 📁 Структура проекта

```
seo-monster/
├── backend/                 # Python FastAPI backend
│   ├── app/                 # API endpoints
│   ├── services/            # Бизнес-логика и AI сервисы
│   ├── main.py              # Точка входа
│   └── requirements.txt     # Python зависимости
├── frontend/                # React TypeScript frontend
│   ├── src/                 # Компоненты и логика
│   └── package.json         # Node.js зависимости
├── windows-installer/       # Windows установщик и GUI
│   ├── install.bat          # CMD установщик
│   ├── install.ps1          # PowerShell установщик
│   └── seo_monster_gui.py   # GUI приложение
├── start.bat                # Windows запуск
├── stop.bat                 # Windows остановка
├── Start-SEOMonster.ps1     # PowerShell запуск
└── install.sh               # Linux установщик
```

---

## 🤝 Контрибьюторы

*   **burtyuo9** - Lead Developer
*   **Manus AI** - AI-ассистент, разработка и документация

---

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [Установка Linux](INSTALL.md) | Инструкция для Ubuntu/Debian |
| [Установка Windows](INSTALL_WINDOWS.md) | Инструкция для Windows 10/11 |
| [Руководство пользователя](docs/USER_GUIDE.md) | Полное описание всех модулей |
| [AI Провайдеры](docs/AI_PROVIDERS.md) | Настройка AI провайдеров |

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
