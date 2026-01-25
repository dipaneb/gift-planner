# Declare phony targets (targets that don't represent actual files)
.PHONY: help start stop logs rebuild prod-start prod-stop prod-logs prod-rebuild alembic-init alembic-rev alembic-up alembic-down alembic-history alembic-current alembic-prod-up alembic-prod-current alembic-prod-history shell test test-unit test-integration test-e2e test-path format lint lint-fix check

# ============================================================================
# HELP COMMAND
# ============================================================================

help:
	@echo ""
	@echo "================================================================================"
	@echo "🚀 Gift Planner - Available Commands"
	@echo "================================================================================"
	@echo ""
	@echo "📦 DEVELOPMENT:"
	@echo "   start                Start development environment with hot-reload"
	@echo "   stop                 Stop development environment"
	@echo "   logs                 View development logs in real-time"
	@echo "   rebuild              Rebuild and restart development environment"
	@echo ""
	@echo ""
	@echo "🏭 PRODUCTION:"
	@echo "   prod-start           Start production environment"
	@echo "   prod-stop            Stop production environment"
	@echo "   prod-logs            View production logs in real-time"
	@echo "   prod-rebuild         Rebuild and restart production environment"
	@echo ""
	@echo ""
	@echo "🗄️ DATABASE MIGRATIONS (DEV):"
	@echo "   alembic-init         Initialize Alembic for database migrations"
	@echo "   alembic-rev          Create new migration (use: make alembic-rev m='message')"
	@echo "   alembic-up           Apply all pending migrations"
	@echo "   alembic-down         Rollback last migration"
	@echo "   alembic-history      Show migration history"
	@echo "   alembic-current      Show current migration"
	@echo ""
	@echo ""
	@echo "🗄️ DATABASE MIGRATIONS (PROD):"
	@echo "   alembic-prod-up      Apply all pending migrations"
	@echo "   alembic-prod-current Show current migration"
	@echo "   alembic-prod-history Show migration history"
	@echo ""
	@echo ""
	@echo "🐳 CONTAINER MANAGEMENT:"
	@echo "   shell                Access container shell for debugging"
	@echo ""
	@echo ""
	@echo "🧪 TESTING:"
	@echo "   test                 Run all tests (uses -v by default)"
	@echo "   test-unit            Run only unit tests"
	@echo "   test-integration     Run only integration tests"
	@echo "   test-e2e             Run only end-to-end tests"
	@echo "   test-path            Run tests in specific path (use: make test-path path=tests/unit)"
	@echo ""
	@echo "   📝 Testing args examples:"
	@echo "      make test args='-k test_register'  # Run specific tests"
	@echo "      make test args='-x -s'             # Stop on first failure, show prints"
	@echo "      make test args='-vv'               # Extra verbose"
	@echo "      make test args='-q'                # Quiet mode"
	@echo ""
	@echo ""
	@echo "🎨 CODE QUALITY:"
	@echo "   format               Format code using black"
	@echo "   lint                 Lint code using ruff"
	@echo "   lint-fix             Lint code using ruff --fix flag"
	@echo "   check                Run all code quality checks"
	@echo ""
	@echo ""
	@echo ""
	@echo "💡 Tip: Use 'make help' to see this menu again"
	@echo ""

# ============================================================================
# DEVELOPMENT COMMANDS
# ============================================================================

# Start development environment with hot-reload enabled
# Code changes in src/ will automatically restart the server
# Uses docker-compose.dev.yml and Dockerfile.dev
start:
	docker compose -f backend/docker/docker-compose.dev.yml up -d

# Stop development environment
# Shuts down containers but preserves the development database volume
stop:
	docker compose -f backend/docker/docker-compose.dev.yml down

# View development logs in real-time
# Press Ctrl+C to exit (containers keep running)
logs:
	docker compose -f backend/docker/docker-compose.dev.yml logs -f

# Rebuild and restart development environment
# Use after changing requirements.txt or Dockerfile.dev
rebuild:
	docker compose -f backend/docker/docker-compose.dev.yml up -d --build


# ============================================================================
# PRODUCTION COMMANDS
# ============================================================================

# Start production environment
# Optimized for performance, no hot-reload
# Uses docker-compose.prod.yml and Dockerfile.prod
prod-start:
	docker compose -f backend/docker/docker-compose.prod.yml up -d

# Stop production environment
# Shuts down containers but preserves the production database volume
prod-stop:
	docker compose -f backend/docker/docker-compose.prod.yml down

# View production logs in real-time
# Press Ctrl+C to exit (containers keep running)
prod-logs:
	docker compose -f backend/docker/docker-compose.prod.yml logs -f

# Rebuild and restart production environment
# Use after changing requirements.txt or Dockerfile.prod
prod-rebuild:
	docker compose -f backend/docker/docker-compose.prod.yml up -d --build


# ============================================================================
# ALEMBIC (DATABASE MIGRATIONS)
# ============================================================================

