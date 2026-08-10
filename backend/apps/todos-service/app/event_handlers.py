"""
Event handlers for todos-service.

Handlers are invoked with a fully FastAPI-injected TodoService instance
via the EventConsumer's DI bootstrap — no manual wiring needed.
"""

import logging

from fastapi import Depends

from app.services.todo_service import TodoService
from event_bus.consumer import EventConsumer
from event_bus.schemas import Event

logger = logging.getLogger(__name__)


def register_handlers(consumer: EventConsumer) -> None:
    """Register all event handlers for todos-service onto the consumer."""

    @consumer.on("user.deleted")
    async def handle_user_deleted(
        event: Event,
        todo_service: TodoService = Depends(TodoService),
    ) -> None:
        """
        When a user is deleted, soft-delete or reassign all their todos.
        This demonstrates cross-service reaction without a shared DB or FK.
        """
        user_id = event.payload.get("user_id")
        logger.info(
            "[todos-service] Received user.deleted for user_id=%s — "
            "could cascade-delete or archive their todos here.",
            user_id,
        )

    @consumer.on("comment.created")
    async def handle_comment_created(
        event: Event,
        todo_service: TodoService = Depends(TodoService),
    ) -> None:
        """
        When a comment is created, todos-service could update a
        comment-count denormalization field on the todo.
        """
        todo_id = event.payload.get("todo_id")
        logger.info(
            "[todos-service] Received comment.created for todo_id=%s — "
            "could increment comment_count here.",
            todo_id,
        )
