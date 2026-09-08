"""create todos table

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE todo_status AS ENUM ('pending', 'in_progress', 'done')")

    op.create_table(
        "todos",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "done", name="todo_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        # user_id is a plain string — no FK constraint, no cross-service coupling at DB level
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_todos_user_id", "todos", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_todos_user_id", table_name="todos")
    op.drop_table("todos")
    op.execute("DROP TYPE todo_status")
