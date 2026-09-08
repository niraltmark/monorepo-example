from fastapi import APIRouter

from app.api.v1.controllers.comment_controller import CommentController

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(CommentController.router)
