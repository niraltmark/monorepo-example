from fastapi import APIRouter, Depends, Query, status

from app.schemas.todo_schema import TodoCreate, TodoListResponse, TodoRead, TodoUpdate
from app.services.todo_service import TodoService


class TodoController:
    def __init__(self, todo_service: TodoService = Depends(TodoService)) -> None:
        self._todo_service = todo_service

    async def create_todo(self, data: TodoCreate) -> TodoRead:
        return await self._todo_service.create_todo(data)

    async def list_todos(self, skip: int, limit: int) -> list[TodoRead]:
        return await self._todo_service.list_todos(skip=skip, limit=limit)

    async def list_todos_by_user(self, user_id: str, skip: int, limit: int) -> TodoListResponse:
        return await self._todo_service.list_todos_by_user(user_id, skip=skip, limit=limit)

    async def get_todo(self, todo_id: str) -> TodoRead:
        return await self._todo_service.get_todo(todo_id)

    async def update_todo(self, todo_id: str, data: TodoUpdate) -> TodoRead:
        return await self._todo_service.update_todo(todo_id, data)

    async def delete_todo(self, todo_id: str) -> None:
        await self._todo_service.delete_todo(todo_id)


router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(
    data: TodoCreate,
    todo_controller: TodoController = Depends(TodoController),
) -> TodoRead:
    return await todo_controller.create_todo(data)


@router.get("", response_model=list[TodoRead])
async def list_todos(
    todo_controller: TodoController = Depends(TodoController),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[TodoRead]:
    return await todo_controller.list_todos(skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=TodoListResponse)
async def list_todos_by_user(
    user_id: str,
    todo_controller: TodoController = Depends(TodoController),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> TodoListResponse:
    return await todo_controller.list_todos_by_user(user_id, skip=skip, limit=limit)


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: str,
    todo_controller: TodoController = Depends(TodoController),
) -> TodoRead:
    return await todo_controller.get_todo(todo_id)


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: str,
    data: TodoUpdate,
    todo_controller: TodoController = Depends(TodoController),
) -> TodoRead:
    return await todo_controller.update_todo(todo_id, data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    todo_controller: TodoController = Depends(TodoController),
) -> None:
    await todo_controller.delete_todo(todo_id)