alembic-init:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic init alembic

alembic-rev:
	if [ -z "$(m)" ]; then \
		echo "Erreur: le message '-m' est manquant. Utilisez: make alembic-rev m=\"votre message\""; \
		exit 1; \
	fi
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic revision --autogenerate -m "$(m)"

alembic-up:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic upgrade head

alembic-down:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic downgrade -1

alembic-history:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic history

alembic-current:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic current


# ============================================================================
# ALEMBIC - PRODUCTION (read-only migrations)
# ============================================================================

alembic-prod-up:
	docker compose -f backend/docker/docker-compose.yml exec api alembic upgrade head

alembic-prod-current:
	docker compose -f backend/docker/docker-compose.yml exec api alembic current

alembic-prod-history:
	docker compose -f backend/docker/docker-compose.yml exec api alembic history


# ============================================================================
# CONTAINER MANAGEMENT
# ============================================================================

# Access the container shell for debugging or manual commands
# Opens an interactive bash terminal inside the development container
# Use 'exit' to leave the container shell
shell:
	docker exec -it docker-api-1 bash


# ============================================================================
# TESTING & CODE QUALITY COMMANDS
# ============================================================================

# Run all tests with verbose output
# Executes all tests in the tests/ directory
# Make sure dev environment is running (make start) before running tests
test:
	@if [ "$(args)" = "-v" ]; then \
		echo "Note: command already uses -v by default"; \
		docker exec -it docker-api-1 pytest tests/ -v; \
	elif [ "$(args)" = "-vv" ] || [ "$(args)" = "-q" ]; then \
		docker exec -it docker-api-1 pytest tests/ $(args); \
	else \
		docker exec -it docker-api-1 pytest tests/ -v $(args); \
	fi

# Run only unit tests
# Executes all tests in tests/unit/ directory
# Unit tests are fast and test individual components in isolation
test-unit:
	@if [ "$(args)" = "-v" ]; then \
		echo "Note: command already uses -v by default"; \
		docker exec -it docker-api-1 pytest tests/unit/ -v; \
	elif [ "$(args)" = "-vv" ] || [ "$(args)" = "-q" ]; then \
		docker exec -it docker-api-1 pytest tests/unit/ $(args); \
	else \
		docker exec -it docker-api-1 pytest tests/unit/ -v $(args); \
	fi

# Run only integration tests
# Executes all tests in tests/integration/ directory
# Integration tests verify that components work together correctly
test-integration:
	@if [ "$(args)" = "-v" ]; then \
		echo "Note: command already uses -v by default"; \
		docker exec -it docker-api-1 pytest tests/integration/ -v; \
	elif [ "$(args)" = "-vv" ] || [ "$(args)" = "-q" ]; then \
		docker exec -it docker-api-1 pytest tests/integration/ $(args); \
	else \
		docker exec -it docker-api-1 pytest tests/integration/ -v $(args); \
	fi

# Run only end-to-end tests
# Executes all tests in tests/e2e/ directory
# E2E tests verify complete user workflows from start to finish
test-e2e:
	@if [ "$(args)" = "-v" ]; then \
		echo "Note: command already uses -v by default"; \
		docker exec -it docker-api-1 pytest tests/e2e/ -v; \
	elif [ "$(args)" = "-vv" ] || [ "$(args)" = "-q" ]; then \
		docker exec -it docker-api-1 pytest tests/e2e/ $(args); \
	else \
		docker exec -it docker-api-1 pytest tests/e2e/ -v $(args); \
	fi

# Run tests in a specific path with optional parameters
# Usage examples:
#   make test-path path=tests/unit/domains/auth
#   make test-path path=tests/integration/api args="-k test_register"
#   make test-path path=tests/unit args="-x -s"
# Common pytest args:
#   -v          verbose output
#   -s          show print statements
#   -x          stop on first failure
#   -k PATTERN  run tests matching pattern
#   --tb=short  shorter traceback format
test-path:
	@if [ -z "$(path)" ]; then \
		echo "Error: 'path' parameter is required. Usage: make test-path path=tests/unit/domains/auth"; \
		echo "Optional: Add pytest arguments with args=\"-x -s\""; \
		exit 1; \
	fi
	docker exec -it docker-api-1 pytest $(path) -v $(args)

# Format code using black
# Automatically formats all Python files according to black's style guide
# Changes are applied directly to your local files via volume mounting
format:
	docker exec -it docker-api-1 black src/

# Lint code using ruff
# Checks for code quality issues, potential bugs, and style violations
# Does not modify files, only reports issues
lint:
	docker exec -it docker-api-1 ruff check src/

lint-fix:
	docker exec -it docker-api-1 ruff check src/ --fix

# Run all code quality checks (format check + lint)
# Use this before committing code to ensure quality standards
# This checks formatting without modifying files and runs linting
check:
	docker exec -it docker-api-1 black --check src/
	docker exec -it docker-api-1 ruff check src/
