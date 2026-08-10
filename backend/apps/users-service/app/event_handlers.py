"""
Event handlers for users-service.

These handlers are registered on the EventConsumer and are invoked when
events arrive from any service on the shared Redis channel.
Each handler receives a fully FastAPI-injected dependency graph — the same
as any route handler would.
"""

import logging

from fastapi import Depends

from app.services.user_service import UserService
from event_bus.consumer import EventConsumer
from event_bus.schemas import Event, TodoDeletedEvent

logger = logging.getLogger(__name__)


def register_handlers(consumer: EventConsumer) -> None:
    """Register all event handlers for users-service onto the consumer."""

    @consumer.on("todo.deleted")
    async def handle_todo_deleted(
        event: Event,
        user_service: UserService = Depends(UserService),
    ) -> None:
        """
        Example cross-service handler: when a todo is deleted,
        the users-service can react (e.g. update user stats, audit log).
        """
        todo_id = event.payload.get("todo_id")
        logger.info(
            "[users-service] Received todo.deleted event for todo_id=%s — "
            "could update user activity stats here.",
            todo_id,
        )

    @consumer.on("comment.created")
    async def handle_comment_created(
        event: Event,
        user_service: UserService = Depends(UserService),
    ) -> None:
        """
        Example: when a comment is created, users-service could
        update a comment-count denormalization or send a notification.
        """
        user_id = event.payload.get("user_id")
        logger.info(
            "[users-service] Received comment.created event from user_id=%s.",
            user_id,
        )
