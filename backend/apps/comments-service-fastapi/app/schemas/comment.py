from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CommentStatus(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class CommentCreate(BaseModel):
    user_id: str = Field(..., max_length=36)
    todo_id: str = Field(..., max_length=36)
    body: str = Field(..., min_length=1, max_length=5000)


class CommentUpdate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class CommentRead(BaseModel):
    id: str
    user_id: str
    todo_id: str
    body: str
    status: CommentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    items: list[CommentRead]
    total: int
    skip: int
    limit: int
