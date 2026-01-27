#!/bin/bash

# SEO Monster - One-Click Installer v2.0
# Installs and configures the entire application stack.

# --- Configuration ---
REPO_URL="https://github.com/burtyuo9/seo-monster.git"
INSTALL_DIR="seo-monster-app"

# --- Colors for output ---
C_RESET='\033[0m'
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;34m'

# --- Helper Functions ---
print_step() {
  echo -e "\n${C_BLUE}==> $1${C_RESET}"
}

print_success() {
  echo -e "${C_GREEN}✓ $1${C_RESET}"
}

print_warning() {
  echo -e "${C_YELLOW}⚠ $1${C_RESET}"
}

print_error() {
  echo -e "${C_RED}✗ $1${C_RESET}" >&2
  exit 1
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# --- Main Installation Logic ---

# 1. System Dependencies
print_step "1. Checking System Dependencies..."
sudo apt-get update -y
sudo apt-get install -y git curl python3 python3-pip python3-venv

if ! command_exists git; then print_error "Git is not installed. Please install it first."; fi
if ! command_exists python3; then print_error "Python 3 is not installed. Please install it first."; fi
print_success "System dependencies are met."

# 2. Node.js and pnpm Setup
print_step "2. Setting up Node.js and pnpm..."
if ! command_exists node; then
  print_warning "Node.js not found. Installing via NVM..."
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm install --lts
  print_success "Node.js installed."
else
  print_success "Node.js is already installed."
fi

if ! command_exists pnpm; then
  print_warning "pnpm not found. Installing..."
  npm install -g pnpm
  print_success "pnpm installed."
else
  print_success "pnpm is already installed."
fi

# 3. Clone Repository
print_step "3. Cloning SEO Monster from GitHub..."
if [ -d "$INSTALL_DIR" ]; then
  print_warning "Directory '$INSTALL_DIR' already exists. Skipping clone."
else
  git clone "$REPO_URL" "$INSTALL_DIR"
  print_success "Repository cloned into '$INSTALL_DIR'."
fi
cd "$INSTALL_DIR" || print_error "Could not change to directory '$INSTALL_DIR'."

# 4. Backend Setup
print_step "4. Setting up Python Backend..."
cd backend || print_error "Backend directory not found."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
# Create a default .env file if it doesn't exist
if [ ! -f ".env" ]; then
  echo "OPENAI_API_KEY='YOUR_OPENAI_API_KEY'" > .env
  echo "DATABASE_URL='sqlite:///./data/main.db'" >> .env
fi
print_success "Backend setup complete."
cd ..

# 5. Frontend Setup
print_step "5. Setting up Node.js Frontend..."
cd frontend || print_error "Frontend directory not found."
pnpm install
pnpm run build
print_success "Frontend setup complete."
cd ..

# --- Final Instructions ---
print_step "🎉 Installation Complete!"
echo -e "SEO Monster has been successfully installed in the '${C_YELLOW}${INSTALL_DIR}${C_RESET}' directory."
echo -e "Before you start, please edit the backend configuration file:"
echo -e "  ${C_GREEN}nano ${INSTALL_DIR}/backend/.env${C_RESET}"
echo -e "And add your OpenAI API key.\n"

echo -e "To start the application, run the following commands:"
echo -e "1. ${C_GREEN}cd ${INSTALL_DIR}${C_RESET}"
echo -e "2. Start Backend: ${C_GREEN}cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000${C_RESET}"
echo -e "3. In a new terminal, start Frontend: ${C_GREEN}cd frontend && pnpm preview --host 0.0.0.0 --port 5200${C_RESET}\n"
echo -e "Then open your browser to ${C_YELLOW}http://localhost:5200${C_RESET}"
