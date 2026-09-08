from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.todo_model import Todo
from app.repositories.todo_repository import TodoRepository
from app.schemas.todo_schema import TodoCreate, TodoStatus
from app.services.todo_service import TodoService
from context_service.models import RequestContext
from event_bus.publisher import EventPublisher


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
    for key, value in defaults.items():
        setattr(todo, key, value)
    return todo


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=TodoRepository)


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    return AsyncMock(spec=EventPublisher)


@pytest.fixture
def mock_context_service() -> MagicMock:
    context_service = MagicMock()
    context_service.get.return_value = RequestContext()
    return context_service


@pytest.fixture
def todo_service(
    mock_repository: AsyncMock,
    mock_event_publisher: AsyncMock,
    mock_context_service: MagicMock,
) -> TodoService:
    return TodoService(
        todo_repository=mock_repository,
        event_publisher=mock_event_publisher,
        context_service=mock_context_service,
    )


@pytest.mark.asyncio
async def test_create_todo(
    todo_service: TodoService,
    mock_repository: AsyncMock,
    mock_event_publisher: AsyncMock,
) -> None:
    mock_repository.create.return_value = make_todo()

    data = TodoCreate(title="Buy groceries", user_id="user-uuid", status=TodoStatus.PENDING)
    result = await todo_service.create_todo(data)

    assert result.title == "Buy groceries"
    mock_repository.create.assert_awaited_once()
    mock_event_publisher.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_todo_not_found(
    todo_service: TodoService, mock_repository: AsyncMock
) -> None:
    from fastapi import HTTPException

    mock_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await todo_service.get_todo("nonexistent-id")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo_not_found(
    todo_service: TodoService, mock_repository: AsyncMock
) -> None:
    from fastapi import HTTPException

    mock_repository.delete.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        await todo_service.delete_todo("nonexistent-id")

    assert exc_info.value.status_code == 404
