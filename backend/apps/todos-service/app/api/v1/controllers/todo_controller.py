from fastapi import APIRouter, Depends, Query, status

from app.schemas.todo_schema import TodoCreate, TodoListResponse, TodoRead, TodoUpdate
from app.services.todo_service import TodoService


class TodoController:
    router = APIRouter(prefix="/todos", tags=["todos"])

    @staticmethod
    @router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
    async def create_todo(data: TodoCreate, todo_service: TodoService = Depends(TodoService)) -> TodoRead:
        return await todo_service.create_todo(data)

    @staticmethod
    @router.get("", response_model=list[TodoRead])
    async def list_todos(
        todo_service: TodoService = Depends(TodoService),
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[TodoRead]:
        return await todo_service.list_todos(skip=skip, limit=limit)

    @staticmethod
    @router.get("/user/{user_id}", response_model=TodoListResponse)
    async def list_todos_by_user(
        user_id: str,
        todo_service: TodoService = Depends(TodoService),
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=1, le=500),
    ) -> TodoListResponse:
        return await todo_service.list_todos_by_user(user_id, skip=skip, limit=limit)

    @staticmethod
    @router.get("/{todo_id}", response_model=TodoRead)
    async def get_todo(todo_id: str, todo_service: TodoService = Depends(TodoService)) -> TodoRead:
        return await todo_service.get_todo(todo_id)

    @staticmethod
    @router.patch("/{todo_id}", response_model=TodoRead)
    async def update_todo(
        todo_id: str,
        data: TodoUpdate,
        todo_service: TodoService = Depends(TodoService),
    ) -> TodoRead:
        return await todo_service.update_todo(todo_id, data)

    @staticmethod
    @router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_todo(todo_id: str, todo_service: TodoService = Depends(TodoService)) -> None:
        await todo_service.delete_todo(todo_id)
