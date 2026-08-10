from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.todo_repository import TodoRepository
from app.services.todo_service import TodoService

# ── Session dependency ────────────────────────────────────────────────────────

DbSession = Annotated[AsyncSession, Depends(get_db)]

# ── Repository dependency ─────────────────────────────────────────────────────


def get_todo_repository(session: DbSession) -> TodoRepository:
    """Provide a TodoRepository bound to the current request session."""
    return TodoRepository(session)


TodoRepo = Annotated[TodoRepository, Depends(get_todo_repository)]

# ── Service dependency ────────────────────────────────────────────────────────


def get_todo_service(repository: TodoRepo) -> TodoService:
    """Provide a TodoService with its repository injected."""
    return TodoService(repository)


TodoSvc = Annotated[TodoService, Depends(get_todo_service)]
