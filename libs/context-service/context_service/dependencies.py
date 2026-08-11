"""
FastAPI dependency providers for ContextService.

Provides two injection styles:

1. Direct class injection (preferred for services):
       def __init__(self, context_service: ContextService = Depends(ContextService)):
           self._context = context_service

2. Shorthand for the current context object:
       async def my_route(ctx: RequestContext = Depends(get_current_context)):
           print(ctx.user_id)

3. Guard dependency that raises 401 for unauthenticated requests:
       async def my_route(ctx: RequestContext = Depends(require_authenticated)):
           ...
"""

from fastapi import Depends, HTTPException, status

from context_service.models import RequestContext
from context_service.service import ContextService


def get_current_context() -> RequestContext:
    """
    FastAPI dependency that returns the current RequestContext.
    The context was populated by ContextMiddleware at request start.
    """
    return ContextService.get()


def require_authenticated(
    context: RequestContext = Depends(get_current_context),
) -> RequestContext:
    """
    FastAPI dependency that raises HTTP 401 if the request is not authenticated.
    Use this instead of get_current_user in route handlers.

    Example:
        @router.get("/me")
        async def get_me(ctx: RequestContext = Depends(require_authenticated)):
            return {"user_id": ctx.user_id, "username": ctx.username}
    """
    if not context.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return context
