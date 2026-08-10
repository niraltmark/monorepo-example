from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserPasswordUpdate,
    UserRead,
    UserUpdate,
)


class UserService:
    """
    Service layer containing all business logic for user management.
    Depends on UserRepository via constructor injection (FastAPI DI).
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def register(self, data: UserCreate) -> UserRead:
        if await self._repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )
        if await self._repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this username already exists.",
            )
        user = await self._repo.create(data)
        return UserRead.model_validate(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated.",
            )
        token = create_access_token(subject=user.id)
        return TokenResponse(access_token=token)

    async def get_user(self, user_id: str) -> UserRead:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserRead.model_validate(user)

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[UserRead]:
        users = await self._repo.get_all(skip=skip, limit=limit)
        return [UserRead.model_validate(u) for u in users]

    async def update_user(self, user_id: str, data: UserUpdate) -> UserRead:
        user = await self._repo.update(user_id, data)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserRead.model_validate(user)

    async def change_password(self, user_id: str, data: UserPasswordUpdate) -> UserRead:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        updated = await self._repo.update_password(user_id, hash_password(data.new_password))
        return UserRead.model_validate(updated)

    async def delete_user(self, user_id: str) -> None:
        deleted = await self._repo.delete(user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
