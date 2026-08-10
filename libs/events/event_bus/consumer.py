"""
EventConsumer — NestJS-style microservice bootstrap for FastAPI.

The problem
-----------
Redis Pub/Sub messages arrive on a background asyncio task, completely
outside the normal HTTP request/response cycle. FastAPI's dependency
injection is designed around requests, so there is no built-in way to
call `Depends(MyService)` from a background task.

The solution — "mini app" context
----------------------------------
We replicate what NestJS does with its microservice `createMicroservice` /
`app.init()` pattern:

1. At startup we create a *dependency injection context* by calling
   `fastapi.concurrency.run_in_threadpool` — actually we use
   `dependency_injector` pattern directly through FastAPI's own
   `dependant` machinery via `fastapi.dependencies.utils.solve_dependencies`.

2. Each @event_handler decorated function declares its dependencies
   exactly like a route handler:

       @consumer.on("user.created")
       async def handle_user_created(
           event: Event,
           todo_service: TodoService = Depends(TodoService),
       ) -> None:
           ...

3. When a message arrives, EventConsumer calls `solve_dependencies` with
   a synthetic `Request`-like scope so FastAPI resolves the full DI graph
   (including DB sessions, repositories, services) just as it would for a
   real HTTP request.

This means every event handler gets a fresh, properly scoped set of
dependencies per message — identical to how a route handler works.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from fastapi.requests import Request
from starlette.datastructures import Headers
from starlette.types import Scope

from event_bus.publisher import EVENT_CHANNEL
from event_bus.schemas import Event

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Subscribes to the Redis Pub/Sub channel and dispatches incoming events
    to registered handlers using FastAPI's dependency injection machinery.

    Usage
    -----
    Instantiate once per service and register handlers:

        consumer = EventConsumer(app=app, redis_url="redis://localhost:6379")

        @consumer.on("user.created")
        async def handle_user_created(
            event: Event,
            todo_service: TodoService = Depends(TodoService),
        ) -> None:
            # todo_service is fully injected — DB session, repository, all of it
            await todo_service.handle_user_created(event)

    Then start/stop it from the FastAPI lifespan:

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await consumer.start()
            yield
            await consumer.stop()
    """

    def __init__(self, app: FastAPI, redis_url: str) -> None:
        self._app = app
        self._redis_url = redis_url
        self._handlers: dict[str, list[Callable]] = {}
        self._task: asyncio.Task | None = None
        self._redis: aioredis.Redis | None = None

    def on(self, event_type: str) -> Callable:
        """
        Decorator to register a handler for a specific event type.
        The handler signature may include any FastAPI-injectable dependencies.
        """
        def decorator(func: Callable) -> Callable:
            self._handlers.setdefault(event_type, []).append(func)
            logger.debug("Registered handler %s for event '%s'", func.__name__, event_type)
            return func
        return decorator

    async def start(self) -> None:
        self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
        self._task = asyncio.create_task(self._listen())
        logger.info("EventConsumer started — listening on channel '%s'", EVENT_CHANNEL)

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._redis:
            await self._redis.aclose()
        logger.info("EventConsumer stopped")

    async def _listen(self) -> None:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(EVENT_CHANNEL)
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                await self._dispatch(message["data"])
        except asyncio.CancelledError:
            await pubsub.unsubscribe(EVENT_CHANNEL)
            raise

    async def _dispatch(self, raw: str) -> None:
        try:
            data = json.loads(raw)
            event = Event.model_validate(data)
        except Exception as exc:
            logger.error("Failed to parse event: %s — %s", raw, exc)
            return

        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            return

        for handler in handlers:
            try:
                await self._invoke_with_di(handler, event)
            except Exception as exc:
                logger.error(
                    "Handler %s failed for event %s: %s",
                    handler.__name__,
                    event.event_type,
                    exc,
                    exc_info=True,
                )

    async def _invoke_with_di(self, handler: Callable, event: Event) -> None:
        """
        Resolve the handler's dependencies using FastAPI's own DI machinery,
        exactly as it does for HTTP route handlers.

        We build a synthetic ASGI scope so that FastAPI's dependency resolver
        has a valid Request-like context to work with (needed for scoped
        dependencies such as DB sessions).
        """
        # Build a minimal ASGI scope that satisfies FastAPI's dependency resolver
        scope: Scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [],
            "app": self._app,
        }
        request = Request(scope)

        dependant = get_dependant(path="/", call=handler)

        # Inject the `event` parameter directly — it is not a Depends() dependency
        dependency_cache: dict[Any, Any] = {}
        solved = await solve_dependencies(
            request=request,
            dependant=dependant,
            dependency_overrides_provider=self._app,
        )

        kwargs = solved.values
        # Manually inject `event` if the handler declares it as a plain parameter
        if "event" in handler.__code__.co_varnames:
            kwargs["event"] = event

        await handler(**kwargs)
