#!/bin/bash
# SEO Monster - Installation Script for CentOS/RHEL/Rocky/Alma
# Supports: CentOS Stream 8/9, Rocky Linux 8/9, AlmaLinux 8/9, RHEL 8/9

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_msg "⚠️  Please do not run as root. Use a regular user with sudo privileges." "$YELLOW"
        exit 1
    fi
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
        VERSION_MAJOR=$(echo $VERSION_ID | cut -d'.' -f1)
    else
        print_msg "❌ Cannot detect OS." "$RED"
        exit 1
    fi
    
    print_msg "✓ Detected: $OS $VERSION" "$GREEN"
}

update_system() {
    print_header "Updating System"
    sudo dnf update -y
    print_msg "✓ System updated" "$GREEN"
}

install_dependencies() {
    print_header "Installing Dependencies"
    
    # Enable EPEL repository
    sudo dnf install -y epel-release
    
    # Essential packages
    sudo dnf install -y \
        curl \
        wget \
        git \
        gcc \
        gcc-c++ \
        make \
        openssl-devel \
        bzip2-devel \
        libffi-devel \
        zlib-devel
    
    print_msg "✓ Essential packages installed" "$GREEN"
}

install_python() {
    print_header "Installing Python 3.11"
    
    if command -v python3.11 &> /dev/null; then
        print_msg "✓ Python 3.11 already installed" "$GREEN"
        return
    fi
    
    # Install Python 3.11 from source or AppStream
    if [ "$VERSION_MAJOR" -ge 9 ]; then
        sudo dnf install -y python3.11 python3.11-devel python3.11-pip
    else
        # For CentOS/RHEL 8, build from source
        cd /tmp
        wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
        tar xzf Python-3.11.7.tgz
        cd Python-3.11.7
        ./configure --enable-optimizations --prefix=/usr/local
        make -j$(nproc)
        sudo make altinstall
        cd ~
        rm -rf /tmp/Python-3.11.7*
    fi
    
    print_msg "✓ Python 3.11 installed" "$GREEN"
}

install_nodejs() {
    print_header "Installing Node.js 20"
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -ge 20 ]; then
            print_msg "✓ Node.js $NODE_VERSION already installed" "$GREEN"
            return
        fi
    fi
    
    # Install Node.js via NodeSource
    curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
    sudo dnf install -y nodejs
    
    # Install pnpm
    sudo npm install -g pnpm
    
    print_msg "✓ Node.js 20 and pnpm installed" "$GREEN"
}

install_docker() {
    print_header "Installing Docker (Optional)"
    
    read -p "Do you want to install Docker? (y/n): " install_docker_choice
    if [ "$install_docker_choice" != "y" ]; then
        print_msg "⏭️  Skipping Docker installation" "$YELLOW"
        return
    fi
    
    if command -v docker &> /dev/null; then
        print_msg "✓ Docker already installed" "$GREEN"
        return
    fi
    
    # Install Docker
    sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    
    print_msg "✓ Docker installed" "$GREEN"
}

clone_repository() {
    print_header "Cloning SEO Monster Repository"
    
    INSTALL_DIR="${HOME}/seo_monster"
    
    if [ -d "$INSTALL_DIR" ]; then
        print_msg "⚠️  Directory $INSTALL_DIR already exists" "$YELLOW"
        read -p "Remove and clone fresh? (y/n): " remove_choice
        if [ "$remove_choice" = "y" ]; then
            rm -rf "$INSTALL_DIR"
        else
            return
        fi
    fi
    
    git clone https://github.com/burtyuo9/seo-monster.git "$INSTALL_DIR"
    
    print_msg "✓ Repository cloned" "$GREEN"
}

install_backend() {
    print_header "Installing Backend Dependencies"
    
    cd "${HOME}/seo_monster/backend"
    
    python3.11 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    print_msg "✓ Backend dependencies installed" "$GREEN"
}

install_frontend() {
    print_header "Installing Frontend Dependencies"
    
    cd "${HOME}/seo_monster/frontend"
    pnpm install
    
    print_msg "✓ Frontend dependencies installed" "$GREEN"
}

build_frontend() {
    print_header "Building Frontend"
    
    cd "${HOME}/seo_monster/frontend"
    pnpm run build
    sudo npm install -g serve
    
    print_msg "✓ Frontend built" "$GREEN"
}

create_services() {
    print_header "Creating Systemd Services"
    
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

[Install]
WantedBy=multi-user.target
EOF

    sudo tee /etc/systemd/system/seo-monster-frontend.service > /dev/null <<EOF
[Unit]
Description=SEO Monster Frontend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=${HOME}/seo_monster/frontend
ExecStart=/usr/bin/npx serve -s dist -l 3000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    
    # Configure firewall
    sudo firewall-cmd --permanent --add-port=3000/tcp
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
    
    print_msg "✓ Services created and firewall configured" "$GREEN"
}

setup_environment() {
    print_header "Setting Up Environment"
    
    cd "${HOME}/seo_monster"
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_msg "✓ Created .env file" "$GREEN"
    fi
}

print_instructions() {
    print_header "Installation Complete! 🎉"
    
    echo -e "${GREEN}SEO Monster installed successfully!${NC}"
    echo ""
    echo "Access URLs:"
    echo "  • Frontend: http://localhost:3000"
    echo "  • Backend: http://localhost:8000"
    echo ""
    echo "Commands:"
    echo "  • Start: sudo systemctl start seo-monster-backend seo-monster-frontend"
    echo "  • Stop: sudo systemctl stop seo-monster-backend seo-monster-frontend"
    echo ""
}

main() {
    print_header "SEO Monster Installation (CentOS/RHEL)"
    
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
    print_instructions
}

main "$@"
