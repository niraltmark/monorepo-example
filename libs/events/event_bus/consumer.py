"""
EventConsumer — NestJS-style microservice bootstrap for FastAPI.

The problem
-----------
Redis Pub/Sub messages arrive on a background asyncio task, completely
outside the normal HTTP request/response cycle. FastAPI's dependency
injection is designed around requests, so there is no built-in way to
call ``Depends(MyService)`` from a background task.

The solution — "mini app" context
----------------------------------
We replicate what NestJS does with its microservice ``createMicroservice`` /
``app.init()`` pattern:

1. Each @consumer.on decorated function declares its dependencies exactly
   like a route handler:

       @consumer.on("user.created")
       async def handle_user_created(
           event: Event,
           todo_service: TodoService = Depends(TodoService),
       ) -> None:
           ...

2. When a message arrives, EventConsumer calls ``solve_dependencies`` with
   a synthetic Request-like scope so FastAPI resolves the full DI graph
   (including DB sessions, repositories, services) just as it would for a
   real HTTP request.

Context propagation
-------------------
Every published event carries a ``context`` field containing the serialised
RequestContext of the user who triggered the original action. Before invoking
each handler, EventConsumer restores that context via ContextService.set() so
that ContextService.get() returns the correct user inside the handler — exactly
as it does inside HTTP route handlers.
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
from starlette.types import Scope

from event_bus.publisher import EVENT_CHANNEL
from event_bus.schemas import Event

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Subscribes to the Redis Pub/Sub channel and dispatches incoming events
    to registered handlers using FastAPI's dependency injection machinery.
    Restores the RequestContext from the event payload before each dispatch.
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
            # Extract and remove the context field before validating the Event
            context_data: dict[str, Any] = data.pop("context", {})
            event = Event.model_validate(data)
        except Exception as exc:
            logger.error("Failed to parse event: %s — %s", raw, exc)
            return

        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            return

        for handler in handlers:
            try:
                await self._invoke_with_di(handler, event, context_data)
            except Exception as exc:
                logger.error(
                    "Handler %s failed for event %s: %s",
                    handler.__name__,
                    event.event_type,
                    exc,
                    exc_info=True,
                )

    async def _invoke_with_di(
        self, handler: Callable, event: Event, context_data: dict[str, Any]
    ) -> None:
        """
        Restore the RequestContext from the event payload, then resolve
        the handler's dependencies using FastAPI's own DI machinery.

        Context restoration
        -------------------
        We call ContextService.set_from_dict(context_data) before invoking
        the handler. Because each asyncio Task has its own ContextVar copy,
        this is safe — the restored context is visible only within this
        handler invocation and does not affect other concurrent tasks.
        The ContextVar token is reset after the handler completes.
        """
        # ── 1. Restore RequestContext from the event payload ──────────────────
        reset_token = None
        try:
            from context_service.service import ContextService
            reset_token = ContextService().set_from_dict(context_data)
        except ImportError:
            pass  # context_service not available — skip silently

        try:
            # ── 2. Build a minimal ASGI scope for FastAPI's DI resolver ───────
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
            solved = await solve_dependencies(
                request=request,
                dependant=dependant,
                dependency_overrides_provider=self._app,
            )

            kwargs = solved.values
            # Inject `event` directly — it is not a Depends() dependency
            if "event" in handler.__code__.co_varnames:
                kwargs["event"] = event

            await handler(**kwargs)

        finally:
            # ── 3. Restore the previous ContextVar state ──────────────────────
            if reset_token is not None:
                try:
                    from context_service.service import ContextService
                    ContextService._var.reset(reset_token)  # reset via class-level _var
                except ImportError:
                    pass
