# 🎁 Gift Planner

A full-stack web application for organizing gifts, budgets, and Christmas lists with friends and family.


## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Development Workflow](#-development-workflow)
- [Available Commands](#-available-commands)
- [Contributing](#-contributing)
- [Additional Doc](#-additional-documentation)



## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy with Alembic migrations
- **Containerization**: Docker + Docker Compose
- **Database UI**: Adminer (development)
- **Authentication**: JWT tokens
- **Email**: Mailjet API
- **Code Quality**: Ruff + Black

### Frontend
- **Framework**: Vue 3 + TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **Validation**: Zod
- **Testing**: Vitest (unit) + Cypress (E2E)
- **Code Quality**: ESLint + Prettier

### Development Tools
- **Version Management**: Mise (Node.js & pnpm)
- **Task Runner**: Make (Makefiles for both frontend & backend)
- **Container Management**: Docker Desktop



## 📁 Project Structure

```
gift-planner/
├── backend/                    # FastAPI backend
│   ├── docker/                # Docker configuration files
│   │   ├── Dockerfile.dev     # Development image
│   │   ├── Dockerfile.prod    # Production image
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   ├── src/                   # Application source code
│   │   ├── config/           # Configuration modules
│   │   ├── core/             # Core functionality
│   │   ├── domains/          # Domain logic
│   │   └── main.py           # FastAPI entry point
│   ├── alembic/              # Database migrations
│   ├── .env.example          # Environment variables template
│   ├── Makefile              # Backend commands
│   └── requirements*.txt     # Python dependencies
│
├── frontend/                  # Vue.js frontend
│   ├── src/                  # Application source code
│   │   ├── api/             # API client
│   │   ├── assets/          # Static assets
│   │   ├── components/      # Vue components
│   │   ├── router/          # Vue Router config
│   │   ├── stores/          # Pinia stores
│   │   └── views/           # Page components
│   ├── cypress/             # E2E tests
│   ├── mise.toml            # Node/pnpm version control
│   ├── Makefile             # Frontend commands
│   └── package.json         # Dependencies
│
└── README.md                # This file
```



## ✅ Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop)
- **Make**: Pre-installed on macOS/Linux. For Windows, install via [Chocolatey](https://chocolatey.org/) for example.
- **Mise**: Install via `curl https://mise.run | sh` or [see docs](https://mise.jdx.dev/installing-mise.html)

### Optional but Recommended
- **Git**: For version control
- A code editor (VS Code, WebStorm, etc.)



## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd gift-planner
```

### Step 2: Backend Setup

#### 2.1 Configure Environment Variables

```bash
cd backend
cp .env.example .env.dev
```

Edit `backend/.env.dev` and configure the following **required** variables:

```env
# Database Configuration
POSTGRES_DB=gift_planner_dev
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password_123

# Database URL (must match above credentials)
DATABASE_URL=postgresql+psycopg://dev_user:dev_password_123@db:5432/gift_planner_dev

# Application Settings
ENV=development
DEBUG=True
ENABLE_DOCS=True
LOG_LEVEL=DEBUG

# Security (generate a strong random key for production)
SECRET_KEY=your-secret-key-change-this-in-production
REFRESH_TOKEN_TTL_DAYS=7
ACCESS_TOKEN_LIFESPAN_IN_MINUTES=15

# Email Configuration (optional for development)
MAILJET_API_KEY=your_mailjet_key
MAILJET_API_SECRET_KEY=your_mailjet_secret
MAIL_FROM_EMAIL=noreply@yourdomain.com
MAIL_FROM_NAME=Gift Planner
FRONTEND_BASE_URL=http://localhost:5173
```

#### 2.2 Start Backend Services

```bash
# From the backend/ directory
make start
```

This will:
- Build the Docker images (API + PostgreSQL + Adminer)
- Start all containers in detached mode
- Create the development database

**View logs** (optional):
```bash
make logs
```

Press `Ctrl+C` to exit logs (containers keep running).

**Verify backend is running**:
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Adminer (Database UI): http://localhost:8080

### Step 3: Frontend Setup

Open a **new terminal window** (keep backend running).

#### 3.1 Install Mise and Dependencies

```bash
cd frontend

# Mise will automatically install Node 24 and pnpm 10
# based on mise.toml when you first run a command
mise install

# Install frontend dependencies
make install
```

#### 3.2 Configure Frontend Environment

```bash
# Copy and edit .env file
cp .env.example .env.development # name is important, see https://vite.dev/guide/env-and-mode
```

#### 3.3 Start Frontend Dev Server

```bash
make dev
```

The frontend will be available at: **http://localhost:5173**



## 💻 Development Workflow

### Recommended Terminal Setup

For efficient development, keep **3 terminal windows** open:

#### Terminal 1: Backend
```bash
cd backend
make start    # Start containers
make logs     # Watch logs (optional)
```

#### Terminal 2: Frontend
```bash
cd frontend
make dev      # Start Vite dev server
```

#### Terminal 3: Git Operations
```bash
cd gift-planner  # Project root
git status
git add .
git commit -m "Your commit message"
git push
```

### Hot Reload

- **Backend**: Code changes in `backend/src/` automatically restart the FastAPI server
- **Frontend**: Code changes trigger instant hot-reload in the browser



## 📚 Available Commands

### Backend Commands

Run from `backend/` directory:

```bash
make help              # Show all available commands

# Development
make start             # Start development environment
make stop              # Stop development environment  
make logs              # View real-time logs
make rebuild           # Rebuild containers from scratch

# Production
make prod-start        # Start production environment
make prod-stop         # Stop production environment
make prod-logs         # View production logs
make prod-rebuild      # Rebuild production containers

# Database Migrations
make alembic-rev m="migration message"  # Create new migration
make alembic-up        # Apply migrations
make alembic-down      # Rollback last migration
make alembic-history   # View migration history

# Testing
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-e2e          # Run E2E tests only

# Code Quality
make format            # Format code with Black
make lint              # Lint with Ruff
make lint-fix          # Auto-fix linting issues
make check             # Run all quality checks

# Container Management
make shell             # Access container shell
```

### Frontend Commands

Run from `frontend/` directory:

```bash
make help              # Show all available commands

# Setup
make install           # Install dependencies

# Development
make dev               # Start dev server (http://localhost:5173)
make build             # Build for production

# Testing
make test-unit         # Run Vitest unit tests
make test-e2e-dev      # Run Cypress E2E (dev server)
make test-e2e          # Run Cypress E2E (production build)

# Code Quality
make lint              # Lint with ESLint
```



## 🤝 Contributing

### Git Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Quality Checks

**Before committing**, run:

```bash
# Backend
cd backend
make check             # Format check + lint

# Frontend  
cd frontend
make lint              # ESLint check
```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build/tooling changes




## 📖 Additional Documentation

- **Backend Details**: See `backend/README.md`
- **API Documentation**: http://localhost:8000/docs (when running)
- **Database Management**: http://localhost:8080 (Adminer)