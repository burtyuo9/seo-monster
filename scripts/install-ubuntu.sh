#!/bin/bash
# SEO Monster - Installation Script for Ubuntu/Debian
# Supports: Ubuntu 20.04, 22.04, 24.04 | Debian 11, 12

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_msg "⚠️  Please do not run as root. Use a regular user with sudo privileges." "$YELLOW"
        exit 1
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        print_msg "❌ Cannot detect OS. This script supports Ubuntu/Debian only." "$RED"
        exit 1
    fi
    
    print_msg "✓ Detected: $OS $VERSION" "$GREEN"
}

# Update system
update_system() {
    print_header "Updating System"
    sudo apt-get update -y
    sudo apt-get upgrade -y
    print_msg "✓ System updated" "$GREEN"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    # Essential packages
    sudo apt-get install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    print_msg "✓ Essential packages installed" "$GREEN"
}

# Install Python 3.11
install_python() {
    print_header "Installing Python 3.11"
    
    # Check if Python 3.11 is already installed
    if command -v python3.11 &> /dev/null; then
        print_msg "✓ Python 3.11 already installed" "$GREEN"
        return
    fi
    
    # Add deadsnakes PPA for Ubuntu
    if [ "$OS" = "ubuntu" ]; then
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update
    fi
    
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
    
    # Set Python 3.11 as default python3
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    
    print_msg "✓ Python 3.11 installed" "$GREEN"
}

# Install Node.js 20
install_nodejs() {
    print_header "Installing Node.js 20"
    
    # Check if Node.js 20 is already installed
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -ge 20 ]; then
            print_msg "✓ Node.js $NODE_VERSION already installed" "$GREEN"
            return
        fi
    fi
    
    # Install Node.js via NodeSource
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    # Install pnpm
    sudo npm install -g pnpm
    
    print_msg "✓ Node.js 20 and pnpm installed" "$GREEN"
}

# Install Docker (optional)
install_docker() {
    print_header "Installing Docker (Optional)"
    
    read -p "Do you want to install Docker? (y/n): " install_docker_choice
    if [ "$install_docker_choice" != "y" ]; then
        print_msg "⏭️  Skipping Docker installation" "$YELLOW"
        return
    fi
    
    # Check if Docker is already installed
    if command -v docker &> /dev/null; then
        print_msg "✓ Docker already installed" "$GREEN"
        return
    fi
    
    # Install Docker
    curl -fsSL https://get.docker.com | sudo sh
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Install Docker Compose
    sudo apt-get install -y docker-compose-plugin
    
    print_msg "✓ Docker installed. Please log out and back in to use Docker without sudo." "$GREEN"
}

# Clone repository
clone_repository() {
    print_header "Cloning SEO Monster Repository"
    
    INSTALL_DIR="${HOME}/seo_monster"
    
    if [ -d "$INSTALL_DIR" ]; then
        print_msg "⚠️  Directory $INSTALL_DIR already exists" "$YELLOW"
        read -p "Do you want to remove it and clone fresh? (y/n): " remove_choice
        if [ "$remove_choice" = "y" ]; then
            rm -rf "$INSTALL_DIR"
        else
            print_msg "⏭️  Using existing directory" "$YELLOW"
            return
        fi
    fi
    
    git clone https://github.com/burtyuo9/seo-monster.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    print_msg "✓ Repository cloned to $INSTALL_DIR" "$GREEN"
}

# Install backend dependencies
install_backend() {
    print_header "Installing Backend Dependencies"
    
    cd "${HOME}/seo_monster/backend"
    
    # Create virtual environment
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    deactivate
    
    print_msg "✓ Backend dependencies installed" "$GREEN"
}

# Install frontend dependencies
install_frontend() {
    print_header "Installing Frontend Dependencies"
    
    cd "${HOME}/seo_monster/frontend"
    
    pnpm install
    
    print_msg "✓ Frontend dependencies installed" "$GREEN"
}

# Create systemd services
create_services() {
    print_header "Creating Systemd Services"
    
    # Backend service
    sudo tee /etc/systemd/system/seo-monster-backend.service > /dev/null <<EOF
[Unit]
Description=SEO Monster Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=${HOME}/seo_monster/backend
Environment="PATH=${HOME}/seo_monster/backend/venv/bin"
ExecStart=${HOME}/seo_monster/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Frontend service (production build with serve)
    sudo tee /etc/systemd/system/seo-monster-frontend.service > /dev/null <<EOF
[Unit]
Description=SEO Monster Frontend
After=network.target seo-monster-backend.service

[Service]
Type=simple
User=$USER
WorkingDirectory=${HOME}/seo_monster/frontend
ExecStart=/usr/bin/npx serve -s dist -l 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    
    print_msg "✓ Systemd services created" "$GREEN"
}

# Build frontend for production
build_frontend() {
    print_header "Building Frontend for Production"
    
    cd "${HOME}/seo_monster/frontend"
    pnpm run build
    
    # Install serve globally
    sudo npm install -g serve
    
    print_msg "✓ Frontend built for production" "$GREEN"
}

# Setup environment
setup_environment() {
    print_header "Setting Up Environment"
    
    cd "${HOME}/seo_monster"
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_msg "✓ Created .env file from template" "$GREEN"
        print_msg "⚠️  Please edit .env file to add your API keys" "$YELLOW"
    else
        print_msg "✓ .env file already exists" "$GREEN"
    fi
}

# Start services
start_services() {
    print_header "Starting Services"
    
    read -p "Do you want to start SEO Monster now? (y/n): " start_choice
    if [ "$start_choice" != "y" ]; then
        print_msg "⏭️  Skipping service start" "$YELLOW"
        return
    fi
    
    sudo systemctl enable seo-monster-backend
    sudo systemctl enable seo-monster-frontend
    sudo systemctl start seo-monster-backend
    sudo systemctl start seo-monster-frontend
    
    print_msg "✓ Services started" "$GREEN"
}

# Print final instructions
print_instructions() {
    print_header "Installation Complete! 🎉"
    
    echo -e "${GREEN}SEO Monster has been installed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Access URLs:${NC}"
    echo "  • Frontend: http://localhost:3000"
    echo "  • Backend API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  • Start services:   sudo systemctl start seo-monster-backend seo-monster-frontend"
    echo "  • Stop services:    sudo systemctl stop seo-monster-backend seo-monster-frontend"
    echo "  • View logs:        sudo journalctl -u seo-monster-backend -f"
    echo "  • Check status:     sudo systemctl status seo-monster-backend"
    echo ""
    echo -e "${BLUE}Configuration:${NC}"
    echo "  • Edit ${HOME}/seo_monster/.env to configure API keys"
    echo ""
    echo -e "${YELLOW}⚠️  Don't forget to configure your API keys in .env file!${NC}"
}

# Main installation flow
main() {
    print_header "SEO Monster Installation Script"
    print_msg "This script will install SEO Monster on your system" "$BLUE"
    echo ""
    
    check_root
    detect_os
    update_system
    install_dependencies
    install_python
    install_nodejs
    install_docker
    clone_repository
    install_backend
    install_frontend
    build_frontend
    setup_environment
    create_services
    start_services
    print_instructions
}

# Run main function
main "$@"
