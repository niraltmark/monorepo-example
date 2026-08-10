import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Event(BaseModel):
    """
    Base class for all domain events published across the system.

    Every event carries:
      - event_id:    unique identifier for this specific event occurrence
      - event_type:  dot-namespaced string, e.g. "user.created", "todo.deleted"
      - service:     name of the originating service
      - occurred_at: UTC timestamp of when the event was raised
      - payload:     arbitrary domain data (subclasses define typed payloads)
    """

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    service: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)


# ── User events ───────────────────────────────────────────────────────────────

class UserCreatedEvent(Event):
    event_type: str = "user.created"
    service: str = "users-service"


class UserUpdatedEvent(Event):
    event_type: str = "user.updated"
    service: str = "users-service"


class UserDeletedEvent(Event):
    event_type: str = "user.deleted"
    service: str = "users-service"


# ── Todo events ───────────────────────────────────────────────────────────────

class TodoCreatedEvent(Event):
    event_type: str = "todo.created"
    service: str = "todos-service"


class TodoUpdatedEvent(Event):
    event_type: str = "todo.updated"
    service: str = "todos-service"


class TodoDeletedEvent(Event):
    event_type: str = "todo.deleted"
    service: str = "todos-service"


# ── Comment events ────────────────────────────────────────────────────────────

class CommentCreatedEvent(Event):
    event_type: str = "comment.created"
    service: str = "comments-service"


class CommentUpdatedEvent(Event):
    event_type: str = "comment.updated"
    service: str = "comments-service"


class CommentDeletedEvent(Event):
    event_type: str = "comment.deleted"
    service: str = "comments-service"
