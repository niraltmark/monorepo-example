from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRead
from app.services.user_service import UserService

# ── Session dependency ────────────────────────────────────────────────────────

DbSession = Annotated[AsyncSession, Depends(get_db)]

# ── Repository dependency ─────────────────────────────────────────────────────


def get_user_repository(session: DbSession) -> UserRepository:
    """Provide a UserRepository bound to the current request session."""
    return UserRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repository)]

# ── Service dependency ────────────────────────────────────────────────────────


def get_user_service(repository: UserRepo) -> UserService:
    """Provide a UserService with its repository injected."""
    return UserService(repository)


UserSvc = Annotated[UserService, Depends(get_user_service)]

# ── Auth dependency ───────────────────────────────────────────────────────────

_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    service: UserSvc,
) -> UserRead:
    """Validate JWT and return the authenticated user."""
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")
    return await service.get_user(user_id)


CurrentUser = Annotated[UserRead, Depends(get_current_user)]
