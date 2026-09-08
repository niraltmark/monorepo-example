from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.user_schema import LoginRequest, TokenResponse, UserCreate, UserPasswordUpdate, UserRead, UserUpdate
from app.services.user_service import UserService
from context_service.dependencies import require_authenticated
from context_service.service import ContextService


class UserController:
    router = APIRouter(prefix="/users", tags=["users"])

    @staticmethod
    @router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
    async def register(data: UserCreate, user_service: UserService = Depends(UserService)) -> UserRead:
        return await user_service.register(data)

    @staticmethod
    @router.post("/login", response_model=TokenResponse)
    async def login(data: LoginRequest, user_service: UserService = Depends(UserService)) -> TokenResponse:
        return await user_service.login(data)

    @staticmethod
    @router.get("/me", response_model=UserRead)
    async def get_me(
        context_service: ContextService = Depends(require_authenticated),
        user_service: UserService = Depends(UserService),
    ) -> UserRead:
        return await user_service.get_user(context_service.get().user_id)

    @staticmethod
    @router.get("", response_model=list[UserRead])
    async def list_users(
        user_service: UserService = Depends(UserService),
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[UserRead]:
        return await user_service.list_users(skip=skip, limit=limit)

    @staticmethod
    @router.get("/{user_id}", response_model=UserRead)
    async def get_user(user_id: str, user_service: UserService = Depends(UserService)) -> UserRead:
        return await user_service.get_user(user_id)

    @staticmethod
    @router.patch("/{user_id}", response_model=UserRead)
    async def update_user(
        user_id: str,
        data: UserUpdate,
        user_service: UserService = Depends(UserService),
    ) -> UserRead:
        return await user_service.update_user(user_id, data)

    @staticmethod
    @router.put("/{user_id}/password", response_model=UserRead)
    async def change_password(
        user_id: str,
        data: UserPasswordUpdate,
        user_service: UserService = Depends(UserService),
        context_service: ContextService = Depends(require_authenticated),
    ) -> UserRead:
        if context_service.get().user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only change your own password.")
        return await user_service.change_password(user_id, data)

    @staticmethod
    @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_user(user_id: str, user_service: UserService = Depends(UserService)) -> None:
        await user_service.delete_user(user_id)
