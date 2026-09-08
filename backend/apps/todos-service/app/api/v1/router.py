from fastapi import APIRouter

from app.api.v1.controllers.todo_controller import router as todo_controller_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(todo_controller_router)
