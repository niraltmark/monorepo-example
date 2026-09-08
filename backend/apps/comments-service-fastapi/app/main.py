from application.application_factory import create_application
from app.api.v1.router import api_router
from app.core.config import settings
from app.event_handlers import register_handlers

app = create_application(
    settings=settings,
    api_router=api_router,
    register_event_handlers=register_handlers,
)
