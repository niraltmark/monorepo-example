.PHONY: help install dev build test lint docker-up docker-down migrate-users migrate-todos

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (Node + Python)
	pnpm install
	cd backend/apps/users-service && pip install -r requirements.txt
	cd backend/apps/todos-service && pip install -r requirements.txt

dev-frontend: ## Start the React frontend dev server
	pnpm nx serve frontend

dev-users: ## Start the users-service dev server
	cd backend/apps/users-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

dev-todos: ## Start the todos-service dev server
	cd backend/apps/todos-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

build: ## Build all projects
	pnpm nx run-many --target=build --all

test: ## Run all tests
	pnpm nx run-many --target=test --all

test-users: ## Run users-service tests
	pnpm nx test users-service

test-todos: ## Run todos-service tests
	pnpm nx test todos-service

lint: ## Lint all projects
	pnpm nx run-many --target=lint --all

docker-up: ## Start all services with Docker Compose
	docker compose up --build -d

docker-down: ## Stop all Docker Compose services
	docker compose down

docker-logs: ## Tail Docker Compose logs
	docker compose logs -f

migrate-users: ## Run Alembic migrations for users-service
	cd backend/apps/users-service && alembic upgrade head

migrate-todos: ## Run Alembic migrations for todos-service
	cd backend/apps/todos-service && alembic upgrade head

migrate-all: migrate-users migrate-todos ## Run all migrations
