# monorepo-example

A full-stack **Todo App with User Management** built as an NX monorepo. The project demonstrates a microservices architecture with a React frontend and two independent Python/FastAPI backend services, each backed by its own PostgreSQL database.

## Architecture Overview

```
monorepo-example/
├── apps/
│   ├── frontend/          # React 19 + Vite + TypeScript (port 5173 / 3000)
│   ├── users-service/     # FastAPI microservice — user auth & management (port 8001)
│   └── todos-service/     # FastAPI microservice — todo CRUD (port 8002)
├── docker-compose.yml     # Full local stack
├── Makefile               # Developer shortcuts
└── nx.json                # NX workspace config
```

### Key Design Decisions

| Concern | Decision |
|---|---|
| **Monorepo tooling** | NX — unified task runner, caching, dependency graph |
| **Frontend** | React 19, Vite, TypeScript, React Router v6 |
| **Backend** | FastAPI with async SQLAlchemy 2.0 and asyncpg |
| **Database** | PostgreSQL 16 — one database per service, no cross-DB foreign keys |
| **Decoupling** | `todos.user_id` is a plain VARCHAR(36) — no FK constraint |
| **Pattern** | Repository Pattern — all DB access encapsulated in `*Repository` classes |
| **Validation** | Pydantic v2 schemas for all request/response models |
| **Migrations** | Alembic per service with async engine support |
| **Auth** | JWT (HS256) issued by users-service |

---

## Getting Started

### Prerequisites

- Node.js 22+ and pnpm
- Python 3.12+
- Docker & Docker Compose

### Quick Start with Docker

```bash
make docker-up      # Start all services
make docker-logs    # Tail logs
make docker-down    # Stop everything
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Users Service API docs | http://localhost:8001/docs |
| Todos Service API docs | http://localhost:8002/docs |

### Local Development

```bash
make install                          # Install Node + Python deps
docker compose up users-db todos-db -d
make migrate-all                      # Run Alembic migrations
make dev-users   # port 8001
make dev-todos   # port 8002
make dev-frontend  # port 5173
```

---

## API Reference

### Users Service (`/api/v1`)

| Method | Path | Description |
|---|---|---|
| POST | `/users/register` | Register a new user |
| POST | `/users/login` | Authenticate, receive JWT |
| GET | `/users/me` | Get current user |
| GET | `/users` | List all users |
| GET | `/users/{id}` | Get user by ID |
| PATCH | `/users/{id}` | Update user profile |
| PUT | `/users/{id}/password` | Change password |
| DELETE | `/users/{id}` | Delete user |

### Todos Service (`/api/v1`)

| Method | Path | Description |
|---|---|---|
| POST | `/todos` | Create a todo |
| GET | `/todos` | List all todos |
| GET | `/todos/user/{user_id}` | List todos for a user |
| GET | `/todos/{id}` | Get todo by ID |
| PATCH | `/todos/{id}` | Update todo |
| DELETE | `/todos/{id}` | Delete todo |

---

## NX Commands

```bash
pnpm nx serve frontend
pnpm nx serve users-service
pnpm nx serve todos-service
pnpm nx test users-service
pnpm nx test todos-service
pnpm nx run-many --target=build --all
pnpm nx graph
```

---

## Database Design

No cross-service foreign keys — services are independently deployable.

```sql
-- users_db.users
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    ...
);

-- todos_db.todos (separate DB, no FK to users)
CREATE TABLE todos (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,  -- plain string, no FK constraint
    title VARCHAR(255) NOT NULL,
    status todo_status NOT NULL DEFAULT 'pending',
    ...
);
```
