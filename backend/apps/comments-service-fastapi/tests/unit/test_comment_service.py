from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.comment_model import Comment
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment_schema import CommentCreate
from app.services.comment_service import CommentService
from context_service.models import RequestContext
from event_bus.publisher import EventPublisher


def make_comment(**kwargs) -> MagicMock:
    from datetime import datetime, timezone

    defaults = dict(
        id="comment-uuid",
        user_id="user-uuid",
        todo_id="todo-uuid",
        body="This is a comment",
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    comment = MagicMock(spec=Comment)
    for key, value in defaults.items():
        setattr(comment, key, value)
    return comment


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=CommentRepository)


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    return AsyncMock(spec=EventPublisher)


@pytest.fixture
def mock_context_service() -> MagicMock:
    context_service = MagicMock()
    context_service.get.return_value = RequestContext()
    return context_service


@pytest.fixture
def comment_service(
    mock_repository: AsyncMock,
    mock_event_publisher: AsyncMock,
    mock_context_service: MagicMock,
) -> CommentService:
    return CommentService(
        comment_repository=mock_repository,
        event_publisher=mock_event_publisher,
        context_service=mock_context_service,
    )


@pytest.mark.asyncio
async def test_create_comment_success(
    comment_service: CommentService,
    mock_repository: AsyncMock,
    mock_event_publisher: AsyncMock,
) -> None:
    mock_repository.create.return_value = make_comment()

    data = CommentCreate(user_id="user-uuid", todo_id="todo-uuid", body="Great todo!")
    result = await comment_service.create_comment(data)

    assert result.body == "This is a comment"
    mock_repository.create.assert_awaited_once()
    mock_event_publisher.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comment_not_found_raises(
    comment_service: CommentService, mock_repository: AsyncMock
) -> None:
    mock_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await comment_service.get_comment("nonexistent-id")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_comment_deleted_raises(
    comment_service: CommentService, mock_repository: AsyncMock
) -> None:
    mock_repository.get_by_id.return_value = make_comment(status="deleted")

    with pytest.raises(HTTPException) as exc_info:
        await comment_service.get_comment("deleted-id")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_comment_not_found_raises(
    comment_service: CommentService, mock_repository: AsyncMock
) -> None:
    mock_repository.delete.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        await comment_service.delete_comment("nonexistent-id")

    assert exc_info.value.status_code == 404
