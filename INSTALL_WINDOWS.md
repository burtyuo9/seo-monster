# SEO Monster - Установка на Windows

## 🚀 Быстрая установка (1 клик)

### Вариант 1: PowerShell (Рекомендуется)

Откройте PowerShell **от имени администратора** и выполните:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
irm https://raw.githubusercontent.com/burtyuo9/seo-monster/main/windows-installer/install.ps1 | iex
```

### Вариант 2: CMD

1. Скачайте [install.bat](windows-installer/install.bat)
2. Запустите **от имени администратора**
3. Следуйте инструкциям

### Вариант 3: GUI Приложение

1. Скачайте `SEO Monster.exe` из [Releases](https://github.com/burtyuo9/seo-monster/releases)
2. Запустите приложение
3. Нажмите "Запустить всё"

---

## 📋 Системные требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| ОС | Windows 10 | Windows 11 |
| RAM | 4 GB | 8 GB |
| Диск | 2 GB | 5 GB |
| Python | 3.10+ | 3.11+ |
| Node.js | 18+ | 20+ |

---

## 🔧 Что устанавливается автоматически

Установщик проверит и установит (при необходимости):

- **Python 3.11** - для Backend
- **Node.js 20** - для Frontend  
- **Git** - для клонирования репозитория
- **pnpm** - менеджер пакетов Node.js
- **Все Python зависимости** (FastAPI, uvicorn, и др.)
- **Все Node.js зависимости** (React, Vite, и др.)

---

## 🖥️ GUI Приложение

### Возможности

| Функция | Описание |
|---------|----------|
| 🚀 Запуск/Остановка | Управление Backend и Frontend одним кликом |
| 📊 Мониторинг | Статус сервисов в реальном времени |
| 📋 Логи | Просмотр логов в удобном интерфейсе |
| 🌙/☀️ Темы | Тёмная и светлая тема |
| 🌐 Браузер | Автоматическое открытие UI |

### Скриншот

```
╔════════════════════════════════════════════════════════════╗
║  🦖 SEO Monster v2.0                                  🌙   ║
╠════════════════════════════════════════════════════════════╣
║  ┌─────────────────┐  ┌─────────────────┐                 ║
║  │ ⚙️ Backend (API) │  │ 🖥️ Frontend (UI) │                 ║
║  │ ● Работает      │  │ ● Работает      │                 ║
║  └─────────────────┘  └─────────────────┘                 ║
║                                                            ║
║  [▶️ Запустить всё] [⏹️ Остановить] [🌐 Браузер] [🔄]      ║
║                                                            ║
║  📋 Логи                                                   ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │ [12:34:56] [SUCCESS] Backend запущен                 │ ║
║  │ [12:34:59] [SUCCESS] Frontend запущен                │ ║
║  └──────────────────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════════════════╝
```

---

## 📁 Структура после установки

```
C:\Users\<Username>\seo-monster-app\
├── backend\
│   ├── venv\              # Python виртуальное окружение
│   ├── app\               # API endpoints
│   ├── services\          # Бизнес-логика
│   ├── main.py            # Точка входа
│   └── .env               # ⚠️ Настройте API ключи здесь!
├── frontend\
│   ├── node_modules\      # Node.js зависимости
│   ├── src\               # React компоненты
│   └── dist\              # Собранное приложение
├── start.bat              # 🚀 Быстрый запуск
├── stop.bat               # ⏹️ Остановка
└── Start-SEOMonster.ps1   # PowerShell запуск
```

---

## ⚙️ Настройка API ключей

После установки **обязательно** настройте API ключи:

```
notepad C:\Users\<Username>\seo-monster-app\backend\.env
```

### Бесплатные AI провайдеры (рекомендуется)

```env
# Groq - Llama 3.3 70B (30 req/min бесплатно)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Together AI - Llama 3.3 70B (60 req/min бесплатно)
TOGETHER_API_KEY=xxxxxxxxxxxxx

# Google Gemini - Gemini 1.5 Flash (60 req/min бесплатно)
GOOGLE_AI_API_KEY=xxxxxxxxxxxxx

# DeepSeek - DeepSeek Chat (60 req/min бесплатно)
DEEPSEEK_API_KEY=xxxxxxxxxxxxx

# Mistral AI - Mistral Large (30 req/min бесплатно)
MISTRAL_API_KEY=xxxxxxxxxxxxx
```

### OpenAI (опционально)

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

> 💡 **Совет**: SEO Monster работает полностью автономно с бесплатными провайдерами!

---

## 🚀 Запуск

### Через GUI (рекомендуется)

1. Запустите `SEO Monster.exe`
2. Нажмите **"▶️ Запустить всё"**
3. Дождитесь зелёных индикаторов
4. Нажмите **"🌐 Открыть в браузере"**

### Через скрипты

**CMD:**
```cmd
cd C:\Users\<Username>\seo-monster-app
start.bat
```

**PowerShell:**
```powershell
cd C:\Users\<Username>\seo-monster-app
.\Start-SEOMonster.ps1
```

### Вручную (для разработки)

**Terminal 1 - Backend:**
```cmd
cd C:\Users\<Username>\seo-monster-app\backend
venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```cmd
cd C:\Users\<Username>\seo-monster-app\frontend
pnpm dev
```

---

## 🔗 Адреса

| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:5200 | Веб-интерфейс |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger документация |
| ReDoc | http://localhost:8000/redoc | Альтернативная документация |

---

## 🔧 Устранение неполадок

### Python не найден

```cmd
# Проверка
python --version

# Решение: добавьте в PATH
# C:\Users\<Username>\AppData\Local\Programs\Python\Python311
# C:\Users\<Username>\AppData\Local\Programs\Python\Python311\Scripts
```

### Node.js не найден

```cmd
# Проверка
node --version

# Решение: переустановите с https://nodejs.org/
```

### Порт занят

```cmd
# Найти процесс
netstat -ano | findstr :8000

# Завершить
taskkill /F /PID <PID>
```

### Ошибки зависимостей Backend

```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

### Ошибки зависимостей Frontend

```cmd
cd frontend
rmdir /s /q node_modules
pnpm install
pnpm run build
```

### Белый экран в браузере

```cmd
cd frontend
pnpm run build
```

---

## 📞 Поддержка

- **GitHub Issues**: [Создать issue](https://github.com/burtyuo9/seo-monster/issues)
- **Документация**: [docs/](docs/)

---

## 📄 Лицензия

Приватный проект. Все права защищены.
