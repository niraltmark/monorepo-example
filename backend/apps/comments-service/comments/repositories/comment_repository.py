from typing import Any

from comments.comment_model import CommentModel
from comments.repositories.base import AbstractRepository

class CommentRepository(AbstractRepository[CommentModel, dict, dict]):

    def get_by_id(self, entity_id: Any) -> CommentModel | None:
        try:
            return CommentModel.objects.get(pk=entity_id)
        except CommentModel.DoesNotExist:
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> list[CommentModel]:
        return list(CommentModel.objects.all()[skip : skip + limit])

    def get_all_with_total(self, skip: int = 0, limit: int = 100) -> tuple[list[CommentModel], int]:
        queryset = CommentModel.objects.filter(status=CommentModel.Status.ACTIVE)
        total = queryset.count()
        return list(queryset[skip : skip + limit]), total

    def get_by_todo_id(
        self, todo_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[CommentModel], int]:
        queryset = CommentModel.objects.filter(todo_id=todo_id, status=CommentModel.Status.ACTIVE)
        total = queryset.count()
        return list(queryset[skip : skip + limit]), total

    def get_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[CommentModel], int]:
        queryset = CommentModel.objects.filter(user_id=user_id, status=CommentModel.Status.ACTIVE)
        total = queryset.count()
        return list(queryset[skip : skip + limit]), total

    def create(self, data: dict) -> CommentModel:
        return CommentModel.objects.create(
            user_id=data["user_id"],
            todo_id=data["todo_id"],
            body=data["body"],
        )

    def update(self, entity_id: Any, data: dict) -> CommentModel | None:
        comment = self.get_by_id(entity_id)
        if not comment:
            return None
        for field, value in data.items():
            setattr(comment, field, value)
        comment.save()
        return comment

    def delete(self, entity_id: Any) -> bool:
        comment = self.get_by_id(entity_id)
        if not comment:
            return False
        comment.status = CommentModel.Status.DELETED
        comment.save(update_fields=["status", "updated_at"])
        return True
