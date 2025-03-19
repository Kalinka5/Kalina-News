# Kalina News Makefile

.PHONY: install run test migrate revision help clean db-setup db-direct start-postgres check-postgres db-simple

# Default target
.DEFAULT_GOAL := help

install: ## Install all dependencies
	pip install -r requirements.txt

run: ## Run the application
	uvicorn app.main:app --reload

test: ## Run the tests
	pytest -v

migrate: ## Apply all migrations
	python run_migration.py

revision: ## Create a new migration
	python create_migration.py

setup: ## Setup project with one command
	python setup.py

db-setup: ## Setup database using Alembic (with migrations)
	python db_setup.py

db-direct: ## Setup database directly (without migrations)
	python database.py

db-simple: ## Simplest database setup (no migrations, no config dependency)
	python direct_db_setup.py

start-postgres: ## Start PostgreSQL service (requires sudo)
	@echo "Starting PostgreSQL service..."
	@if [ -f /etc/arch-release ] || [ -f /etc/manjaro-release ]; then \
		echo "Detected Arch/Manjaro Linux"; \
		sudo systemctl start postgresql; \
	elif [ -f /etc/debian_version ]; then \
		echo "Detected Debian/Ubuntu Linux"; \
		sudo systemctl start postgresql; \
	elif command -v brew >/dev/null 2>&1; then \
		echo "Detected macOS with Homebrew"; \
		brew services start postgresql; \
	else \
		echo "Detected generic Linux"; \
		sudo systemctl start postgresql; \
	fi

check-postgres: ## Check if PostgreSQL is running
	@if nc -z localhost 5432 >/dev/null 2>&1; then \
		echo "✅ PostgreSQL is running on localhost:5432"; \
	else \
		echo "❌ PostgreSQL is not running"; \
		echo "Run 'make start-postgres' to start it"; \
	fi

clean: ## Remove Python and test cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

help: ## Show this help
	@echo "Kalina News Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Database Commands:"
	@echo "  make db-setup      Setup database using migrations (preferred for development)"
	@echo "  make db-direct     Setup database directly without migrations (fallback option)"
	@echo "  make start-postgres Start PostgreSQL database service"
	@echo "  make check-postgres Check if PostgreSQL is running" 