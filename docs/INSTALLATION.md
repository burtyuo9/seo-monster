'''
# SEO Monster - Инструкция по установке

**Автор:** Manus AI
**Версия:** 3.0 (Автономная)
**Последнее обновление:** 27.01.2026

## 1. Ключевые особенности

-   **Полная автономность:** SEO Monster работает **без внешних AI API** по умолчанию. Он использует собственный движок для анализа и генерации контента.
-   **Опциональный AI:** Вы можете *по желанию* подключить внешних AI-провайдеров (бесплатных или платных) для расширения возможностей.
-   **Кроссплатформенность:** Работает на Linux, macOS и Windows (через Docker или WSL).

## 2. Требования

-   **Сервер/VPS/Локальная машина** с 2+ GB RAM.
-   **Docker** и **Docker Compose** (для рекомендуемого способа установки).
-   *Или* **Python 3.9+**, **Node.js 18+** и **pnpm** (для ручной установки).
-   **Git**.

## 3. Установка

### Docker (Рекомендуется)

Это самый простой и надежный способ. Все зависимости изолированы в контейнерах.

**Шаг 1: Клонировать репозиторий**

```bash
git clone https://github.com/burtyuo9/seo-monster.git
cd seo-monster
```

**Шаг 2: Создать файл конфигурации**

Скопируйте пример файла `.env`.

```bash
cp .env.example .env
```

**Шаг 3: Запустить Docker Compose**

Эта команда скачает образы, создаст контейнеры и запустит приложение в фоновом режиме.

```bash
docker compose up -d
```

Приложение будет доступно через несколько минут.

-   **Frontend:** `http://localhost:5173`
-   **Backend API:** `http://localhost:8000`

### Ручная установка

Этот способ требует ручной установки всех зависимостей.

**Шаг 1: Клонировать репозиторий**

```bash
git clone https://github.com/burtyuo9/seo-monster.git
cd seo-monster
```

**Шаг 2: Настройка Backend**

```bash
# Перейдите в директорию backend
cd backend

# Создайте и активируйте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Создайте файл .env
cp ../.env.example .env
```

**Шаг 3: Настройка Frontend**

```bash
# Вернитесь в корневую директорию и перейдите в frontend
cd ../frontend

# Установите pnpm (если не установлен)
npm install -g pnpm

# Установите зависимости
pnpm install

# Соберите проект
pnpm build
```

## 4. Конфигурация

Основной файл конфигурации - `.env` в корневой директории проекта.

```ini
# Основные настройки
APP_SECRET_KEY=your_strong_secret_key

# Настройки базы данных (для Docker)
DB_HOST=db
DB_PORT=3306
DB_USER=user
DB_PASSWORD=password
DB_NAME=seomonster

# --- Опциональные AI Провайдеры ---
# SEO Monster работает автономно. Эти ключи НЕ обязательны.

# OpenAI
OPENAI_API_KEY=

# Anthropic
ANTHROPIC_API_KEY=

# Google Gemini
GEMINI_API_KEY=

# Другие провайдеры...
GROQ_API_KEY=
MISTRAL_API_KEY=
```

**Важно:** Вам **не нужно** заполнять ключи AI для базовой работы. Система полностью автономна.

## 5. Запуск приложения

Если вы использовали **ручную установку**, вам нужно запустить два процесса в двух разных терминалах.

**Терминал 1: Запуск Backend**

```bash
cd seo-monster/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Терминал 2: Запуск Frontend**

```bash
cd seo-monster/frontend
pnpm dev --host
```

Откройте `http://localhost:5173` в вашем браузере.

## 6. Обновление

**Для Docker:**

```bash
cd seo-monster
docker compose pull
docker compose up -d --force-recreate
```

**Для ручной установки:**

```bash
cd seo-monster
git pull origin main

# Обновить backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Обновить frontend
cd ../frontend
pnpm install
pnpm build
```
'''
