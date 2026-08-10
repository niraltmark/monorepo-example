from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TodoStatus = TodoStatus.PENDING
    due_date: datetime | None = None


class TodoCreate(TodoBase):
    user_id: str = Field(..., description="UUID of the owning user (from users-service)")


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TodoStatus | None = None
    due_date: datetime | None = None
    is_completed: bool | None = None


class TodoRead(TodoBase):
    id: str
    user_id: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TodoListResponse(BaseModel):
    items: list[TodoRead]
    total: int
    skip: int
    limit: int
