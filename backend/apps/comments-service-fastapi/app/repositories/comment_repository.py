import uuid

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.comment_model import Comment
from app.repositories.base import AbstractRepository
from app.schemas.comment_schema import CommentCreate, CommentUpdate

class CommentRepository(AbstractRepository[Comment, CommentCreate, CommentUpdate]):

    def __init__(self, session: AsyncSession = Depends(get_db)) -> None:
        super().__init__(session)

    async def get_by_id(self, entity_id: str) -> Comment | None:
        result = await self._session.execute(
            select(Comment).where(Comment.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Comment]:
        result = await self._session.execute(select(Comment).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_todo_id(
        self, todo_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Comment], int]:
        base_query = select(Comment).where(
            Comment.todo_id == todo_id, Comment.status == "active"
        )
        count_result = await self._session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()
        result = await self._session.execute(base_query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Comment], int]:
        base_query = select(Comment).where(
            Comment.user_id == user_id, Comment.status == "active"
        )
        count_result = await self._session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()
        result = await self._session.execute(base_query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def create(self, data: CommentCreate) -> Comment:
        comment = Comment(
            id=str(uuid.uuid4()),
            user_id=data.user_id,
            todo_id=data.todo_id,
            body=data.body,
        )
        self._session.add(comment)
        await self._session.flush()
        await self._session.refresh(comment)
        return comment

    async def update(self, entity_id: str, data: CommentUpdate) -> Comment | None:
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
