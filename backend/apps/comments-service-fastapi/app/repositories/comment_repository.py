import uuid

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database_session import get_database_session
from app.models.comment_model import CommentModel
from repositories.base_repository import BaseRepository
from app.schemas.comment_schema import CommentCreate, CommentUpdate

class CommentRepository(BaseRepository[CommentModel, CommentCreate, CommentUpdate]):

    def __init__(self, database_session: AsyncSession = Depends(get_database_session)) -> None:
        super().__init__(database_session)

    async def get_by_id(self, entity_id: str) -> CommentModel | None:
        result = await self._session.execute(
            select(CommentModel).where(CommentModel.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[CommentModel]:
        result = await self._session.execute(select(CommentModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_todo_id(
        self, todo_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[CommentModel], int]:
        base_query = select(CommentModel).where(
            CommentModel.todo_id == todo_id, CommentModel.status == "active"
        )
        count_result = await self._session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()
        result = await self._session.execute(base_query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[CommentModel], int]:
        base_query = select(CommentModel).where(
            CommentModel.user_id == user_id, CommentModel.status == "active"
        )
        count_result = await self._session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()
        result = await self._session.execute(base_query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def create(self, data: CommentCreate) -> CommentModel:
        comment = CommentModel(
            id=str(uuid.uuid4()),
            user_id=data.user_id,
            todo_id=data.todo_id,
            body=data.body,
        )
        self._session.add(comment)
        await self._session.flush()
        await self._session.refresh(comment)
        return comment

    async def update(self, entity_id: str, data: CommentUpdate) -> CommentModel | None:
        comment = await self.get_by_id(entity_id)
        if not comment:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)
        await self._session.flush()
        await self._session.refresh(comment)
        return comment

    async def delete(self, entity_id: str) -> bool:
        comment = await self.get_by_id(entity_id)
        if not comment:
            return False
        comment.status = "deleted"
        await self._session.flush()
        return True
