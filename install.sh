#!/bin/bash
#
# SEO Monster - One-Click Installation Script
# Автоматическая установка SEO Monster
#
# Использование: ./install.sh [--docker]
#

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "  ____  _____ ___    __  __                 _            "
echo " / ___|| ____/ _ \\  |  \\/  | ___  _ __  ___| |_ ___ _ __ "
echo " \\___ \\|  _|| | | | | |\\/| |/ _ \\| '_ \\/ __| __/ _ \\ '__|"
echo "  ___) | |__| |_| | | |  | | (_) | | | \\__ \\ ||  __/ |   "
echo " |____/|_____|\\___/  |_|  |_|\\___/|_| |_|___/\\__\\___|_|   "
echo -e "${NC}"
echo "=============================================="
echo "       Автономный ИИ-агент для SEO"
echo "=============================================="
echo ""

USE_DOCKER=false
[[ "$1" == "--docker" ]] && USE_DOCKER=true

# Docker установка
if [ "$USE_DOCKER" = true ]; then
    echo -e "${YELLOW}🐳 Установка через Docker...${NC}"
    docker-compose up -d --build
    echo -e "${GREEN}✅ Запущено! http://localhost:5200${NC}"
    exit 0
fi

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не найден${NC}"
    exit 1
fi
echo -e "${GREEN}✅${NC} Python $(python3 --version)"

# Создание виртуального окружения
echo -e "${BLUE}📦 Создание виртуального окружения...${NC}"
[ ! -d "venv" ] && python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo -e "${BLUE}📦 Установка Python зависимостей...${NC}"
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
pip install playwright cryptography aiofiles -q

# Frontend
if command -v node &> /dev/null; then
    echo -e "${BLUE}📦 Установка frontend...${NC}"
    cd frontend && npm install -q && cd ..
fi

# Создание директорий
mkdir -p backend/data backend/services/data/{sessions,accounts,cookies} backend/knowledge logs backups

# .env
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# SEO Monster Configuration
OPENAI_API_KEY=your-api-key-here
DEBUG=false
DATABASE_URL=sqlite:///./data/seo_monster.db
EOF
    echo -e "${YELLOW}⚠️  Добавьте OpenAI API ключ в .env${NC}"
fi

# Скрипты запуска
cat > start.sh << 'STARTEOF'
#!/bin/bash
source venv/bin/activate
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
[ -d "../frontend/node_modules" ] && cd ../frontend && npm run dev &
echo "✅ SEO Monster: http://localhost:5200"
wait
STARTEOF
chmod +x start.sh

cat > stop.sh << 'STOPEOF'
#!/bin/bash
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null
echo "✅ Остановлено"
STOPEOF
chmod +x stop.sh

echo ""
echo -e "${GREEN}✅ Установка завершена!${NC}"
echo ""
echo "Запуск: ./start.sh"
echo "Остановка: ./stop.sh"
echo "Бэкап: python scripts/backup_manager.py backup"
echo "Миграция: python scripts/backup_manager.py migrate"
echo ""
