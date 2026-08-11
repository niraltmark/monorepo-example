"""
ContextService
==============

A request-scoped context service backed by FastAPI's ``Request`` object.

Design
------
Rather than a ``ContextVar``, context is stored directly on
``request.state.context`` — the standard FastAPI/Starlette pattern for
attaching per-request data in middleware. ``ContextService`` depends on
``Request`` via FastAPI's built-in ``Depends(Request)`` mechanism, which
means:

- No ``ContextVar`` management needed.
- Works identically for HTTP route handlers and event consumer handlers,
  because the ``EventConsumer`` already builds a synthetic ``Request``
  object before calling ``solve_dependencies`` — it just needs to set
  ``request.state.context`` on that synthetic request.
- Thread-safe and async-safe by construction — each request/message has
  its own ``Request`` instance.

Usage
-----
Inject via ``Depends(ContextService)`` anywhere in the DI graph:

    class TodoService:
        def __init__(
            self,
            context_service: ContextService = Depends(ContextService),
        ) -> None:
            self._context = context_service

    async def create_todo(self, data: TodoCreate) -> TodoRead:
        ctx = self._context.get()
        print(ctx.user_id)   # set by ContextMiddleware for HTTP requests
                              # set by EventConsumer for event handlers
"""

from fastapi import Depends
from fastapi.requests import Request

from context_service.models import RequestContext

_ANONYMOUS = RequestContext()


class ContextService:
    """
    Injectable service that reads the current ``RequestContext`` from
    ``request.state.context``.

    ``ContextMiddleware`` sets ``request.state.context`` at the start of
    every HTTP request. ``EventConsumer`` sets it on the synthetic Request
    before invoking each event handler. All other code simply calls
    ``context_service.get()``.
    """

    def __init__(self, request: Request = Depends()) -> None:
        self._request = request

    def get(self) -> RequestContext:
        """
        Return the current RequestContext.
        Returns an anonymous RequestContext if none has been set
        (e.g. health-check endpoints with no Authorization header).
        """
        return getattr(self._request.state, "context", _ANONYMOUS)

    def set(self, context: RequestContext) -> None:
        """
        Set the RequestContext on the current request.
        Normally called only by ContextMiddleware and EventConsumer.
        """
        self._request.state.context = context
