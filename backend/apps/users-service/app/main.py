from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import Base, engine
from app.event_handlers import register_handlers
from context_service.middleware import ContextMiddleware
from event_bus.consumer import EventConsumer
from event_bus.dependencies import init_event_bus


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ── Database ──────────────────────────────────────────────────────────────
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # ── Event bus ─────────────────────────────────────────────────────────────
    init_event_bus(app, settings.REDIS_URL)

    consumer = EventConsumer(app=app, redis_url=settings.REDIS_URL)
    register_handlers(consumer)
    await consumer.start()

    yield

    await consumer.stop()
    await app.state.redis.aclose()
    await engine.dispose()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ContextMiddleware must be added BEFORE CORSMiddleware so that the context
    # is available to all downstream middleware and route handlers.
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


app = create_application()
