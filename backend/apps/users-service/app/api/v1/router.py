from fastapi import APIRouter

from app.api.v1.controllers.user_controller import UserController

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(UserController.router)
