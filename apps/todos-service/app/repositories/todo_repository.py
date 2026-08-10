import uuid

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.todo import Todo
from app.repositories.base import AbstractRepository
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoRepository(AbstractRepository[Todo, TodoCreate, TodoUpdate]):
    """
    Concrete repository for Todo persistence operations.
    All database access is encapsulated here — services never touch SQLAlchemy directly.
    FastAPI resolves the AsyncSession automatically via Depends(get_db).
    """

    def __init__(self, session: AsyncSession = Depends(get_db)) -> None:
        super().__init__(session)

    async def get_by_id(self, entity_id: str) -> Todo | None:
        result = await self._session.execute(select(Todo).where(Todo.id == entity_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Todo]:
        result = await self._session.execute(select(Todo).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Todo], int]:
        """Return todos for a specific user along with the total count."""
        count_result = await self._session.execute(
            select(func.count()).select_from(Todo).where(Todo.user_id == user_id)
        )
        total = count_result.scalar_one()

        result = await self._session.execute(
            select(Todo).where(Todo.user_id == user_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, data: TodoCreate) -> Todo:
        todo = Todo(
            id=str(uuid.uuid4()),
            title=data.title,
            description=data.description,
            status=data.status.value,
            due_date=data.due_date,
            user_id=data.user_id,
        )
        self._session.add(todo)
        await self._session.flush()
        await self._session.refresh(todo)
        return todo

    async def update(self, entity_id: str, data: TodoUpdate) -> Todo | None:
        todo = await self.get_by_id(entity_id)
        if not todo:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value is not None:
                value = value.value  # convert Enum to string
            setattr(todo, field, value)
        await self._session.flush()
        await self._session.refresh(todo)
        return todo

    async def delete(self, entity_id: str) -> bool:
        todo = await self.get_by_id(entity_id)
        if not todo:
            return False
        await self._session.delete(todo)
        await self._session.flush()
        return True
