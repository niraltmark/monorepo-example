from fastapi import APIRouter, Depends, Query, status

from app.schemas.comment_schema import CommentCreate, CommentListResponse, CommentRead, CommentUpdate
from app.services.comment_service import CommentService


class CommentController:
    def __init__(self, comment_service: CommentService = Depends(CommentService)) -> None:
        self._comment_service = comment_service

    async def create_comment(self, data: CommentCreate) -> CommentRead:
        return await self._comment_service.create_comment(data)

    async def list_comments(self, skip: int, limit: int) -> list[CommentRead]:
        return await self._comment_service.list_comments(skip=skip, limit=limit)

    async def list_comments_by_todo(self, todo_id: str, skip: int, limit: int) -> CommentListResponse:
        return await self._comment_service.list_comments_by_todo(todo_id, skip=skip, limit=limit)

    async def list_comments_by_user(self, user_id: str, skip: int, limit: int) -> CommentListResponse:
        return await self._comment_service.list_comments_by_user(user_id, skip=skip, limit=limit)

    async def get_comment(self, comment_id: str) -> CommentRead:
        return await self._comment_service.get_comment(comment_id)

    async def update_comment(self, comment_id: str, data: CommentUpdate) -> CommentRead:
        return await self._comment_service.update_comment(comment_id, data)

    async def delete_comment(self, comment_id: str) -> None:
        await self._comment_service.delete_comment(comment_id)


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    comment_controller: CommentController = Depends(CommentController),
) -> CommentRead:
    return await comment_controller.create_comment(data)


@router.get("", response_model=list[CommentRead])
async def list_comments(
    comment_controller: CommentController = Depends(CommentController),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[CommentRead]:
    return await comment_controller.list_comments(skip=skip, limit=limit)


@router.get("/todo/{todo_id}", response_model=CommentListResponse)
async def list_comments_by_todo(
    todo_id: str,
    comment_controller: CommentController = Depends(CommentController),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> CommentListResponse:
    return await comment_controller.list_comments_by_todo(todo_id, skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=CommentListResponse)
async def list_comments_by_user(
    user_id: str,
    comment_controller: CommentController = Depends(CommentController),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> CommentListResponse:
    return await comment_controller.list_comments_by_user(user_id, skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment(
    comment_id: str,
    comment_controller: CommentController = Depends(CommentController),
) -> CommentRead:
    return await comment_controller.get_comment(comment_id)


@router.patch("/{comment_id}", response_model=CommentRead)
async def update_comment(
    comment_id: str,
    data: CommentUpdate,
    comment_controller: CommentController = Depends(CommentController),
) -> CommentRead:
    return await comment_controller.update_comment(comment_id, data)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    comment_controller: CommentController = Depends(CommentController),
) -> None:
    await comment_controller.delete_comment(comment_id)
