from rest_framework.exceptions import NotFound, ValidationError

from comments.models import Comment
from comments.repositories.comment_repository import CommentRepository

class CommentService:

    def __init__(self, comment_repository: CommentRepository | None = None) -> None:
        self._repository = comment_repository or CommentRepository()

    def create_comment(self, user_id: str, todo_id: str, body: str) -> Comment:
        if not body.strip():
            raise ValidationError({"body": "Comment body cannot be empty."})
        return self._repository.create(
            {"user_id": str(user_id), "todo_id": str(todo_id), "body": body.strip()}
        )

    def get_comment(self, comment_id: str) -> Comment:
        comment = self._repository.get_by_id(comment_id)
        if not comment or comment.status == Comment.Status.DELETED:
            raise NotFound("Comment not found.")
        return comment

    def list_comments(self, skip: int = 0, limit: int = 100) -> tuple[list[Comment], int]:
        return self._repository.get_all_with_total(skip=skip, limit=limit)

    def list_comments_by_todo(
        self, todo_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Comment], int]:
        return self._repository.get_by_todo_id(todo_id, skip=skip, limit=limit)

    def list_comments_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[Comment], int]:
        return self._repository.get_by_user_id(user_id, skip=skip, limit=limit)

    def update_comment(self, comment_id: str, body: str) -> Comment:
        if not body.strip():
            raise ValidationError({"body": "Comment body cannot be empty."})
        comment = self._repository.update(comment_id, {"body": body.strip()})
        if not comment or comment.status == Comment.Status.DELETED:
            raise NotFound("Comment not found.")
        return comment

    def delete_comment(self, comment_id: str) -> None:
        self.get_comment(comment_id)
        if not self._repository.delete(comment_id):
            raise NotFound("Comment not found.")
