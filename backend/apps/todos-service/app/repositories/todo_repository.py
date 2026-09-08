import uuid

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_session import get_database_session
from app.models.todo_model import TodoModel
from repositories.base_repository import BaseRepository
from app.schemas.todo_schema import TodoCreate, TodoUpdate

class TodoRepository(BaseRepository[TodoModel, TodoCreate, TodoUpdate]):

    def __init__(self, database_session: AsyncSession = Depends(get_database_session)) -> None:
        super().__init__(database_session)

    async def get_by_id(self, entity_id: str) -> TodoModel | None:
        result = await self._session.execute(select(TodoModel).where(TodoModel.id == entity_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[TodoModel]:
        result = await self._session.execute(select(TodoModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[TodoModel], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(TodoModel).where(TodoModel.user_id == user_id)
        )
        total = count_result.scalar_one()

        result = await self._session.execute(
            select(TodoModel).where(TodoModel.user_id == user_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, data: TodoCreate) -> TodoModel:
        todo = TodoModel(
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

    async def update(self, entity_id: str, data: TodoUpdate) -> TodoModel | None:
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
