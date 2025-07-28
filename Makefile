.PHONY: help install install-dev serve-api serve-frontend stop-api stop-frontend stop-all \
        test test-cov test-unit test-integration test-functional test-all test-frontend test-frontend-watch \
        lint format format-check type-check security-check migrate migrate-create migrate-down \
        build build-sdk-python build-sdk-typescript docker-build docker-up docker-down docker-logs \
        docker-ps docker-clean db-shell db-backup db-restore clean setup-dev ci-test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development
install: ## Install production dependencies
	pip install -r requirements.txt
	cd ui && npm install

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	cd ui && npm install
	pre-commit install

serve-api: ## Run development API server
	PYTHONPATH=./src uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

serve-frontend: ## Run development frontend server
	cd ui && npm run dev

stop-api: ## Stop development API server
	@echo "Stopping API server..."
	@pkill -f "uvicorn app.api.main:app" || echo "API server not running"

stop-frontend: ## Stop development frontend server
	@echo "Stopping frontend server..."
	@pkill -f "vite" || echo "Frontend server not running"

stop-all: ## Stop all development servers
	@echo "Stopping all development servers..."
	@make stop-api
	@make stop-frontend
	@echo "All servers stopped"

# Testing
test: ## Run tests
	PYTHONPATH=./src pytest tests/unit tests/integration -v

test-cov: ## Run tests with coverage
	PYTHONPATH=./src pytest --cov=src --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	PYTHONPATH=./src pytest tests/unit -v -m unit

test-integration: ## Run integration tests only
	PYTHONPATH=./src pytest tests/integration -v -m integration

test-functional: ## Run functional tests only
	PYTHONPATH=./src pytest tests/functional -v -m functional

test-all: ## Run all tests (unit, integration, functional)
	PYTHONPATH=./src pytest tests -v

test-frontend: ## Run frontend tests
	cd ui && npm run test:run

test-frontend-watch: ## Run frontend tests in watch mode
	cd ui && npm test

# Code Quality
lint: ## Run all linters
	black --check src tests
	isort --check-only src tests
	flake8 src tests
	cd ui && npm run lint

format: ## Format code
	black src tests
	isort src tests
	cd ui && npm run format

format-check: ## Check code formatting
	black --check src tests
	isort --check-only src tests
	cd ui && npm run format:check

type-check: ## Run type checking
	mypy src
	cd ui && npm run type-check

security-check: ## Run security checks
	pip-audit
	bandit -r src

# Database
migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create a new migration
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down: ## Rollback last migration
	alembic downgrade -1

# Build
build: ## Build for production
	cd ui && npm run build

build-sdk-python: ## Build Python SDK
	cd client-sdk/python && python setup.py sdist bdist_wheel

build-sdk-typescript: ## Build TypeScript SDK
	cd client-sdk/typescript && npm run build

# Docker
docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View logs
	docker-compose logs -f

docker-ps: ## List running containers
	docker-compose ps

docker-clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

# Database Management
db-shell: ## Open database shell
	docker-compose exec db psql -U postgres -d fullstack_db

db-backup: ## Backup database
	docker-compose exec db pg_dump -U postgres fullstack_db > backup_$$(date +%Y%m%d_%H%M%S).sql

db-restore: ## Restore database from backup
	@read -p "Enter backup file path: " file; \
	docker-compose exec -T db psql -U postgres fullstack_db < $$file

# Utility
clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	cd ui && rm -rf dist/ node_modules/

setup-dev: ## Set up development environment
	cp .env.example .env
	make install-dev
	make docker-up
	sleep 5
	make migrate
	@echo "Development environment ready!"

# CI/CD
ci-test: ## Run CI tests
	make lint
	make type-check
	make test-cov
	make security-check