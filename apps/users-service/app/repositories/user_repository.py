import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.repositories.base import AbstractRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(AbstractRepository[User, UserCreate, UserUpdate]):
    """
    Concrete repository for User persistence operations.
    All database access is encapsulated here — services never touch SQLAlchemy directly.
    FastAPI resolves the AsyncSession automatically via Depends(get_db).
    """

    def __init__(self, session: AsyncSession = Depends(get_db)) -> None:
        super().__init__(session)

    async def get_by_id(self, entity_id: str) -> User | None:
        result = await self._session.execute(select(User).where(User.id == entity_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self._session.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, data: UserCreate) -> User:
        user = User(
            id=str(uuid.uuid4()),
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update(self, entity_id: str, data: UserUpdate) -> User | None:
        user = await self.get_by_id(entity_id)
        if not user:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update_password(self, entity_id: str, new_hashed_password: str) -> User | None:
        user = await self.get_by_id(entity_id)
        if not user:
            return None
        user.hashed_password = new_hashed_password
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def delete(self, entity_id: str) -> bool:
        user = await self.get_by_id(entity_id)
        if not user:
            return False
        await self._session.delete(user)
        await self._session.flush()
        return True
