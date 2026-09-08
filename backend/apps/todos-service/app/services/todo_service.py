from fastapi import Depends, HTTPException, status

from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import TodoCreate, TodoListResponse, TodoRead, TodoUpdate
from context_service.service import ContextService
from event_bus.dependencies import get_event_publisher
from event_bus.publisher import EventPublisher
from event_bus.schemas import TodoCreatedEvent, TodoDeletedEvent, TodoUpdatedEvent

class TodoService:
    def __init__(
        self,
        todo_repository: TodoRepository = Depends(TodoRepository),
        event_publisher: EventPublisher = Depends(get_event_publisher),
        context_service: ContextService = Depends(ContextService),
    ) -> None:
        self._repository = todo_repository
        self._publisher = event_publisher
        self._context = context_service

    async def create_todo(self, data: TodoCreate) -> TodoRead:
        todo = await self._repository.create(data)
        result = TodoRead.model_validate(todo)
        await self._publisher.publish(
            TodoCreatedEvent(payload={"todo_id": result.id, "user_id": result.user_id, "title": result.title}),
            context_service=self._context,
        )
        return result

    async def get_todo(self, todo_id: str) -> TodoRead:
        todo = await self._repository.get_by_id(todo_id)
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")
        return TodoRead.model_validate(todo)

    async def list_todos(self, skip: int = 0, limit: int = 100) -> list[TodoRead]:
        todos = await self._repository.get_all(skip=skip, limit=limit)
        return [TodoRead.model_validate(t) for t in todos]

    async def list_todos_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> TodoListResponse:
        todos, total = await self._repository.get_by_user_id(user_id, skip=skip, limit=limit)
        return TodoListResponse(
            items=[TodoRead.model_validate(t) for t in todos],
            total=total, skip=skip, limit=limit,
        )

    async def update_todo(self, todo_id: str, data: TodoUpdate) -> TodoRead:
        todo = await self._repository.update(todo_id, data)
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")
        result = TodoRead.model_validate(todo)
        await self._publisher.publish(
            TodoUpdatedEvent(payload={"todo_id": result.id, "changes": data.model_dump(exclude_unset=True)}),
            context_service=self._context,
        )
        return result

    async def delete_todo(self, todo_id: str) -> None:
        deleted = await self._repository.delete(todo_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")
        await self._publisher.publish(
            TodoDeletedEvent(payload={"todo_id": todo_id}),
            context_service=self._context,
        )
