# SEO Monster - Windows Installation Guide

## 🚀 Быстрая установка

### Вариант 1: PowerShell (Рекомендуется)

1. Откройте PowerShell **от имени администратора**
2. Выполните команду:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/burtyuo9/seo-monster/main/windows-installer/install.ps1 | iex
```

### Вариант 2: CMD (Batch)

1. Скачайте `install.bat`
2. Запустите **от имени администратора**
3. Следуйте инструкциям на экране

### Вариант 3: GUI Приложение

1. Скачайте `SEO Monster.exe` из релизов
2. Запустите приложение
3. Используйте графический интерфейс для управления

---

## 📋 Что устанавливается автоматически

Установщик автоматически проверит и установит (при необходимости):

| Компонент | Версия | Описание |
|-----------|--------|----------|
| Python | 3.11+ | Для backend |
| Node.js | 20+ | Для frontend |
| Git | Latest | Для клонирования |
| pnpm | Latest | Менеджер пакетов |

---

## 🖥️ GUI Приложение

### Возможности

- **Запуск/Остановка** Backend и Frontend одним кликом
- **Мониторинг статуса** сервисов в реальном времени
- **Логи** в удобном интерфейсе
- **Тёмная/Светлая** тема
- **Автоматическое** открытие браузера

### Скриншот

```
╔════════════════════════════════════════════════════════════╗
║  🦖 SEO Monster v2.0                                  🌙   ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  ┌─────────────────┐  ┌─────────────────┐                 ║
║  │ ⚙️ Backend (API) │  │ 🖥️ Frontend (UI) │                 ║
║  │ ● Работает      │  │ ● Работает      │                 ║
║  └─────────────────┘  └─────────────────┘                 ║
║                                                            ║
║  [▶️ Запустить всё] [⏹️ Остановить] [🌐 Браузер] [🔄]      ║
║                                                            ║
║  ┌──────────────────────────────────────────────────────┐ ║
║  │ 📋 Логи                                              │ ║
║  │ [12:34:56] [INFO] Backend запущен                   │ ║
║  │ [12:34:59] [INFO] Frontend запущен                  │ ║
║  │ [12:35:02] [SUCCESS] Статус обновлён                │ ║
║  └──────────────────────────────────────────────────────┘ ║
║                                                            ║
║  📁 C:\Users\User\seo-monster-app                         ║
╚════════════════════════════════════════════════════════════╝
```

---

## 📁 Структура после установки

```
C:\Users\<Username>\seo-monster-app\
├── backend\
│   ├── venv\              # Python виртуальное окружение
│   ├── app\               # Код приложения
│   ├── services\          # Сервисы
│   ├── main.py            # Точка входа
│   ├── requirements.txt   # Python зависимости
│   └── .env               # Конфигурация (API ключи)
├── frontend\
│   ├── node_modules\      # Node.js зависимости
│   ├── src\               # Исходный код
│   ├── dist\              # Собранное приложение
│   └── package.json       # Node.js конфигурация
├── start.bat              # Скрипт запуска
├── stop.bat               # Скрипт остановки
└── Start-SEOMonster.ps1   # PowerShell запуск
```

---

## ⚙️ Настройка API ключей

После установки отредактируйте файл `.env`:

```
C:\Users\<Username>\seo-monster-app\backend\.env
```

### Бесплатные AI провайдеры (рекомендуется)

```env
# Groq - 30 req/min бесплатно
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Together AI - 60 req/min бесплатно
TOGETHER_API_KEY=xxxxxxxxxxxxx

# Google Gemini - 60 req/min бесплатно
GOOGLE_AI_API_KEY=xxxxxxxxxxxxx

# DeepSeek - 60 req/min бесплатно
DEEPSEEK_API_KEY=xxxxxxxxxxxxx
```

### OpenAI (опционально)

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

---

## 🚀 Запуск

### Через GUI

1. Запустите `SEO Monster.exe`
2. Нажмите "▶️ Запустить всё"
3. Дождитесь запуска сервисов
4. Нажмите "🌐 Открыть в браузере"

### Через скрипты

```cmd
cd C:\Users\<Username>\seo-monster-app
start.bat
```

### Вручную

**Terminal 1 - Backend:**
```cmd
cd C:\Users\<Username>\seo-monster-app\backend
venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```cmd
cd C:\Users\<Username>\seo-monster-app\frontend
pnpm preview --host 0.0.0.0 --port 5200
```

---

## 🔧 Устранение неполадок

### Python не найден

```cmd
# Проверьте установку
python --version

# Если не работает, добавьте в PATH:
# C:\Users\<Username>\AppData\Local\Programs\Python\Python311
# C:\Users\<Username>\AppData\Local\Programs\Python\Python311\Scripts
```

### Node.js не найден

```cmd
# Проверьте установку
node --version

# Если не работает, переустановите с https://nodejs.org/
```

### Порт занят

```cmd
# Найти процесс на порту 8000
netstat -ano | findstr :8000

# Завершить процесс
taskkill /F /PID <PID>
```

### Ошибки зависимостей

```cmd
# Переустановка backend зависимостей
cd backend
venv\Scripts\activate
pip install -r requirements.txt --force-reinstall

# Переустановка frontend зависимостей
cd frontend
pnpm install --force
pnpm run build
```

---

## 📞 Поддержка

- **GitHub Issues**: [github.com/burtyuo9/seo-monster/issues](https://github.com/burtyuo9/seo-monster/issues)
- **Документация**: [docs/](../docs/)

---

## 📄 Лицензия

Приватный проект. Все права защищены.
