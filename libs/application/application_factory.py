from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Protocol

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from context_service.middleware import ContextMiddleware
from database.database_base import DatabaseBase
from database.database_session import DatabaseSessionManager
from event_bus.consumer import EventConsumer
from event_bus.dependencies import init_event_bus


class ApplicationSettings(Protocol):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    DATABASE_URL: str
    SECRET_KEY: str
    REDIS_URL: str
    ALLOWED_ORIGINS: list[str]


EventHandlerRegistrar = Callable[[EventConsumer], None]


def create_application(
    *,
    settings: ApplicationSettings,
    api_router: APIRouter,
    register_event_handlers: EventHandlerRegistrar,
) -> FastAPI:
    database_session_manager = DatabaseSessionManager(
        database_url=settings.DATABASE_URL,
        debug=settings.DEBUG,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        async with database_session_manager.engine.begin() as connection:
            await connection.run_sync(DatabaseBase.metadata.create_all)

        redis_client = init_event_bus(app, settings.REDIS_URL)
        event_consumer = EventConsumer(app=app, redis_url=settings.REDIS_URL)
        register_event_handlers(event_consumer)
        await event_consumer.start()

        try:
            yield
        finally:
            await event_consumer.stop()
            await redis_client.aclose()
            await database_session_manager.dispose()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.state.database_session_manager = database_session_manager
    app.add_middleware(ContextMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.APP_NAME}

    return app
