
import logging

from fastapi import Depends

from app.services.user_service import UserService
from event_bus.consumer import EventConsumer
from event_bus.schemas import Event

logger = logging.getLogger(__name__)

def register_handlers(consumer: EventConsumer) -> None:

    @consumer.on("todo.deleted")
    async def handle_todo_deleted(
        event: Event,
        user_service: UserService = Depends(UserService),
    ) -> None:
        todo_id = event.payload.get("todo_id")
        logger.info(
            "[users-service] todo.deleted received — todo_id=%s deleted at %s (event_id=%s). "
            "Would write to audit log here.",
            todo_id,
            event.occurred_at.isoformat(),
            event.event_id,
        )

    @consumer.on("comment.created")
    async def handle_comment_created(
        event: Event,
        user_service: UserService = Depends(UserService),
    ) -> None:
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
            logger.debug(
                "[users-service] user_id=%s not found when handling comment.created — skipping.",
                user_id,
            )
