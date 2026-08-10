from fastapi import Depends, HTTPException, status

from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate, CommentListResponse, CommentRead, CommentUpdate


class CommentService:
    """
    Service layer containing all business logic for comment management.
    FastAPI resolves CommentRepository automatically via Depends(CommentRepository).
    """

    def __init__(self, comment_repository: CommentRepository = Depends(CommentRepository)) -> None:
        self._repository = comment_repository

    async def create_comment(self, data: CommentCreate) -> CommentRead:
        comment = await self._repository.create(data)
        return CommentRead.model_validate(comment)

    async def get_comment(self, comment_id: str) -> CommentRead:
        comment = await self._repository.get_by_id(comment_id)
        if not comment or comment.status == "deleted":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
        return CommentRead.model_validate(comment)

    async def list_comments(self, skip: int = 0, limit: int = 100) -> list[CommentRead]:
        comments = await self._repository.get_all(skip=skip, limit=limit)
        return [CommentRead.model_validate(c) for c in comments]

    async def list_comments_by_todo(
        self, todo_id: str, skip: int = 0, limit: int = 100
    ) -> CommentListResponse:
        comments, total = await self._repository.get_by_todo_id(todo_id, skip=skip, limit=limit)
        return CommentListResponse(
            items=[CommentRead.model_validate(c) for c in comments],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def list_comments_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> CommentListResponse:
        comments, total = await self._repository.get_by_user_id(user_id, skip=skip, limit=limit)
        return CommentListResponse(
            items=[CommentRead.model_validate(c) for c in comments],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_comment(self, comment_id: str, data: CommentUpdate) -> CommentRead:
        comment = await self._repository.update(comment_id, data)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
        return CommentRead.model_validate(comment)

    async def delete_comment(self, comment_id: str) -> None:
        deleted = await self._repository.delete(comment_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
