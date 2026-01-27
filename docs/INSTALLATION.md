# SEO Monster - Installation Guide

**Author:** Manus AI
**Version:** 1.0.0
**Last Updated:** 2026-01-27

## Introduction

This guide provides comprehensive instructions for installing SEO Monster on various operating systems. Choose the method that best suits your environment.

## 1. Quick Installation (Recommended)

This method uses a single command to auto-detect your OS and install SEO Monster. It is the fastest and easiest way to get started.

**Supported OS:** Ubuntu, Debian, CentOS, RHEL, Rocky Linux, AlmaLinux, Fedora

```bash
curl -fsSL https://raw.githubusercontent.com/burtyuo9/seo-monster/master/scripts/quick-install.sh | bash
```

## 2. Docker Installation (Universal)

This is the most reliable and recommended method for all operating systems, as it provides a consistent and isolated environment.

### Prerequisites

- **Docker:** [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose:** (Included with Docker Desktop)
- **Git:** [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Steps

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/burtyuo9/seo-monster.git
    cd seo-monster
    ```

2.  **Create `.env` file:**

    Copy the example file and add your API keys.

    ```bash
    cp .env.example .env
    nano .env
    ```

3.  **Run with Docker Compose:**

    This command will build the images and start all services.

    ```bash
    docker compose up -d
    ```

4.  **Access SEO Monster:**

    -   **Frontend:** `http://localhost`
    -   **Backend API:** `http://localhost:8000`

### Docker Compose Profiles

-   **Default:** Runs only the core `backend` and `frontend` services.
-   **Full:** Runs all services, including `redis` and `postgres`.

    ```bash
    # Run with all optional services
    docker compose --profile full up -d
    ```

## 3. Manual Installation

This method is for advanced users or unsupported operating systems.

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 Cores | 4+ Cores |
| **RAM** | 4 GB | 8+ GB |
| **Disk** | 20 GB SSD | 50+ GB SSD |
| **Python** | 3.10+ | 3.11+ |
| **Node.js** | 18+ | 20+ |

### Installation Steps

#### A. Ubuntu / Debian

1.  **Update system:**

    ```bash
    sudo apt-get update && sudo apt-get upgrade -y
    ```

2.  **Install dependencies:**

    ```bash
    sudo apt-get install -y python3.11 nodejs npm git
    ```

3.  **Clone repository:**

    ```bash
    git clone https://github.com/burtyuo9/seo-monster.git
    cd seo-monster
    ```

4.  **Install backend dependencies:**

    ```bash
    cd backend
    pip3 install -r requirements.txt
    cd ..
    ```

5.  **Install frontend dependencies:**

    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

6.  **Run the application:**

    ```bash
    # Terminal 1: Backend
    cd backend
    uvicorn main:app --host 0.0.0.0 --port 8000

    # Terminal 2: Frontend
    cd frontend
    npm run dev -- --port 3000
    ```

#### B. CentOS / RHEL

1.  **Update system:**

    ```bash
    sudo dnf update -y
    ```

2.  **Install dependencies:**

    ```bash
    sudo dnf install -y python3.11 nodejs npm git
    ```

3.  Follow steps 3-6 from the Ubuntu/Debian section.

#### C. macOS

1.  **Install Homebrew:**

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2.  **Install dependencies:**

    ```bash
    brew install python@3.11 node@20 git
    ```

3.  Follow steps 3-6 from the Ubuntu/Debian section.

#### D. Windows (with WSL2)

1.  **Install WSL2:**

    Follow the official [Microsoft guide](https://docs.microsoft.com/en-us/windows/wsl/install).

2.  **Install Ubuntu from Microsoft Store:**

    Open the Microsoft Store and search for "Ubuntu".

3.  **Open Ubuntu terminal:**

    Launch the installed Ubuntu application.

4.  **Follow Ubuntu/Debian instructions:**

    Inside the WSL2 Ubuntu terminal, follow the manual installation steps for Ubuntu.

## 4. Configuration

SEO Monster is configured via environment variables. Create a `.env` file in the root directory by copying `.env.example`.

| Variable | Description | Default |
|-----------------------|-------------------------------------------|-----------------------------------|
| `BACKEND_PORT` | Port for the backend API | `8000` |
| `FRONTEND_PORT` | Port for the frontend UI | `80` (Docker) / `3000` (Manual) |
| `OPENAI_API_KEY` | Your OpenAI API key | `null` |
| `AWS_ACCESS_KEY_ID` | Your AWS access key | `null` |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | `null` |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | `null` |
| `DATABASE_URL` | Database connection string | `sqlite:///./data/seo_monster.db` |
| `SECRET_KEY` | Secret key for JWT tokens | `change-this...` |

## 5. Troubleshooting

-   **Port conflicts:** Change `BACKEND_PORT` or `FRONTEND_PORT` in your `.env` file.
-   **Dependency issues:** Ensure you are using the correct versions of Python and Node.js.
-   **Docker issues:** Run `docker compose logs -f` to view logs for all services.

---

For further assistance, please open an issue on the [GitHub repository](https://github.com/burtyuo9/seo-monster/issues).
