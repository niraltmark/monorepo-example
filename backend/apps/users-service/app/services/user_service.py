from fastapi import Depends, HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserPasswordUpdate,
    UserRead,
    UserUpdate,
)
from context_service.service import ContextService
from event_bus.dependencies import get_event_publisher
from event_bus.publisher import EventPublisher
from event_bus.schemas import UserCreatedEvent, UserDeletedEvent, UserUpdatedEvent

class UserService:

    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        event_publisher: EventPublisher = Depends(get_event_publisher),
        context_service: ContextService = Depends(ContextService),
    ) -> None:
        self._repository = user_repository
        self._publisher = event_publisher
        self._context = context_service

    async def register(self, data: UserCreate) -> UserRead:
        if await self._repository.get_by_email(data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")
        if await self._repository.get_by_username(data.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this username already exists.")
        user = await self._repository.create(data)
        result = UserRead.model_validate(user)
        await self._publisher.publish(
            UserCreatedEvent(payload={"user_id": result.id, "email": result.email, "username": result.username}),
            context_service=self._context,
        )
        return result

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._repository.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.", headers={"WWW-Authenticate": "Bearer"})
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been deactivated.")
        token = create_access_token(subject=user.id)
        return TokenResponse(access_token=token)

    async def get_user(self, user_id: str) -> UserRead:
        user = await self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserRead.model_validate(user)

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[UserRead]:
        users = await self._repository.get_all(skip=skip, limit=limit)
        return [UserRead.model_validate(u) for u in users]

    async def update_user(self, user_id: str, data: UserUpdate) -> UserRead:
        user = await self._repository.update(user_id, data)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        result = UserRead.model_validate(user)
        await self._publisher.publish(
            UserUpdatedEvent(payload={"user_id": result.id, "changes": data.model_dump(exclude_unset=True)}),
            context_service=self._context,
        )
        return result

    async def change_password(self, user_id: str, data: UserPasswordUpdate) -> UserRead:
        user = await self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")
        updated = await self._repository.update_password(user_id, hash_password(data.new_password))
        result = UserRead.model_validate(updated)
        await self._publisher.publish(
            UserUpdatedEvent(payload={"user_id": result.id, "changes": {"password": "changed"}}),
            context_service=self._context,
        )
        return result

    async def delete_user(self, user_id: str) -> None:
        deleted = await self._repository.delete(user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        await self._publisher.publish(
            UserDeletedEvent(payload={"user_id": user_id}),
            context_service=self._context,
        )
