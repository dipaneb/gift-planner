# Declare phony targets (targets that don't represent actual files)
.PHONY: help install dev build test-unit test-e2e-dev test-e2e lint

# ============================================================================
# HELP COMMAND
# ============================================================================

help:
	@echo ""
	@echo "================================================================================"
	@echo "🎨 Gift Planner - Frontend Commands"
	@echo "================================================================================"
	@echo ""
	@echo "📦 SETUP:"
	@echo "   install              Install dependencies (pnpm install)"
	@echo ""
	@echo ""
	@echo "🚀 DEVELOPMENT:"
	@echo "   dev                  Start dev server with hot-reload"
	@echo "   build                Type-check, compile and minify for production"
	@echo ""
	@echo ""
	@echo "🧪 TESTING:"
	@echo "   test-unit            Run unit tests with Vitest"
	@echo "   test-e2e-dev         Run E2E tests against Vite dev server"
	@echo "   test-e2e             Run E2E tests against production build"
	@echo ""
	@echo ""
	@echo "🎨 CODE QUALITY:"
	@echo "   lint                 Lint code with ESLint"
	@echo ""
	@echo ""
	@echo "💡 Tip: Use 'make help' to see this menu again"
	@echo ""

# ============================================================================
# SETUP COMMANDS
# ============================================================================

# Install frontend dependencies using pnpm
install:
	pnpm install

# ============================================================================
# DEVELOPMENT COMMANDS
# ============================================================================

# Start frontend development server with hot-reload
# The server will be available at http://localhost:5173 (default Vite port)
dev:
	pnpm dev

# Type-check, compile and minify for production
# Builds optimized production bundle in dist/
build:
	pnpm build

# ============================================================================
# TESTING COMMANDS
# ============================================================================

# Run unit tests with Vitest
# Tests are located in src/**/*.spec.ts files
test-unit:
	pnpm test:unit

# Run end-to-end tests against Vite development server
# This is faster than testing production build
# Runs tests with Cypress against development server
test-e2e-dev:
	pnpm test:e2e:dev

# Run end-to-end tests against production build
# Recommended for CI/CD pipelines and pre-deployment testing
# First builds the app, then runs Cypress tests
test-e2e:
	@echo "Recommended for CI/CD pipelines and pre-deployment testing"
	@echo "First builds the app, then runs Cypress tests"
	pnpm build && pnpm test:e2e

# ============================================================================
# CODE QUALITY COMMANDS
# ============================================================================

# Lint frontend code with ESLint
# Checks for code quality issues and potential bugs
lint:
	pnpm lint
