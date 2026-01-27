# AWS SES Warm-up Manager - Полный функционал

## Обзор
Модуль автоматического прогрева (Warm-up) для AWS SES ключей обеспечивает постепенное наращивание объемов отправки email для построения репутации отправителя и достижения высокой доставляемости.

## Реализованные функции

### 1. Создание планов прогрева
- **3 стратегии прогрева:**
  - **Conservative (21 день)** - медленный и безопасный прогрев, идеален для новых доменов
  - **Moderate (14 дней)** - сбалансированный прогрев, подходит для большинства случаев  
  - **Aggressive (7 дней)** - быстрый прогрев, повышенный риск проблем с доставляемостью

- **Настраиваемые параметры:**
  - Целевой дневной объем отправки
  - Максимальный bounce rate (по умолчанию 5%)
  - Максимальный complaint rate (по умолчанию 0.1%)
  - Автоматическая пауза при превышении порогов

### 2. Автоматический режим (Auto Mode)
- **Планировщик отправки:**
  - Настраиваемое время отправки (час и минута)
  - Автоматическое выполнение каждый день
  - Интеграция с Auto-Executor

- **Конфигурация:**
  - Выбор списка получателей
  - Выбор шаблона письма
  - Email и имя отправителя

### 3. Warmup Executor
- **Автоматическое выполнение:**
  - Фоновый планировщик с интервалом проверки 60 секунд
  - Проверка квоты AWS перед отправкой
  - Соблюдение rate limit AWS SES

- **Статусы:**
  - Running/Stopped индикатор
  - Количество активных планов
  - Количество планов в автоматическом режиме

### 4. Мониторинг и статистика
- **Общая статистика:**
  - Total Plans
  - In Progress
  - Completed
  - Paused
  - Emails Sent
  - Overall Delivery Rate

- **Статистика по плану:**
  - Total Sent
  - Delivery Rate
  - Bounce Rate
  - Open Rate
  - Health Score (0-100)
  - Reputation Trend (improving/stable/declining)

### 5. Timeline (Расписание)
- **Детальная информация по дням:**
  - Target volume
  - Actual sent
  - Delivered
  - Bounce %
  - Open %
  - Status (completed/current/pending)

### 6. Execution Log
- **Лог выполнения:**
  - Timestamp
  - Action (execute/simulate/start/pause)
  - Status (success/failed/warning)
  - Details (sent, delivered, bounced, etc.)
  - Errors

### 7. Рекомендации
- **Типы рекомендаций:**
  - Critical - требуют немедленного внимания
  - Warning - предупреждения
  - Info - информационные

- **Примеры:**
  - Высокий bounce rate
  - Низкий open rate
  - Необходимость паузы
  - Рекомендации по улучшению

### 8. Управление планами
- **Действия:**
  - Start - запуск плана
  - Pause - приостановка с указанием причины
  - Resume - возобновление
  - Delete - удаление
  - Execute Now - немедленное выполнение
  - Simulate Day - симуляция дня для тестирования

- **Настройки плана:**
  - Auto Mode toggle
  - Send time
  - Recipient list
  - Email content
  - From email/name
  - Quality thresholds

## API Endpoints

### Warmup Plans
- `GET /api/ses/warmup/stats` - общая статистика
- `GET /api/ses/warmup/plans` - список планов
- `POST /api/ses/warmup/plans` - создание плана
- `GET /api/ses/warmup/plans/{id}` - детали плана
- `PUT /api/ses/warmup/plans/{id}` - обновление настроек
- `DELETE /api/ses/warmup/plans/{id}` - удаление плана
- `POST /api/ses/warmup/plans/{id}/start` - запуск
- `POST /api/ses/warmup/plans/{id}/pause` - пауза
- `POST /api/ses/warmup/plans/{id}/resume` - возобновление
- `GET /api/ses/warmup/plans/{id}/recommendations` - рекомендации
- `GET /api/ses/warmup/plans/{id}/timeline` - timeline

### Warmup Executor
- `GET /api/ses/warmup/executor/status` - статус executor
- `POST /api/ses/warmup/executor/start` - запуск executor
- `POST /api/ses/warmup/executor/stop` - остановка executor
- `GET /api/ses/warmup/executor/log` - лог выполнения
- `POST /api/ses/warmup/execute/{id}` - ручное выполнение
- `POST /api/ses/warmup/simulate/{id}` - симуляция

## Файлы модуля

### Backend
- `/backend/services/ses_warmup.py` - основной сервис warmup
- `/backend/services/warmup_executor.py` - executor для автоматического выполнения
- `/backend/app/api/ses_routes.py` - API endpoints

### Frontend
- `/frontend/src/components/SESWarmup.tsx` - UI компонент

## Интеграции
- **AWS SES Service** - отправка писем через AWS SES
- **Recipient Manager** - получение списков получателей
- **Email Content Generator** - получение контента писем

## Безопасность
- Автоматическая пауза при превышении bounce/complaint rate
- Проверка квоты AWS перед отправкой
- Соблюдение rate limit
- Логирование всех операций
