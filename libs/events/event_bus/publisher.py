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

    Designed to be used as a FastAPI dependency:

        async def my_route(publisher: EventPublisher = Depends(get_event_publisher)):
            await publisher.publish(UserCreatedEvent(payload={...}))

    The publisher is a thin wrapper — it serialises the event to JSON and
    publishes it to the shared Redis channel. It holds no state beyond the
    Redis connection, so it is safe to share across requests.
    """

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    async def publish(self, event: Event) -> None:
        message = event.model_dump_json()
        await self._redis.publish(EVENT_CHANNEL, message)
        logger.debug("Published event: %s (id=%s)", event.event_type, event.event_id)
