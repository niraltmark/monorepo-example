"""
FastAPI dependency providers for the event bus.

Each service calls `init_event_bus(app, redis_url)` in its lifespan,
which stores the Redis client and EventPublisher on `app.state`.
Route handlers and service classes then declare:

    publisher: EventPublisher = Depends(get_event_publisher)

and FastAPI resolves it automatically.
"""

import redis.asyncio as aioredis
from fastapi import Depends, FastAPI, Request

from event_bus.publisher import EventPublisher


def init_event_bus(app: FastAPI, redis_url: str) -> aioredis.Redis:
    """
    Create and store the Redis client on app.state.
    Call this inside the service's lifespan before `yield`.
    Returns the Redis client so the caller can also create an EventConsumer.
    """
    redis_client = aioredis.from_url(redis_url, decode_responses=True)
    app.state.redis = redis_client
    app.state.event_publisher = EventPublisher(redis_client)
    return redis_client


async def get_event_publisher(request: Request) -> EventPublisher:
    """
    FastAPI dependency that returns the shared EventPublisher from app.state.
    Inject with: publisher: EventPublisher = Depends(get_event_publisher)
    """
    return request.app.state.event_publisher
