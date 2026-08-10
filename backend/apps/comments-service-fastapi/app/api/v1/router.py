from fastapi import APIRouter

from app.api.v1.routes.comments import router as comments_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(comments_router)
