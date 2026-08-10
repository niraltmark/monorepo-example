from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUser, UserSvc
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserPasswordUpdate,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, service: UserSvc) -> UserRead:
    """Register a new user account."""
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, service: UserSvc) -> TokenResponse:
    """Authenticate and receive a JWT access token."""
    return await service.login(data)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUser) -> UserRead:
    """Return the currently authenticated user's profile."""
    return current_user


@router.get("", response_model=list[UserRead])
async def list_users(
    service: UserSvc,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[UserRead]:
    """List all users (paginated)."""
    return await service.list_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, service: UserSvc) -> UserRead:
    """Retrieve a user by their ID."""
    return await service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: str, data: UserUpdate, service: UserSvc) -> UserRead:
    """Update a user's profile fields."""
    return await service.update_user(user_id, data)


@router.put("/{user_id}/password", response_model=UserRead)
async def change_password(
    user_id: str,
    data: UserPasswordUpdate,
    service: UserSvc,
    current_user: CurrentUser,
) -> UserRead:
    """Change a user's password (requires authentication)."""
    return await service.change_password(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, service: UserSvc) -> None:
    """Delete a user by their ID."""
    await service.delete_user(user_id)
