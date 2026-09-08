from typing import Any

from comments.models import Comment
from comments.repositories.base import AbstractRepository


class CommentRepository(AbstractRepository[Comment, dict, dict]):
    """
    Concrete repository for Comment persistence operations.
    All database access is encapsulated here — services never touch the ORM directly.
    Uses Django's ORM synchronously (standard Django pattern).
    """

    def get_by_id(self, entity_id: Any) -> Comment | None:
        try:
            return Comment.objects.get(pk=entity_id)
        except Comment.DoesNotExist:
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Comment]:
        return list(Comment.objects.all()[skip : skip + limit])

    def get_all_with_total(self, skip: int = 0, limit: int = 100) -> tuple[list[Comment], int]:
        """Return paginated comments and the total unpaginated count."""
        queryset = Comment.objects.filter(status=Comment.Status.ACTIVE)
        total = queryset.count()
        return list(queryset[skip : skip + limit]), total

    def get_by_todo_id(
        self, todo_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Comment], int]:
        queryset = Comment.objects.filter(todo_id=todo_id, status=Comment.Status.ACTIVE)
        total = queryset.count()
        return list(queryset[skip : skip + limit]), total

    def get_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Comment], int]:
        queryset = Comment.objects.filter(user_id=user_id, status=Comment.Status.ACTIVE)
        total = queryset.count()
        return list(queryset[skip : skip + limit]), total

    def create(self, data: dict) -> Comment:
        return Comment.objects.create(
            user_id=data["user_id"],
            todo_id=data["todo_id"],
            body=data["body"],
        )

    def update(self, entity_id: Any, data: dict) -> Comment | None:
        comment = self.get_by_id(entity_id)
        if not comment:
            return None
        for field, value in data.items():
            setattr(comment, field, value)
        comment.save()
        return comment

    def delete(self, entity_id: Any) -> bool:
        """Soft-delete by setting status to DELETED."""
        comment = self.get_by_id(entity_id)
        if not comment:
            return False
        comment.status = Comment.Status.DELETED
        comment.save(update_fields=["status", "updated_at"])
        return True
