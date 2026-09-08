from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService
from context_service.models import RequestContext
from event_bus.publisher import EventPublisher


def make_user(**kwargs) -> UserModel:
    from datetime import datetime, timezone

    defaults = dict(
        id="test-uuid",
        email="alice@example.com",
        username="alice",
        full_name="Alice Smith",
        hashed_password="$2b$12$hashed",
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    user = MagicMock(spec=UserModel)
    for key, value in defaults.items():
        setattr(user, key, value)
    return user


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    return AsyncMock(spec=EventPublisher)


@pytest.fixture
def mock_context_service() -> MagicMock:
    context_service = MagicMock()
    context_service.get.return_value = RequestContext()
    return context_service


@pytest.fixture
def user_service(
    mock_repository: AsyncMock,
    mock_event_publisher: AsyncMock,
    mock_context_service: MagicMock,
) -> UserService:
    return UserService(
        user_repository=mock_repository,
        event_publisher=mock_event_publisher,
        context_service=mock_context_service,
    )


@pytest.mark.asyncio
async def test_register_success(
    user_service: UserService,
    mock_repository: AsyncMock,
    mock_event_publisher: AsyncMock,
) -> None:
    mock_repository.get_by_email.return_value = None
    mock_repository.get_by_username.return_value = None
    mock_repository.create.return_value = make_user()

    data = UserCreate(email="alice@example.com", username="alice", password="SecurePass1")
    result = await user_service.register(data)

    assert result.email == "alice@example.com"
    mock_repository.create.assert_awaited_once()
    mock_event_publisher.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_email(
    user_service: UserService, mock_repository: AsyncMock
) -> None:
    from fastapi import HTTPException

    mock_repository.get_by_email.return_value = make_user()

    data = UserCreate(email="alice@example.com", username="alice", password="SecurePass1")
    with pytest.raises(HTTPException) as exc_info:
        await user_service.register(data)

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_get_user_not_found(
    user_service: UserService, mock_repository: AsyncMock
) -> None:
    from fastapi import HTTPException

    mock_repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_user("nonexistent-id")

    assert exc_info.value.status_code == 404
