# 🤖 SEO Monster - AI Providers & Agents

## Обзор

SEO Monster поддерживает работу с множеством бесплатных AI-провайдеров и может функционировать **полностью автономно без OpenAI**. Система автоматически переключается между провайдерами для обеспечения бесперебойной работы.

---

## 🆓 Бесплатные LLM Провайдеры

### 1. Groq (Рекомендуется)
- **Модель**: `llama-3.3-70b-versatile`
- **Лимит**: 30 запросов/мин
- **Токены**: до 8,192
- **Регистрация**: [console.groq.com](https://console.groq.com)
- **Особенности**: Самый быстрый inference, отличное качество

### 2. Together AI
- **Модель**: `meta-llama/Llama-3.3-70B-Instruct-Turbo`
- **Лимит**: 60 запросов/мин (free tier)
- **Токены**: до 4,096
- **Регистрация**: [together.ai](https://together.ai)
- **Особенности**: Большой выбор моделей

### 3. HuggingFace Inference
- **Модель**: `mistralai/Mixtral-8x7B-Instruct-v0.1`
- **Лимит**: 30 запросов/мин
- **Токены**: до 4,096
- **Регистрация**: [huggingface.co](https://huggingface.co)
- **Особенности**: Доступ к тысячам open-source моделей

### 4. Ollama (Локальный)
- **Модели**: `llama3.2`, `mistral`, `codellama`, `phi3`
- **Лимит**: Без ограничений
- **Токены**: до 8,192
- **Установка**: [ollama.ai](https://ollama.ai)
- **Особенности**: Полностью локальный, приватный, без интернета

### 5. Cohere
- **Модель**: `command-r-plus`
- **Лимит**: 20 запросов/мин (free tier)
- **Токены**: до 4,096
- **Регистрация**: [cohere.com](https://cohere.com)
- **Особенности**: Отличный для RAG и поиска

### 6. Mistral AI
- **Модель**: `mistral-large-latest`
- **Лимит**: 30 запросов/мин
- **Токены**: до 8,192
- **Регистрация**: [mistral.ai](https://mistral.ai)
- **Особенности**: Европейский провайдер, GDPR-compliant

### 7. DeepSeek
- **Модель**: `deepseek-chat`
- **Лимит**: 60 запросов/мин
- **Токены**: до 8,192
- **Регистрация**: [deepseek.com](https://deepseek.com)
- **Особенности**: Отличный для кода и технических задач

### 8. OpenRouter (Free Models)
- **Модель**: `meta-llama/llama-3.2-3b-instruct:free`
- **Лимит**: 20 запросов/мин
- **Токены**: до 4,096
- **Регистрация**: [openrouter.ai](https://openrouter.ai)
- **Особенности**: Агрегатор множества бесплатных моделей

### 9. Google Gemini
- **Модель**: `gemini-1.5-flash`
- **Лимит**: 60 запросов/мин
- **Токены**: до 8,192
- **Регистрация**: [aistudio.google.com](https://aistudio.google.com)
- **Особенности**: Мультимодальный, быстрый

### 10. Cloudflare Workers AI
- **Модель**: `@cf/meta/llama-3.1-8b-instruct`
- **Лимит**: 50 запросов/мин
- **Токены**: до 2,048
- **Регистрация**: [cloudflare.com](https://cloudflare.com)
- **Особенности**: Edge computing, низкая задержка

---

## 🤖 Встроенные AI-Агенты

SEO Monster включает 9 специализированных AI-агентов:

| Агент | Роль | Возможности |
|-------|------|-------------|
| **seo_writer** | Контент-райтер | Статьи, мета-теги, заголовки |
| **keyword_specialist** | Исследователь ключей | Анализ, search intent, long-tail |
| **competitor_analyst** | Аналитик конкурентов | Gap-анализ, стратегии |
| **tech_seo_expert** | Технический SEO | Аудит, schema, скорость |
| **content_editor** | Редактор | Корректура, стиль, читаемость |
| **translator** | Переводчик | Локализация, мультиязычный SEO |
| **data_analyst** | Аналитик данных | Отчёты, прогнозы, тренды |
| **creative_writer** | Креативный райтер | Storytelling, вирусный контент |
| **fact_checker** | Фактчекер | Проверка источников, точность |

---

## 🌐 Внешние AI-Сервисы

SEO Monster может взаимодействовать с внешними бесплатными AI:

| Сервис | Возможности | Статус |
|--------|-------------|--------|
| **Perplexity AI** | Поиск, исследования, факты | ✅ Бесплатно |
| **You.com AI** | Поиск, чат, код | ✅ Бесплатно |
| **Phind** | Технический поиск, код | ✅ Бесплатно |
| **Poe by Quora** | Множество моделей | ✅ Бесплатно |
| **ChatGPT (Free)** | Чат, анализ, письмо | ✅ Бесплатно |
| **Claude (Free)** | Чат, анализ, код | ✅ Бесплатно |
| **Google Gemini** | Чат, мультимодальный | ✅ Бесплатно |
| **Microsoft Copilot** | Чат, поиск, изображения | ✅ Бесплатно |
| **HuggingChat** | Open-source модели | ✅ Бесплатно |
| **Forefront AI** | GPT-4, Claude, персоны | ✅ Бесплатно |

---

## ⚙️ Настройка провайдеров

### Через UI

1. Откройте **AI Providers** в боковом меню
2. Выберите вкладку **LLM Провайдеры**
3. Нажмите 🔑 для установки API ключа
4. Включите/выключите провайдера кнопкой

### Через .env файл

```env
# Бесплатные провайдеры (получите ключи на их сайтах)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
TOGETHER_API_KEY=xxxxxxxxxxxxx
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx
COHERE_API_KEY=xxxxxxxxxxxxx
MISTRAL_API_KEY=xxxxxxxxxxxxx
DEEPSEEK_API_KEY=xxxxxxxxxxxxx
OPENROUTER_API_KEY=xxxxxxxxxxxxx
GOOGLE_API_KEY=xxxxxxxxxxxxx

# Локальный Ollama (без ключа)
OLLAMA_BASE_URL=http://localhost:11434

# Опционально: OpenAI (платный)
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

### Приоритет провайдеров

Система автоматически выбирает провайдера по приоритету:

1. **Groq** (если доступен) — самый быстрый
2. **Together AI** — хорошее качество
3. **HuggingFace** — надёжный fallback
4. **Ollama** — локальный, если настроен
5. **Остальные** — по порядку

При ошибке система автоматически переключается на следующий провайдер.

---

## 🔄 Автоматическое переключение

SEO Monster автоматически:

- ✅ Определяет доступность провайдера
- ✅ Переключается при rate limit
- ✅ Выбирает оптимальный провайдер для задачи
- ✅ Балансирует нагрузку между провайдерами
- ✅ Кэширует успешные ответы

---

## 📊 Мониторинг

В разделе **AI Providers** доступна статистика:

- Количество активных провайдеров
- Success rate каждого агента
- Общее число запросов
- Статус подключения внешних сервисов

---

## 🚀 Работа без интернета

Для полностью автономной работы без интернета:

1. Установите [Ollama](https://ollama.ai)
2. Скачайте модель: `ollama pull llama3.2`
3. Включите Ollama в настройках SEO Monster
4. Отключите остальные провайдеры

Система будет работать полностью локально!

---

## 🧠 Система самообучения и автообновления

### Автоматическое обучение агентов

Monster автоматически учится на результатах своей работы:

1. **Запись результатов** — каждая задача записывается с оценкой качества
2. **Анализ паттернов** — система выявляет успешные и неуспешные паттерны
3. **Эволюция агентов** — агенты автоматически улучшают свои промпты
4. **Обновление провайдеров** — автоматическое переключение на здоровые провайдеры
5. **Пополнение агентов** — автоматическое создание новых агентов для новых моделей

### Параллельное выполнение

Все SEO-задачи выполняются параллельно несколькими агентами:

```python
from backend.services.parallel_seo_executor import run_parallel_seo

# Запуск параллельных задач
tasks = [
    {"type": "keyword_research", "data": {"topic": "crypto"}},
    {"type": "content_generation", "data": {"topic": "bitcoin"}},
    {"type": "competitor_analysis", "data": {"competitors": [...]}}
]

results = await run_parallel_seo("example.com", tasks)
```

### Monster Core API

```python
from backend.services.monster_core import monster

# Запуск автопилота
results = await monster.run_full_autopilot(
    domain="example.com",
    duration_minutes=30,
    config={"articles_per_cycle": 5}
)

# Получение статуса
status = monster.get_status()

# Получение активных агентов
agents = monster.get_active_agents()
```

---

## 📝 Примеры использования

### Python API

```python
from services.ai_providers import AIProviderManager

# Инициализация
manager = AIProviderManager()

# Генерация текста (автовыбор провайдера)
response = await manager.generate(
    prompt="Write SEO article about virtual cards",
    max_tokens=2000
)

# Использование конкретного провайдера
response = await manager.generate(
    prompt="Analyze keywords",
    provider="groq",
    model="llama-3.3-70b-versatile"
)
```

### AI-to-AI коммуникация

```python
from services.ai_communication import ai_network, ai_collaboration

# Получить всех агентов
agents = ai_network.get_all_agents()

# Создать коллаборацию для задачи
collab_id = await ai_collaboration.create_collaboration(
    task_name="content_creation",
    required_roles=[AIAgentRole.CONTENT_WRITER, AIAgentRole.EDITOR],
    task_description="Create and edit SEO article"
)

# Выполнить задачу
results = await ai_collaboration.execute_collaborative_task(
    collab_id, 
    {"topic": "Virtual cards for crypto"}
)
```

---

## 🆘 Поддержка

При проблемах с AI провайдерами:

1. Проверьте статус провайдера в UI
2. Убедитесь в наличии API ключа
3. Проверьте rate limits
4. Попробуйте другой провайдер

**GitHub Issues**: [github.com/burtyuo9/seo-monster/issues](https://github.com/burtyuo9/seo-monster/issues)
