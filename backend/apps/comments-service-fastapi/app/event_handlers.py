
import logging

from fastapi import Depends

from app.services.comment_service import CommentService
from event_bus.consumer import EventConsumer
from event_bus.schemas import Event

logger = logging.getLogger(__name__)

def register_handlers(consumer: EventConsumer) -> None:

    @consumer.on("todo.deleted")
    async def handle_todo_deleted(
        event: Event,
        comment_service: CommentService = Depends(CommentService),
    ) -> None:
        todo_id = event.payload.get("todo_id")
        logger.info(
            "[comments-service] Received todo.deleted for todo_id=%s — "
            "soft-deleting all comments on this todo.",
            todo_id,
        )
        response = await comment_service.list_comments_by_todo(todo_id)
        for comment in response.items:
            await comment_service.delete_comment(comment.id)
        logger.info(
            "[comments-service] Soft-deleted %d comment(s) for todo_id=%s.",
            len(response.items),
            todo_id,
        )

    @consumer.on("user.deleted")
    async def handle_user_deleted(
        event: Event,
        comment_service: CommentService = Depends(CommentService),
    ) -> None:
        user_id = event.payload.get("user_id")
        logger.info(
            "[comments-service] Received user.deleted for user_id=%s — "
            "soft-deleting all their comments.",
            user_id,
        )
        response = await comment_service.list_comments_by_user(user_id)
        for comment in response.items:
            await comment_service.delete_comment(comment.id)
        logger.info(
            "[comments-service] Soft-deleted %d comment(s) for user_id=%s.",
            len(response.items),
            user_id,
        )
