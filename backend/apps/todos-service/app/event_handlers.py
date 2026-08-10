"""
Event handlers for todos-service.

Each handler is registered with @consumer.on("<event_type>") and receives:
  - event:        the raw Event object (payload, event_id, occurred_at, etc.)
  - todo_service: a fully FastAPI-injected TodoService instance
                  (which itself has a DB session, repository, and publisher)

This is the NestJS microservice pattern replicated in FastAPI:
the EventConsumer calls FastAPI's own solve_dependencies() to build the
dependency graph for each handler, exactly as it does for HTTP route handlers.
"""

import logging

from fastapi import Depends

from app.schemas.todo import TodoUpdate
from app.services.todo_service import TodoService
from event_bus.consumer import EventConsumer
from event_bus.schemas import Event

logger = logging.getLogger(__name__)


def register_handlers(consumer: EventConsumer) -> None:
    """Register all event handlers for todos-service onto the consumer."""

    # ── Example 1: Cross-service cascade ─────────────────────────────────────
    # When a user is deleted in users-service, hard-delete all their todos here.
    # No shared DB, no FK — pure event-driven coordination.
    @consumer.on("user.deleted")
    async def handle_user_deleted(
        event: Event,
        todo_service: TodoService = Depends(TodoService),
    ) -> None:
        """
        Cascade-delete all todos belonging to a deleted user.

        Payload shape: {"user_id": "<uuid>"}
        """
        user_id = event.payload.get("user_id")
        if not user_id:
            logger.warning("[todos-service] user.deleted event missing user_id — skipping.")
            return

        logger.info("[todos-service] user.deleted received for user_id=%s — deleting their todos.", user_id)

        response = await todo_service.list_todos_by_user(user_id)
        deleted_count = 0
        for todo in response.items:
            try:
                await todo_service.delete_todo(todo.id)
                deleted_count += 1
            except Exception as exc:
                logger.error("[todos-service] Failed to delete todo_id=%s: %s", todo.id, exc)

        logger.info(
            "[todos-service] Deleted %d todo(s) for user_id=%s (event_id=%s).",
            deleted_count,
            user_id,
            event.event_id,
        )

    # ── Example 2: Denormalization / status update ────────────────────────────
    # When a comment is created on a todo, mark that todo as "in_progress"
    # if it is still "pending" — a simple business rule driven by events.
    @consumer.on("comment.created")
    async def handle_comment_created(
        event: Event,
        todo_service: TodoService = Depends(TodoService),
    ) -> None:
        """
        When a comment is added to a todo that is still pending,
        automatically advance its status to in_progress.

        Payload shape: {"comment_id": "<uuid>", "todo_id": "<uuid>", "user_id": "<uuid>"}
        """
        todo_id = event.payload.get("todo_id")
        if not todo_id:
            logger.warning("[todos-service] comment.created event missing todo_id — skipping.")
            return

        try:
            todo = await todo_service.get_todo(todo_id)
        except Exception:
            # Todo may not exist in this service — that is fine, ignore silently.
            logger.debug("[todos-service] todo_id=%s not found — skipping status update.", todo_id)
            return

        if todo.status == "pending":
            await todo_service.update_todo(todo_id, TodoUpdate(status="in_progress"))
            logger.info(
                "[todos-service] todo_id=%s advanced from pending → in_progress "
                "because a comment was added (event_id=%s).",
                todo_id,
                event.event_id,
            )
        else:
            logger.debug(
                "[todos-service] todo_id=%s already has status=%s — no update needed.",
                todo_id,
                todo.status,
            )
