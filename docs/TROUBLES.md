# SEO Monster - Troubleshooting Guide

## Известные проблемы и решения

### 1. PowerShell UTF-8 Encoding Issues

**Симптомы:** Скрипты с кириллицей или emoji не выполняются на Windows

**Причина:** PowerShell по умолчанию использует Windows-1251, а не UTF-8

**Решение:**
```powershell
# Установить UTF-8 кодировку
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Или использовать ASCII версии скриптов без спецсимволов
```

### 2. Frontend не подключается к Backend

**Симптомы:** "API Disconnected" в UI, ошибки CORS

**Причина:** Frontend настроен на localhost вместо IP сервера

**Решение:**
1. Найти все файлы с `localhost:8000`:
```bash
grep -r "localhost:8000" frontend/src/
```
2. Заменить на IP сервера:
```bash
sed -i 's/localhost:8000/YOUR_SERVER_IP:8000/g' frontend/src/**/*.tsx
```
3. Пересобрать frontend:
```bash
cd frontend && pnpm run build
```

### 3. AWS SES Key не добавляется

**Симптомы:** Кнопка Save не реагирует, нет сообщений об ошибках

**Причина:** Отсутствует обработка ошибок в frontend

**Решение:** Обновить SESManager.tsx с обработкой ошибок (см. коммит от 2026-01-28)

### 4. MANUS.space публикация не работает

**Симптомы:** Error 1016 - Origin DNS error

**Причина:** MANUS.space поддомены требуют внутренний Manus API

**Решение:** 
- Использовать Scheduled Task в Manus для публикации
- Или использовать альтернативные хостинги (Netlify, Vercel)

### 5. Backend не запускается на Windows

**Симптомы:** UnicodeDecodeError при запуске

**Причина:** Emoji символы в Python файлах

**Решение:**
1. Удалить emoji из main.py и других файлов
2. Или добавить в начало файла:
```python
# -*- coding: utf-8 -*-
```

### 6. Порты заблокированы на VPS

**Симптомы:** Сайт недоступен извне

**Решение:**
```powershell
# Открыть порты в Windows Firewall
New-NetFirewallRule -DisplayName "SEO Monster Backend" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "SEO Monster Frontend" -Direction Inbound -Port 5200 -Protocol TCP -Action Allow
```

---

## Контакты для поддержки

- GitHub Issues: https://github.com/burtyuo9/seo-monster/issues
- Telegram: @seo_monster_support

---
*Last updated: 2026-01-28*
