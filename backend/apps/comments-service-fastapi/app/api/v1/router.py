from fastapi import APIRouter

from app.api.v1.controllers.comment_controller import router as comment_controller_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(comment_controller_router)
