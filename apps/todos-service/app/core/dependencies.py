from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.todo_repository import TodoRepository
from app.services.todo_service import TodoService

# ── Session dependency ────────────────────────────────────────────────────────

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

# ── Repository dependency ─────────────────────────────────────────────────────


def get_todo_repository(database_session: DatabaseSession) -> TodoRepository:
    """Provide a TodoRepository bound to the current request session."""
    return TodoRepository(database_session)


TodoRepositoryDependency = Annotated[TodoRepository, Depends(get_todo_repository)]

# ── Service dependency ────────────────────────────────────────────────────────


def get_todo_service(todo_repository: TodoRepositoryDependency) -> TodoService:
    """Provide a TodoService with its repository injected."""
    return TodoService(todo_repository)


TodoServiceDependency = Annotated[TodoService, Depends(get_todo_service)]
