from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService


def make_user(**kwargs) -> User:
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
    user = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(user, k, v)
    return user


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def service(mock_repo: AsyncMock) -> UserService:
    return UserService(mock_repo)


@pytest.mark.asyncio
async def test_register_success(service: UserService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_email.return_value = None
    mock_repo.get_by_username.return_value = None
    user = make_user()
    mock_repo.create.return_value = user

    data = UserCreate(email="alice@example.com", username="alice", password="SecurePass1")
    result = await service.register(data)

    assert result.email == "alice@example.com"
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_email(service: UserService, mock_repo: AsyncMock) -> None:
    from fastapi import HTTPException

    mock_repo.get_by_email.return_value = make_user()

    data = UserCreate(email="alice@example.com", username="alice", password="SecurePass1")
    with pytest.raises(HTTPException) as exc_info:
        await service.register(data)

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_get_user_not_found(service: UserService, mock_repo: AsyncMock) -> None:
    from fastapi import HTTPException

    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_user("nonexistent-id")

    assert exc_info.value.status_code == 404
