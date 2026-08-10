from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.todo import Todo
from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import TodoCreate, TodoStatus
from app.services.todo_service import TodoService


def make_todo(**kwargs) -> Todo:
    from datetime import datetime, timezone

    defaults = dict(
        id="todo-uuid",
        title="Buy groceries",
        description=None,
        status="pending",
        is_completed=False,
        due_date=None,
        user_id="user-uuid",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    todo = MagicMock(spec=Todo)
    for k, v in defaults.items():
        setattr(todo, k, v)
    return todo


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock(spec=TodoRepository)


@pytest.fixture
def service(mock_repo: AsyncMock) -> TodoService:
    return TodoService(mock_repo)


@pytest.mark.asyncio
async def test_create_todo(service: TodoService, mock_repo: AsyncMock) -> None:
    todo = make_todo()
    mock_repo.create.return_value = todo

    data = TodoCreate(title="Buy groceries", user_id="user-uuid", status=TodoStatus.PENDING)
    result = await service.create_todo(data)

    assert result.title == "Buy groceries"
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_todo_not_found(service: TodoService, mock_repo: AsyncMock) -> None:
    from fastapi import HTTPException

    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_todo("nonexistent-id")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo_not_found(service: TodoService, mock_repo: AsyncMock) -> None:
    from fastapi import HTTPException

    mock_repo.delete.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_todo("nonexistent-id")

    assert exc_info.value.status_code == 404
