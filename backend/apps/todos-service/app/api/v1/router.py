from fastapi import APIRouter

from app.api.v1.routes.todos import router as todos_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(todos_router)
