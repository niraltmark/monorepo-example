from typing import Any

from pydantic import BaseModel


class RequestContext(BaseModel):
    """
    Immutable snapshot of the current request/message context.

    Carried through the entire call stack — HTTP middleware sets it,
    EventPublisher embeds it in outgoing messages, EventConsumer restores
    it before dispatching handlers.

    Fields
    ------
    user_id:    UUID string of the authenticated user (None for anonymous).
    username:   Display name of the authenticated user.
    email:      Email address of the authenticated user.
    is_active:  Whether the user account is active.
    roles:      List of role strings assigned to the user.
    extra:      Arbitrary key-value bag for service-specific metadata
                (e.g. correlation IDs, feature flags, tenant IDs).
    """

    user_id: str | None = None
    username: str | None = None
    email: str | None = None
    is_active: bool = True
    roles: list[str] = []
    extra: dict[str, Any] = {}

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None

    model_config = {"frozen": True}
