from fastapi import APIRouter

from app.api.v1.controllers.todo_controller import TodoController

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(TodoController.router)
