"""
ContextService
==============

A request-scoped context store backed by Python's ``contextvars.ContextVar``.

Why ContextVar?
---------------
``ContextVar`` is the correct primitive for per-task isolated state in async
Python. Each asyncio Task (which maps to one HTTP request or one event message
dispatch) gets its own copy of the variable. Setting the context in one task
never bleeds into another — unlike a plain module-level global.

Usage
-----
Anywhere in the call stack (middleware, service, repository, event handler):

    from context_service import ContextService

    # Read
    ctx = ContextService.get()
    print(ctx.user_id)

    # Write (typically done only in middleware or EventConsumer)
    ContextService.set(RequestContext(user_id="abc", username="alice", email="alice@example.com"))

    # Clear (called at the end of a request/message to avoid leaks)
    ContextService.clear()
"""

from contextvars import ContextVar, Token
from typing import ClassVar

from context_service.models import RequestContext

# Module-level ContextVar — one instance shared across the entire process.
# Each asyncio Task sees its own isolated copy of this variable.
_context_var: ContextVar[RequestContext] = ContextVar(
    "request_context",
    default=RequestContext(),  # anonymous / empty context by default
)


class ContextService:
    """
    Static service for reading and writing the current request context.

    All methods are class-level so no instantiation is needed — call
    ``ContextService.get()`` from anywhere without dependency injection.
    However, it is also injectable via ``Depends(ContextService)`` if you
    prefer to keep the dependency explicit in your service constructors.
    """

    # Expose the underlying ContextVar for advanced use (e.g. copy_context)
    _var: ClassVar[ContextVar[RequestContext]] = _context_var

    @classmethod
    def get(cls) -> RequestContext:
        """
        Return the current request context for this asyncio task.
        Returns an anonymous RequestContext if none has been set.
        """
        return cls._var.get()

    @classmethod
    def set(cls, context: RequestContext) -> Token:
        """
        Set the request context for the current asyncio task.
        Returns the reset Token so callers can restore the previous value
        if needed (useful in tests or nested context scopes).
        """
        return cls._var.set(context)

    @classmethod
    def clear(cls) -> None:
        """
        Reset the context to the default anonymous state.
        Call this at the end of a request or message dispatch.
        """
        cls._var.set(RequestContext())

    @classmethod
    def set_from_dict(cls, data: dict) -> Token:
        """
        Convenience method to restore context from a serialised dict
        (e.g. extracted from an incoming event payload).
        """
        return cls.set(RequestContext.model_validate(data))
