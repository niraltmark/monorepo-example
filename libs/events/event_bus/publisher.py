import json
import logging

import redis.asyncio as aioredis

from event_bus.schemas import Event

logger = logging.getLogger(__name__)

# Redis channel name — all services publish to and subscribe from this channel.
EVENT_CHANNEL = "domain_events"


class EventPublisher:
    """
    Publishes domain events to Redis Pub/Sub.

    Automatically embeds the current RequestContext (from ContextService)
    into every outgoing event under the ``context`` key. This allows the
    EventConsumer on the receiving end to restore the context before
    invoking handlers, so ContextService.get() returns the correct user
    inside event handlers — exactly as it does inside HTTP route handlers.

    Designed to be used as a FastAPI dependency:

        async def my_route(publisher: EventPublisher = Depends(get_event_publisher)):
            await publisher.publish(UserCreatedEvent(payload={...}))
    """

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    async def publish(self, event: Event) -> None:
        # Lazily import to avoid a hard dependency from event_bus → context_service
        # in environments where context_service is not on the path.
        try:
            from context_service.service import ContextService
            ctx = ContextService.get()
            context_data = ctx.model_dump()
        except ImportError:
            context_data = {}

        # Embed context into the serialised message as a top-level field.
        # We serialise manually so we can inject context without mutating the event.
        message_dict = json.loads(event.model_dump_json())
        message_dict["context"] = context_data
        message = json.dumps(message_dict)

        await self._redis.publish(EVENT_CHANNEL, message)
        logger.debug(
            "Published event: %s (id=%s, user_id=%s)",
            event.event_type,
            event.event_id,
            context_data.get("user_id"),
        )
