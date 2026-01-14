# Declare phony targets (targets that don't represent actual files)
.PHONY: dev-start dev-stop dev-logs dev-rebuild prod-start prod-stop prod-logs prod-rebuild test format lint check

# ============================================================================
# DEVELOPMENT COMMANDS
# ============================================================================

# Start development environment with hot-reload enabled
# Code changes in src/ will automatically restart the server
# Uses docker-compose.dev.yml and Dockerfile.dev
dev-start:
	docker compose -f backend/docker/docker-compose.dev.yml up -d

# Stop development environment
# Shuts down containers but preserves the development database volume
dev-stop:
	docker compose -f backend/docker/docker-compose.dev.yml down

# View development logs in real-time
# Press Ctrl+C to exit (containers keep running)
dev-logs:
	docker compose -f backend/docker/docker-compose.dev.yml logs -f

# Rebuild and restart development environment
# Use after changing requirements.txt or Dockerfile.dev
dev-rebuild:
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

alembic-dev-init:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic init alembic

alembic-dev-rev:
	if [ -z "$(m)" ]; then \
		echo "Erreur: le message '-m' est manquant. Utilisez: make alembic-rev m=\"votre message\""; \
		exit 1; \
	fi
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic revision --autogenerate -m "$(m)"

alembic-dev-up:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic upgrade head

alembic-dev-down:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic downgrade -1

alembic-dev-history:
	docker compose -f backend/docker/docker-compose.dev.yml exec api alembic history

alembic-dev-current:
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
# TESTING & CODE QUALITY COMMANDS
# ============================================================================

# Run all tests using pytest
# Executes tests inside the running development container
# Make sure dev environment is running (make dev-start) before running tests
test:
	docker exec -it docker-api-1 pytest

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

# Run all code quality checks (format check + lint)
# Use this before committing code to ensure quality standards
# This checks formatting without modifying files and runs linting
check:
	docker exec -it docker-api-1 black --check src/
	docker exec -it docker-api-1 ruff check src/
