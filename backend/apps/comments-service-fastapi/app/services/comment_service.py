from fastapi import Depends, HTTPException, status

from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate, CommentListResponse, CommentRead, CommentUpdate
from context_service.service import ContextService
from event_bus.dependencies import get_event_publisher
from event_bus.publisher import EventPublisher
from event_bus.schemas import CommentCreatedEvent, CommentDeletedEvent, CommentUpdatedEvent


class CommentService:
    def __init__(
        self,
        comment_repository: CommentRepository = Depends(CommentRepository),
        event_publisher: EventPublisher = Depends(get_event_publisher),
        context_service: ContextService = Depends(ContextService),
    ) -> None:
        self._repository = comment_repository
        self._publisher = event_publisher
        self._context = context_service

    async def create_comment(self, data: CommentCreate) -> CommentRead:
        comment = await self._repository.create(data)
        result = CommentRead.model_validate(comment)
        await self._publisher.publish(
            CommentCreatedEvent(payload={"comment_id": result.id, "user_id": result.user_id, "todo_id": result.todo_id}),
            context_service=self._context,
        )
        return result

    async def get_comment(self, comment_id: str) -> CommentRead:
        comment = await self._repository.get_by_id(comment_id)
        if not comment or comment.status == "deleted":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
        return CommentRead.model_validate(comment)

    async def list_comments(self, skip: int = 0, limit: int = 100) -> list[CommentRead]:
        comments = await self._repository.get_all(skip=skip, limit=limit)
        return [CommentRead.model_validate(c) for c in comments]

    async def list_comments_by_todo(self, todo_id: str, skip: int = 0, limit: int = 100) -> CommentListResponse:
        comments, total = await self._repository.get_by_todo_id(todo_id, skip=skip, limit=limit)
        return CommentListResponse(
            items=[CommentRead.model_validate(c) for c in comments],
            total=total, skip=skip, limit=limit,
        )

    async def list_comments_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> CommentListResponse:
        comments, total = await self._repository.get_by_user_id(user_id, skip=skip, limit=limit)
        return CommentListResponse(
            items=[CommentRead.model_validate(c) for c in comments],
            total=total, skip=skip, limit=limit,
        )

    async def update_comment(self, comment_id: str, data: CommentUpdate) -> CommentRead:
        comment = await self._repository.update(comment_id, data)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
        result = CommentRead.model_validate(comment)
        await self._publisher.publish(
            CommentUpdatedEvent(payload={"comment_id": result.id, "changes": data.model_dump(exclude_unset=True)}),
            context_service=self._context,
        )
        return result

    async def delete_comment(self, comment_id: str) -> None:
        deleted = await self._repository.delete(comment_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
        await self._publisher.publish(
            CommentDeletedEvent(payload={"comment_id": comment_id}),
            context_service=self._context,
        )
