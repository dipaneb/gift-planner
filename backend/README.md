# Backend - FastAPI + PostgreSQL

This is the backend API for the Gift Planner application, built with FastAPI and PostgreSQL.

## 🏗️ Project Structure

```
backend/
├── docker/
│   ├── Dockerfile.dev           # Development Docker image
│   ├── Dockerfile.prod          # Production Docker image
│   ├── docker-compose.dev.yml   # Development environment config
│   └── docker-compose.prod.yml  # Production environment config
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   └── settings.py              # Environment settings management
├── requirements-dev.txt         # Development dependencies
├── requirements-prod.txt        # Production dependencies
├── .env                         # Environment variables
└── .env.example                 # Template for environment variables
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Make (optional, for using Makefile commands)

### Setup

1. **Copy environment file** (if not already done):

   ```bash
   cp .env.example .env
   ```

2. **Configure your environment variables** in `.env`

3. **Start the development environment**:
   ```bash
   # From the project root
   make dev-start
   ```

The API will be available at `http://localhost:8000`

## 📋 Available Commands

All commands should be run from the **project root** directory.

### Development Commands

```bash
make dev-start    # Start development environment
make dev-stop     # Stop development environment
make dev-logs     # View development logs
make dev-rebuild  # Rebuild and restart development environment
```

### Production Commands

```bash
make prod-start    # Start production environment
make prod-stop     # Stop production environment
make prod-logs     # View production logs
make prod-rebuild  # Rebuild and restart production environment
```

## 🔧 Development vs Production

### Development Environment

**Features:**

- ✅ Hot-reload enabled (code changes auto-restart server)
- ✅ Volume mounting (local `src/` folder synced with container)
- ✅ Development tools (pytest, black, ruff, ipython)
- ✅ Debug mode enabled
- ✅ Separate database (`app_dev`)

**Use for:**

- Daily development work
- Testing new features
- Debugging

### Production Environment

**Features:**

- ✅ Optimized for performance
- ✅ No hot-reload (stable, immutable)
- ✅ Minimal dependencies
- ✅ Debug mode disabled
- ✅ Separate database (`app_prod`)

**Use for:**

- Staging/production deployments
- Performance testing
- Final testing before release

## 📦 Dependencies

### Production Dependencies (`requirements-prod.txt`)

- FastAPI with all extras
- SQLAlchemy + PostgreSQL drivers (psycopg2, asyncpg)
- Pydantic Settings
- Alembic (migrations)
- Security libraries (pwdlib, pyjwt, cryptography)

### Development Dependencies (`requirements-dev.txt`)

- All production dependencies (via `-r requirements-prod.txt`)
- Testing tools (pytest, pytest-asyncio)
- Code quality (black, ruff)
- Development utilities (ipython, watchfiles)

## 🔐 Environment Variables

Key environment variables (see `.env.example` for full list):

- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `DATABASE_URL` - Full database connection URL
- `DEBUG` - Debug mode (True for dev, False for prod)
- `SECRET_KEY` - Secret key for JWT/encryption

**Important:** Never commit `.env` file to version control!

## 🗄️ Database

### Development Database

- Name: `app_dev`
- User: `dev_user`
- Volume: `docker_postgres_data_dev`

### Production Database

- Name: `app_prod`
- User: `prod_user`
- Volume: `docker_postgres_data_prod`

### Database Management with Adminer

**What is Adminer?**

Adminer is a lightweight, single-file database management tool (similar to phpMyAdmin but better). It's included in the development environment for easy database inspection and management.

**Key advantages over pgAdmin:**

- ✅ Extremely lightweight (~500KB vs pgAdmin's ~100MB+)
- ✅ Zero configuration required
- ✅ Simple, clean interface
- ✅ Supports multiple database systems (PostgreSQL, MySQL, SQLite, etc.)
- ✅ No separate login/account setup needed
- ✅ Faster startup and lower resource usage

**Accessing Adminer:**

1. Start the development environment: `make dev-start`
2. Open your browser to: `http://localhost:8080`
3. Login with your development database credentials:
   - **System:** PostgreSQL
   - **Server:** `db`
   - **Username:** `dev_user` (from `.env`)
   - **Password:** `dev_password_123` (from `.env`)
   - **Database:** `app_dev` (from `.env`)

**What you can do with Adminer:**

- Browse tables and data
- Run SQL queries
- Create/modify tables and schemas
- Import/export data
- View database structure
- Execute database operations

### Resetting the Database

To completely reset a database (⚠️ **destroys all data**):

```bash
# Development
docker compose -f backend/docker/docker-compose.dev.yml down -v
make dev-start

# Production
docker compose -f backend/docker/docker-compose.prod.yml down -v
make prod-start
```

## 🧪 Testing

Run tests in the development environment:

```bash
# Access the running container
docker exec -it docker-api-1 bash

# Run tests
pytest
```

## 📝 API Documentation

Once the server is running, access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Troubleshooting

### Containers won't start

```bash
# Check logs
make dev-logs  # or make prod-logs

# Rebuild from scratch
make dev-rebuild  # or make prod-rebuild
```

### Database connection errors

- Ensure environment variables are correctly set in `.env`
- Check that database credentials match between the env file and docker-compose file
- Try resetting the database (see "Resetting the Database" above)

### Port already in use

```bash
# Stop all containers
make dev-stop
make prod-stop

# Or check what's using the port
lsof -i :8000
lsof -i :5432
```
