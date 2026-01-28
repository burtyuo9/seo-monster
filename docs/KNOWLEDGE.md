# SEO Monster - Knowledge Base

## Архитектура системы

### Backend (Python/FastAPI)
- **Порт:** 8000
- **Фреймворк:** FastAPI
- **База данных:** JSON файлы (можно мигрировать на PostgreSQL)
- **AI интеграция:** OpenAI API (опционально), локальные LLM

### Frontend (React/Vite)
- **Порт:** 5200
- **Фреймворк:** React 18 + TypeScript
- **Сборщик:** Vite
- **Стили:** Inline CSS (можно мигрировать на Tailwind)

### Структура проекта
```
seo-monster/
├── backend/
│   ├── app/
│   │   └── api/           # API routes
│   ├── services/          # Business logic
│   ├── data/              # JSON storage
│   └── main.py            # Entry point
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   └── App.tsx        # Main app
│   └── dist/              # Build output
├── docs/                  # Documentation
└── landings/              # Generated HTML pages
```

## API Endpoints

### Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/system/status | GET | System health check |
| /api/sites/ | GET/POST | Manage sites |
| /api/content/generate | POST | Generate content |

### Publishing
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/publishing/publish | POST | Publish landing |
| /api/publishing/preview/{slug} | GET | Preview landing |
| /api/publishing/list | GET | List all landings |

### AWS SES
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/ses/keys | GET/POST | Manage AWS keys |
| /api/ses/content | GET | List email content |
| /api/ses/lists | GET | List recipients |

## Интеграции

### Manus Integration
- **Тип:** Scheduled Task
- **Функция:** Периодическая проверка VPS и публикация контента на MANUS.space
- **Endpoint:** /api/publishing/pending - получение контента для публикации

### AWS SES
- **Регионы:** us-east-1, us-west-2, eu-west-1, eu-central-1, ap-southeast-1, ap-northeast-1
- **Требования:** boto3, валидные AWS credentials с SES permissions

### AI Providers
- **OpenAI:** Опциональная интеграция через API key
- **Локальные LLM:** Ollama, LM Studio (в разработке)
- **Бесплатные API:** Hugging Face, Together AI (в разработке)

## Best Practices

### Деплой на Windows VPS
1. Установить Python 3.11+, Node.js 22+
2. Клонировать репозиторий
3. Создать виртуальное окружение Python
4. Установить зависимости
5. Настроить firewall
6. Запустить backend и frontend

### Генерация контента
1. Использовать конкретные темы (не общие)
2. Указывать язык и тип контента
3. Проверять preview перед публикацией

### Email кампании
1. Верифицировать домен в AWS SES
2. Начинать с небольших объемов (warm-up)
3. Мониторить bounce rate и complaints

---
*Last updated: 2026-01-28*
