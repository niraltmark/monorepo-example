from fastapi import APIRouter, Query, status

from app.core.dependencies import TodoSvc
from app.schemas.todo import TodoCreate, TodoListResponse, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(data: TodoCreate, service: TodoSvc) -> TodoRead:
    """Create a new todo item."""
    return await service.create_todo(data)


@router.get("", response_model=list[TodoRead])
async def list_todos(
    service: TodoSvc,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[TodoRead]:
    """List all todos (paginated)."""
    return await service.list_todos(skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=TodoListResponse)
async def list_todos_by_user(
    user_id: str,
    service: TodoSvc,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> TodoListResponse:
    """List todos for a specific user (by user_id from users-service)."""
    return await service.list_todos_by_user(user_id, skip=skip, limit=limit)


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: str, service: TodoSvc) -> TodoRead:
    """Retrieve a todo by its ID."""
    return await service.get_todo(todo_id)


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(todo_id: str, data: TodoUpdate, service: TodoSvc) -> TodoRead:
    """Update a todo item."""
    return await service.update_todo(todo_id, data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str, service: TodoSvc) -> None:
    """Delete a todo by its ID."""
    await service.delete_todo(todo_id)
