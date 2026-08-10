from fastapi import Depends, HTTPException, status

from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import TodoCreate, TodoListResponse, TodoRead, TodoUpdate


class TodoService:
    """
    Service layer containing all business logic for todo management.
    FastAPI resolves TodoRepository automatically via Depends(TodoRepository).
    """

    def __init__(self, todo_repository: TodoRepository = Depends(TodoRepository)) -> None:
        self._repository = todo_repository

    async def create_todo(self, data: TodoCreate) -> TodoRead:
        todo = await self._repository.create(data)
        return TodoRead.model_validate(todo)

    async def get_todo(self, todo_id: str) -> TodoRead:
        todo = await self._repository.get_by_id(todo_id)
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")
        return TodoRead.model_validate(todo)

    async def list_todos(self, skip: int = 0, limit: int = 100) -> list[TodoRead]:
        todos = await self._repository.get_all(skip=skip, limit=limit)
        return [TodoRead.model_validate(t) for t in todos]

    async def list_todos_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> TodoListResponse:
        todos, total = await self._repository.get_by_user_id(user_id, skip=skip, limit=limit)
        return TodoListResponse(
            items=[TodoRead.model_validate(t) for t in todos],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_todo(self, todo_id: str, data: TodoUpdate) -> TodoRead:
        todo = await self._repository.update(todo_id, data)
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")
        return TodoRead.model_validate(todo)

    async def delete_todo(self, todo_id: str) -> None:
        deleted = await self._repository.delete(todo_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")
