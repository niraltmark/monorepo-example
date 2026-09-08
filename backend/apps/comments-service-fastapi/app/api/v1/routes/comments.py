from fastapi import APIRouter, Depends, Query, status

from app.schemas.comment import CommentCreate, CommentListResponse, CommentRead, CommentUpdate
from app.services.comment_service import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    comment_service: CommentService = Depends(CommentService),
) -> CommentRead:
    return await comment_service.create_comment(data)

@router.get("", response_model=list[CommentRead])
async def list_comments(
    comment_service: CommentService = Depends(CommentService),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[CommentRead]:
    return await comment_service.list_comments(skip=skip, limit=limit)

@router.get("/todo/{todo_id}", response_model=CommentListResponse)
async def list_comments_by_todo(
    todo_id: str,
    comment_service: CommentService = Depends(CommentService),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> CommentListResponse:
    return await comment_service.list_comments_by_todo(todo_id, skip=skip, limit=limit)

@router.get("/user/{user_id}", response_model=CommentListResponse)
async def list_comments_by_user(
    user_id: str,
    comment_service: CommentService = Depends(CommentService),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> CommentListResponse:
    return await comment_service.list_comments_by_user(user_id, skip=skip, limit=limit)

@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment(
    comment_id: str,
    comment_service: CommentService = Depends(CommentService),
) -> CommentRead:
    return await comment_service.get_comment(comment_id)

@router.patch("/{comment_id}", response_model=CommentRead)
async def update_comment(
    comment_id: str,
    data: CommentUpdate,
    comment_service: CommentService = Depends(CommentService),
) -> CommentRead:
    return await comment_service.update_comment(comment_id, data)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    comment_service: CommentService = Depends(CommentService),
) -> None:
    await comment_service.delete_comment(comment_id)
