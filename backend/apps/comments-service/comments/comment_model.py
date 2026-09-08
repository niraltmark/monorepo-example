import uuid

from django.db import models


class CommentModel(models.Model):
    """
    Comment model.

    - user_id:  UUID string referencing a user in users-service.
    - todo_id:  UUID string referencing a todo in todos-service.

    No foreign key constraints — services are fully decoupled at the DB level.
    Cross-service references are plain VARCHAR fields containing UUIDs.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DELETED = "deleted", "Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Loose references — no FK, no DB-level constraint
    user_id = models.CharField(max_length=36, db_index=True)
    todo_id = models.CharField(max_length=36, db_index=True)

    body = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments_comment"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"CommentModel({self.id}) by user={self.user_id} on todo={self.todo_id}"
