from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.comment import Comment
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.comment_service import CommentService


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
def mock_repo() -> AsyncMock:
    return AsyncMock(spec=CommentRepository)


@pytest.fixture
def comment_service(mock_repo: AsyncMock) -> CommentService:
    return CommentService(comment_repository=mock_repo)


@pytest.mark.asyncio
async def test_create_comment_success(comment_service: CommentService, mock_repo: AsyncMock) -> None:
    comment = make_comment()
    mock_repo.create.return_value = comment

    data = CommentCreate(user_id="user-uuid", todo_id="todo-uuid", body="Great todo!")
    result = await comment_service.create_comment(data)

    assert result.body == "This is a comment"
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comment_not_found_raises(comment_service: CommentService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await comment_service.get_comment("nonexistent-id")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_comment_deleted_raises(comment_service: CommentService, mock_repo: AsyncMock) -> None:
    comment = make_comment(status="deleted")
    mock_repo.get_by_id.return_value = comment

    with pytest.raises(HTTPException) as exc_info:
        await comment_service.get_comment("deleted-id")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_comment_not_found_raises(comment_service: CommentService, mock_repo: AsyncMock) -> None:
    mock_repo.delete.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        await comment_service.delete_comment("nonexistent-id")

    assert exc_info.value.status_code == 404
