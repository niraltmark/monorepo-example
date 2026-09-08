.PHONY: help install build test lint docker-up docker-down docker-logs \
	dev-frontend dev-users dev-todos dev-comments dev-comments-fastapi \
	test-users test-todos test-comments test-comments-fastapi \
	migrate-users migrate-todos migrate-comments migrate-all

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

install: ## Install Node and every backend service dependency set
	pnpm install
	cd backend/apps/users-service && pip install -r requirements.txt
	cd backend/apps/todos-service && pip install -r requirements.txt
	cd backend/apps/comments-service-fastapi && pip install -r requirements.txt
	cd backend/apps/comments-service && pip install -r requirements.txt

dev-frontend: ## Start the React frontend dev server
	pnpm nx serve frontend

dev-users: ## Start the users-service development server
	cd backend/apps/users-service && PYTHONPATH=../../../libs:../../../libs/events:../../../libs/context-service uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

dev-todos: ## Start the todos-service development server
	cd backend/apps/todos-service && PYTHONPATH=../../../libs:../../../libs/events:../../../libs/context-service uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

dev-comments-fastapi: ## Start the FastAPI comments-service development server
	cd backend/apps/comments-service-fastapi && PYTHONPATH=../../../libs:../../../libs/events:../../../libs/context-service uvicorn app.main:app --reload --host 0.0.0.0 --port 8004

dev-comments: ## Start the Django comments-service development server
	cd backend/apps/comments-service && python manage.py runserver 0.0.0.0:8003

build: ## Build all projects
	pnpm nx run-many --target=build --all

test: ## Run all available test targets
	pnpm nx run-many --target=test --all

test-users: ## Run users-service tests
	pnpm nx test users-service-tests

test-todos: ## Run todos-service tests
	pnpm nx test todos-service-tests

test-comments-fastapi: ## Run FastAPI comments-service tests
	pnpm nx test comments-service-fastapi

test-comments: ## Run Django/DRF comments-service tests
	pnpm nx test comments-service-tests

lint: ## Lint all projects
	pnpm nx run-many --target=lint --all

docker-up: ## Start all services with Docker Compose
	docker compose up --build -d

docker-down: ## Stop all Docker Compose services
	docker compose down

docker-logs: ## Tail Docker Compose logs
	docker compose logs -f

migrate-users: ## Run Alembic migrations for users-service
	cd backend/apps/users-service && PYTHONPATH=../../../libs alembic upgrade head

migrate-todos: ## Run Alembic migrations for todos-service
	cd backend/apps/todos-service && PYTHONPATH=../../../libs alembic upgrade head

migrate-comments: ## Run Django migrations for comments-service
	cd backend/apps/comments-service && python manage.py migrate

migrate-all: migrate-users migrate-todos migrate-comments ## Run all migrations
