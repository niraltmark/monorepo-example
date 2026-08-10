from unittest.mock import MagicMock

import pytest
from rest_framework.exceptions import NotFound, ValidationError

from comments.models import Comment
from comments.repositories.comment_repository import CommentRepository
from comments.services.comment_service import CommentService


def make_comment(**kwargs) -> MagicMock:
    from datetime import datetime, timezone

    defaults = dict(
        id="550e8400-e29b-41d4-a716-446655440000",
        user_id="user-uuid",
        todo_id="todo-uuid",
        body="This is a comment",
        status=Comment.Status.ACTIVE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    comment = MagicMock(spec=Comment)
    for key, value in defaults.items():
        setattr(comment, key, value)
    return comment


@pytest.fixture
def mock_repo() -> MagicMock:
    return MagicMock(spec=CommentRepository)


@pytest.fixture
def service(mock_repo: MagicMock) -> CommentService:
    return CommentService(comment_repository=mock_repo)


def test_create_comment_success(service: CommentService, mock_repo: MagicMock) -> None:
    comment = make_comment()
    mock_repo.create.return_value = comment

    result = service.create_comment(
        user_id="user-uuid", todo_id="todo-uuid", body="Great todo!"
    )

    assert result.body == "This is a comment"
    mock_repo.create.assert_called_once()


def test_create_comment_empty_body_raises(service: CommentService, mock_repo: MagicMock) -> None:
    with pytest.raises(ValidationError):
        service.create_comment(user_id="user-uuid", todo_id="todo-uuid", body="   ")


def test_get_comment_not_found_raises(service: CommentService, mock_repo: MagicMock) -> None:
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFound):
        service.get_comment("nonexistent-id")


def test_delete_comment_not_found_raises(service: CommentService, mock_repo: MagicMock) -> None:
    mock_repo.delete.return_value = False

    with pytest.raises(NotFound):
        service.delete_comment("nonexistent-id")
