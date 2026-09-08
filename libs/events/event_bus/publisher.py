import json
import logging

import redis.asyncio as aioredis

from event_bus.schemas import Event

logger = logging.getLogger(__name__)

EVENT_CHANNEL = "domain_events"


class EventPublisher:
    """
    Publishes domain events to Redis Pub/Sub.

    Automatically embeds the current RequestContext into every outgoing event
    under the ``context`` key by reading from the injected ContextService.
    The EventConsumer on the receiving end restores this context onto the
    synthetic Request's state before invoking handlers, so ContextService.get()
    returns the correct user inside event handlers.

    Usage:
        publisher: EventPublisher = Depends(get_event_publisher)
        await publisher.publish(UserCreatedEvent(payload={...}))
    """

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    async def publish(self, event: Event, context_service=None) -> None:
        """
        Publish an event to the Redis channel.

        ``context_service`` is an optional ContextService instance. When
        provided (injected via the service layer), the current RequestContext
        is embedded into the message. When absent, an empty context is used.
        """
        context_data: dict = {}
        if context_service is not None:
            try:
                context_data = context_service.get().model_dump()
            except Exception:
                pass

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
