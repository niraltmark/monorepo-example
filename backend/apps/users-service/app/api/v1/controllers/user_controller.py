from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.user_schema import LoginRequest, TokenResponse, UserCreate, UserPasswordUpdate, UserRead, UserUpdate
from app.services.user_service import UserService
from context_service.dependencies import require_authenticated
from context_service.service import ContextService


class UserController:
    def __init__(
        self,
        user_service: UserService = Depends(UserService),
        context_service: ContextService = Depends(ContextService),
    ) -> None:
        self._user_service = user_service
        self._context_service = context_service

    async def register(self, data: UserCreate) -> UserRead:
        return await self._user_service.register(data)

    async def login(self, data: LoginRequest) -> TokenResponse:
        return await self._user_service.login(data)

    async def get_me(self) -> UserRead:
        return await self._user_service.get_user(self._context_service.get().user_id)

    async def list_users(self, skip: int, limit: int) -> list[UserRead]:
        return await self._user_service.list_users(skip=skip, limit=limit)

    async def get_user(self, user_id: str) -> UserRead:
        return await self._user_service.get_user(user_id)

    async def update_user(self, user_id: str, data: UserUpdate) -> UserRead:
        return await self._user_service.update_user(user_id, data)

    async def change_password(self, user_id: str, data: UserPasswordUpdate) -> UserRead:
        if self._context_service.get().user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only change your own password.")
        return await self._user_service.change_password(user_id, data)

    async def delete_user(self, user_id: str) -> None:
        await self._user_service.delete_user(user_id)


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    user_controller: UserController = Depends(UserController),
) -> UserRead:
    return await user_controller.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    user_controller: UserController = Depends(UserController),
) -> TokenResponse:
    return await user_controller.login(data)


@router.get("/me", response_model=UserRead)
async def get_me(
    user_controller: UserController = Depends(UserController),
    authenticated_context_service: ContextService = Depends(require_authenticated),
) -> UserRead:
    return await user_controller.get_me()


@router.get("", response_model=list[UserRead])
async def list_users(
    user_controller: UserController = Depends(UserController),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[UserRead]:
    return await user_controller.list_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    user_controller: UserController = Depends(UserController),
) -> UserRead:
    return await user_controller.get_user(user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    data: UserUpdate,
    user_controller: UserController = Depends(UserController),
) -> UserRead:
    return await user_controller.update_user(user_id, data)


@router.put("/{user_id}/password", response_model=UserRead)
async def change_password(
    user_id: str,
    data: UserPasswordUpdate,
    user_controller: UserController = Depends(UserController),
    authenticated_context_service: ContextService = Depends(require_authenticated),
) -> UserRead:
    return await user_controller.change_password(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_controller: UserController = Depends(UserController),
) -> None:
    await user_controller.delete_user(user_id)
