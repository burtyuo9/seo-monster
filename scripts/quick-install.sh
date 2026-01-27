#!/bin/bash
# SEO Monster - Quick Installation Script
# Auto-detects OS and runs appropriate installer

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "  ____  _____ ___    __  __                 _            "
echo " / ___|| ____/ _ \  |  \/  | ___  _ __  ___| |_ ___ _ __ "
echo " \___ \|  _|| | | | | |\/| |/ _ \| '_ \/ __| __/ _ \ '__|"
echo "  ___) | |__| |_| | | |  | | (_) | | | \__ \ ||  __/ |   "
echo " |____/|_____\___/  |_|  |_|\___/|_| |_|___/\__\___|_|   "
echo ""
echo -e "${NC}"
echo "Quick Installation Script"
echo "========================="
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}Cannot detect OS${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS${NC}"
echo ""

# Download and run appropriate script
REPO_URL="https://raw.githubusercontent.com/burtyuo9/seo-monster/master/scripts"

case $OS in
    ubuntu|debian|linuxmint|pop)
        echo "Using Ubuntu/Debian installer..."
        curl -fsSL "$REPO_URL/install-ubuntu.sh" | bash
        ;;
    centos|rhel|rocky|almalinux|fedora)
        echo "Using CentOS/RHEL installer..."
        curl -fsSL "$REPO_URL/install-centos.sh" | bash
        ;;
    *)
        echo -e "${YELLOW}Your OS ($OS) is not directly supported.${NC}"
        echo ""
        echo "Options:"
        echo "  1. Use Docker installation (recommended)"
        echo "  2. Manual installation"
        echo ""
        read -p "Choose option (1/2): " choice
        
        if [ "$choice" = "1" ]; then
            echo "Installing with Docker..."
            
            # Check if Docker is installed
            if ! command -v docker &> /dev/null; then
                echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
                echo "Visit: https://docs.docker.com/get-docker/"
                exit 1
            fi
            
            # Clone and run with Docker
            git clone https://github.com/burtyuo9/seo-monster.git ~/seo_monster
            cd ~/seo_monster
            cp .env.example .env
            docker compose up -d
            
            echo -e "${GREEN}SEO Monster is running!${NC}"
            echo "Frontend: http://localhost:80"
            echo "Backend: http://localhost:8000"
        else
            echo ""
            echo "Manual installation instructions:"
            echo "1. Install Python 3.11+"
            echo "2. Install Node.js 20+"
            echo "3. Clone: git clone https://github.com/burtyuo9/seo-monster.git"
            echo "4. Backend: cd backend && pip install -r requirements.txt"
            echo "5. Frontend: cd frontend && npm install && npm run build"
            echo "6. Run: uvicorn main:app --port 8000"
        fi
        ;;
esac
