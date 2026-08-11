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

Dependency injection
--------------------
``ContextService`` is designed to be used directly with FastAPI's ``Depends``:

    def __init__(self, context_service: ContextService = Depends(ContextService)):
        self._context = context_service

    async def some_method(self) -> None:
        ctx = self._context.get()
        print(ctx.user_id)

FastAPI instantiates ``ContextService()`` by calling its ``__init__`` (which
takes no arguments), so no factory function or Annotated wrapper is needed.

The underlying ``ContextVar`` is module-level, so all instances share the same
storage — ``ContextService()`` is effectively a zero-cost view over the same
per-task slot regardless of how many times it is instantiated per request.
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
    Injectable service for reading and writing the current request context.

    Instantiate via FastAPI's dependency injection:

        class MyService:
            def __init__(
                self,
                context_service: ContextService = Depends(ContextService),
            ) -> None:
                self._context = context_service

        # In a route handler:
        @router.get("/me")
        async def get_me(
            context_service: ContextService = Depends(ContextService),
        ) -> dict:
            ctx = context_service.get()
            if not ctx.is_authenticated:
                raise HTTPException(status_code=401)
            return {"user_id": ctx.user_id}
    """

    # Expose the underlying ContextVar for the middleware and consumer
    # which need to set/reset the token directly.
    _var: ClassVar[ContextVar[RequestContext]] = _context_var

    def get(self) -> RequestContext:
        """
        Return the current request context for this asyncio task.
        Returns an anonymous RequestContext if none has been set.
        """
        return self._var.get()

    def set(self, context: RequestContext) -> Token:
        """
        Set the request context for the current asyncio task.
        Returns the reset Token so callers can restore the previous value.
        """
        return self._var.set(context)

    def clear(self) -> None:
        """Reset the context to the default anonymous state."""
        self._var.set(RequestContext())

    def set_from_dict(self, data: dict) -> Token:
        """
        Convenience method to restore context from a serialised dict
        (e.g. extracted from an incoming event payload).
        """
        return self.set(RequestContext.model_validate(data))
