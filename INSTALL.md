# Инструкция по установке SEO Monster

Это руководство поможет вам установить и настроить SEO Monster на вашем сервере (Ubuntu 20.04+).

## Содержание
1.  [Требования](#требования)
2.  [Автоматическая установка (в 1 клик)](#автоматическая-установка)
3.  [Ручная установка](#ручная-установка)
    *   [Клонирование репозитория](#1-клонирование-репозитория)
    *   [Настройка Backend](#2-настройка-backend)
    *   [Настройка Frontend](#3-настройка-frontend)
4.  [Запуск приложения](#запуск-приложения)
5.  [Обновление](#обновление)

---

## Требования

*   **Сервер/VPS** с Ubuntu 20.04 или новее
*   **Минимум 2GB RAM**
*   **Python 3.8+**
*   **Node.js 16+**
*   **Git**
*   **API-ключ OpenAI**

---

## Автоматическая установка

Самый простой и быстрый способ начать работу. Скрипт автоматически установит все зависимости, настроит окружение и подготовит приложение к запуску.

1.  **Скачайте скрипт установки:**

    ```bash
    wget https://raw.githubusercontent.com/burtyuo9/seo-monster/main/install.sh
    ```

2.  **Сделайте его исполняемым:**

    ```bash
    chmod +x install.sh
    ```

3.  **Запустите установщик:**

    ```bash
    ./install.sh
    ```

4.  **Настройте API-ключ:**

    После завершения установки откройте файл конфигурации и добавьте ваш ключ OpenAI:

    ```bash
    nano seo-monster-app/backend/.env
    ```

    Замените `YOUR_OPENAI_API_KEY` на ваш реальный ключ.

---

## Ручная установка

Если вы предпочитаете контролировать каждый шаг, следуйте этой инструкции.

### 1. Клонирование репозитория

```bash
git clone https://github.com/burtyuo9/seo-monster.git seo-monster-app
cd seo-monster-app
```

### 2. Настройка Backend

Backend написан на Python с использованием FastAPI.

```bash
# Перейдите в директорию backend
cd backend

# Создайте и активируйте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Создайте файл .env из примера
cp .env.example .env

# Отредактируйте .env и добавьте ваш API-ключ
nano .env
```

### 3. Настройка Frontend

Frontend написан на React с использованием Vite и pnpm.

```bash
# Перейдите в директорию frontend
cd ../frontend

# Установите pnpm, если он не установлен
npm install -g pnpm

# Установите зависимости
pnpm install

# Соберите проект для продакшена
pnpm run build
```

---

## Запуск приложения

Для работы SEO Monster необходимо запустить два процесса: backend и frontend.

1.  **Запустите Backend (в первом терминале):**

    ```bash
    cd seo-monster-app/backend
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

2.  **Запустите Frontend (во втором терминале):**

    ```bash
    cd seo-monster-app/frontend
    pnpm preview --host 0.0.0.0 --port 5200
    ```

После этого откройте в браузере `http://ВАШ_IP_АДРЕС:5200`, и вы увидите панель управления SEO Monster.

---

## Обновление

Для обновления до последней версии выполните следующие шаги:

```bash
cd seo-monster-app

# Скачайте последние изменения
git pull origin main

# Обновите backend зависимости
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Обновите frontend зависимости и пересоберите проект
cd ../frontend
pnpm install
pnpm run build
```
