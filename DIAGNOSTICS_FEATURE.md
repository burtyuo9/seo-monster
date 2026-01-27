# SEO Monster - Diagnostics & Auto-Fix Module v2.0

## Обзор

Комплексная система диагностики и автоматического исправления ошибок для SEO Monster. Модуль обеспечивает мониторинг всех компонентов системы, выявление проблем и их автоматическое устранение.

## Ключевые возможности

### 1. Расширенная диагностика (43 проверки)

| Категория | Кол-во проверок | Описание |
|-----------|-----------------|----------|
| **API** | 3 | Проверка здоровья API, endpoints, response times |
| **File System** | 5 | Дисковое пространство, права доступа, структура директорий |
| **Services** | 4 | Backend, Frontend, Database, Cache |
| **AI** | 4 | OpenAI API, модели, лимиты, конфигурация |
| **Email** | 4 | SMTP, шаблоны, очереди, доставляемость |
| **TDS** | 5 | Traffic Distribution System, правила, редиректы |
| **Integrations** | 5 | AWS SES, внешние API, webhooks |
| **Configuration** | 3 | Env variables, config files, secrets |
| **Dependencies** | 2 | Python packages, Node modules |
| **Performance** | 3 | Memory, CPU, Response times |
| **Security** | 5 | SSL, CORS, Auth, Permissions |

### 2. Уровни серьезности (Severity)

- **Critical** - Критические проблемы, требующие немедленного внимания
- **High** - Серьезные проблемы, влияющие на работу системы
- **Medium** - Проблемы средней важности
- **Low** - Незначительные проблемы или рекомендации

### 3. Health Score (0-100)

Система рассчитывает общий показатель здоровья системы:
- **90-100**: Отлично (зеленый)
- **70-89**: Хорошо (желтый)
- **50-69**: Требует внимания (оранжевый)
- **0-49**: Критическое состояние (красный)

### 4. Автоматическое исправление (Auto-Fix)

Модуль может автоматически исправлять следующие проблемы:
- Создание отсутствующих директорий
- Установка правильных прав доступа
- Очистка временных файлов
- Перезапуск зависших сервисов
- Обновление конфигурации

### 5. Рекомендации

Каждая проверка включает контекстные рекомендации по устранению проблем.

## API Endpoints

### Основные

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/diagnostics/status` | GET | Текущий статус диагностики |
| `/api/diagnostics/checks` | GET | Список доступных проверок |
| `/api/diagnostics/categories` | GET | Список категорий |

### Запуск проверок

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/diagnostics/run-all` | POST | Запуск всех проверок |
| `/api/diagnostics/run-quick` | POST | Быстрая проверка критических компонентов |
| `/api/diagnostics/run-category` | POST | Проверка по категории |
| `/api/diagnostics/run-single` | POST | Запуск одной проверки |

### Исправления

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/diagnostics/fix` | POST | Применить исправление для проверки |
| `/api/diagnostics/fix-all` | POST | Применить все доступные исправления |

### Отчеты

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/diagnostics/health-report` | GET | Полный отчет о здоровье системы |
| `/api/diagnostics/health-summary` | GET | Краткая сводка |
| `/api/diagnostics/health-reports-history` | GET | История отчетов |

### Настройки

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/diagnostics/auto-mode` | POST | Вкл/выкл автоматического режима |
| `/api/diagnostics/auto-fix` | POST | Вкл/выкл автоисправления |
| `/api/diagnostics/check-interval` | POST | Установка интервала проверок |
| `/api/diagnostics/config` | GET/POST | Управление конфигурацией |

### История

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/diagnostics/history` | GET | История проверок |
| `/api/diagnostics/fixes-history` | GET | История исправлений |
| `/api/diagnostics/last-results` | GET | Последние результаты |

## Интерфейс пользователя

### Вкладки

1. **Overview** - Общий обзор с карточками проверок
2. **Results** - Детальные результаты с рекомендациями
3. **Categories** - Проверки по категориям
4. **History** - История проверок и исправлений
5. **Settings** - Настройки автоматического режима

### Функции UI

- Health Score с цветовой индикацией
- Статус по категориям с иконками
- Кнопки быстрых действий (Run All, Quick Check, Fix All)
- Переключатели Auto Mode и Auto-Fix
- Детальная информация по каждой проверке
- Рекомендации по устранению проблем
- История с фильтрацией

## Структура файлов

```
backend/
├── services/
│   └── diagnostics_service.py    # Основной сервис диагностики
├── app/api/
│   └── diagnostics_routes.py     # API endpoints
└── data/diagnostics/
    ├── diagnostics_history.json  # История проверок
    ├── fixes_history.json        # История исправлений
    └── config.json               # Конфигурация

frontend/
└── src/components/
    └── DiagnosticsPanel.tsx      # UI компонент
```

## Примеры использования

### Запуск полной диагностики

```bash
curl -X POST http://localhost:8000/api/diagnostics/run-all
```

### Быстрая проверка

```bash
curl -X POST http://localhost:8000/api/diagnostics/run-quick
```

### Проверка категории

```bash
curl -X POST http://localhost:8000/api/diagnostics/run-category \
  -H "Content-Type: application/json" \
  -d '{"category": "email"}'
```

### Применение исправления

```bash
curl -X POST http://localhost:8000/api/diagnostics/fix \
  -H "Content-Type: application/json" \
  -d '{"check_id": "data_directories"}'
```

### Получение отчета о здоровье

```bash
curl http://localhost:8000/api/diagnostics/health-report
```

## Автоматический режим

При включенном автоматическом режиме:
1. Проверки запускаются каждые N секунд (по умолчанию 300)
2. При обнаружении проблем генерируются уведомления
3. Если включен Auto-Fix, безопасные исправления применяются автоматически
4. История сохраняется для анализа трендов

## Расширение функционала

### Добавление новой проверки

```python
async def check_custom_service(self) -> DiagnosticResult:
    """Проверка кастомного сервиса"""
    try:
        # Логика проверки
        if service_ok:
            return DiagnosticResult(
                check_id="custom_service",
                category=DiagnosticCategory.SERVICES,
                name="Custom Service Check",
                status=DiagnosticStatus.OK,
                message="Service is running",
                severity=DiagnosticSeverity.HIGH,
                fix_available=False
            )
        else:
            return DiagnosticResult(
                check_id="custom_service",
                category=DiagnosticCategory.SERVICES,
                name="Custom Service Check",
                status=DiagnosticStatus.ERROR,
                message="Service is not responding",
                severity=DiagnosticSeverity.HIGH,
                fix_available=True,
                recommendations=["Restart the service", "Check logs"]
            )
    except Exception as e:
        return self._error_result("custom_service", str(e))
```

### Добавление нового исправления

```python
async def fix_custom_service(self) -> FixResult:
    """Исправление для кастомного сервиса"""
    before_result = await self.check_custom_service()
    
    try:
        # Логика исправления
        restart_service()
        
        after_result = await self.check_custom_service()
        
        return FixResult(
            check_id="custom_service",
            success=after_result.status == DiagnosticStatus.OK,
            message="Service restarted successfully",
            before_status=before_result.status,
            after_status=after_result.status,
            actions_taken=["Restarted custom service"]
        )
    except Exception as e:
        return FixResult(
            check_id="custom_service",
            success=False,
            message=f"Fix failed: {e}",
            before_status=before_result.status,
            after_status=before_result.status
        )
```

## Версия

- **Версия**: 2.0
- **Дата обновления**: 2026-01-27
- **Автор**: SEO Monster Team
