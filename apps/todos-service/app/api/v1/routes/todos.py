from fastapi import APIRouter, Depends, Query, status

from app.schemas.todo import TodoCreate, TodoListResponse, TodoRead, TodoUpdate
from app.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(
    data: TodoCreate,
    todo_service: TodoService = Depends(TodoService),
) -> TodoRead:
    """Create a new todo item."""
    return await todo_service.create_todo(data)


@router.get("", response_model=list[TodoRead])
async def list_todos(
    todo_service: TodoService = Depends(TodoService),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[TodoRead]:
    """List all todos (paginated)."""
    return await todo_service.list_todos(skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=TodoListResponse)
async def list_todos_by_user(
    user_id: str,
    todo_service: TodoService = Depends(TodoService),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> TodoListResponse:
    """List todos for a specific user (by user_id from users-service)."""
    return await todo_service.list_todos_by_user(user_id, skip=skip, limit=limit)


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: str,
    todo_service: TodoService = Depends(TodoService),
) -> TodoRead:
    """Retrieve a todo by its ID."""
    return await todo_service.get_todo(todo_id)


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: str,
    data: TodoUpdate,
    todo_service: TodoService = Depends(TodoService),
) -> TodoRead:
    """Update a todo item."""
    return await todo_service.update_todo(todo_id, data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    todo_service: TodoService = Depends(TodoService),
) -> None:
    """Delete a todo by its ID."""
    await todo_service.delete_todo(todo_id)
