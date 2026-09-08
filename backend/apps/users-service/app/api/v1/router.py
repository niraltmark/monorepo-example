from fastapi import APIRouter

from app.api.v1.controllers.user_controller import router as user_controller_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_controller_router)
