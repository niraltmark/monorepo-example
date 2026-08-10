"""
Event handlers for users-service.

Each handler is registered with @consumer.on("<event_type>") and receives:
  - event:        the raw Event object (payload, event_id, occurred_at, etc.)
  - user_service: a fully FastAPI-injected UserService instance
                  (which itself has a DB session, repository, and publisher)

This is the NestJS microservice pattern replicated in FastAPI:
the EventConsumer calls FastAPI's own solve_dependencies() to build the
dependency graph for each handler, exactly as it does for HTTP route handlers.
"""

import logging

from fastapi import Depends

from app.services.user_service import UserService
from event_bus.consumer import EventConsumer
from event_bus.schemas import Event

logger = logging.getLogger(__name__)


def register_handlers(consumer: EventConsumer) -> None:
    """Register all event handlers for users-service onto the consumer."""

    # ── Example 1: Audit / activity tracking ─────────────────────────────────
    # When a todo is deleted, record that in the user's activity log.
    # Here we simply fetch the user to confirm they still exist and log it,
    # but in a real system you would write to an audit_log table.
    @consumer.on("todo.deleted")
    async def handle_todo_deleted(
        event: Event,
        user_service: UserService = Depends(UserService),
    ) -> None:
        """
        React to a todo being deleted by looking up the owning user
        and logging the activity. Demonstrates reading from the DB
        inside a consumer handler using a fully injected service.

        Payload shape: {"todo_id": "<uuid>"}
        Note: users-service does not know the user_id from this event,
        so this example shows how you would handle partial payloads.
        """
        todo_id = event.payload.get("todo_id")
        logger.info(
            "[users-service] todo.deleted received — todo_id=%s deleted at %s (event_id=%s). "
            "Would write to audit log here.",
            todo_id,
            event.occurred_at.isoformat(),
            event.event_id,
        )

    # ── Example 2: Cross-service notification trigger ─────────────────────────
    # When a comment is created, look up the user who wrote it and
    # log their details — simulating a notification dispatch.
    @consumer.on("comment.created")
    async def handle_comment_created(
        event: Event,
        user_service: UserService = Depends(UserService),
    ) -> None:
        """
        When a comment is created, fetch the author's profile and
        simulate sending a notification to the todo owner.

        Payload shape: {"comment_id": "<uuid>", "user_id": "<uuid>", "todo_id": "<uuid>"}
        """
        user_id = event.payload.get("user_id")
        if not user_id:
            logger.warning("[users-service] comment.created event missing user_id — skipping.")
            return

        try:
            user = await user_service.get_user(user_id)
            logger.info(
                "[users-service] comment.created by user '%s' (%s) on todo_id=%s — "
                "would dispatch notification here (event_id=%s).",
                user.username,
                user.email,
                event.payload.get("todo_id"),
                event.event_id,
            )
        except Exception:
            # User may have been deleted between the event being published and now.
            logger.debug(
                "[users-service] user_id=%s not found when handling comment.created — skipping.",
                user_id,
            )
