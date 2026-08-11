"""
FastAPI dependency helpers for ContextService.

The primary injection pattern is:

    context_service: ContextService = Depends(ContextService)

This is all you need in route handlers and service constructors.
No factory function or Annotated wrapper required.

This module provides one additional guard for routes that must reject
unauthenticated requests without repeating the check inline:

    context_service: ContextService = Depends(require_authenticated)

``require_authenticated`` is itself a dependency that resolves a
``ContextService`` instance and raises HTTP 401 if the context has no user.
"""

from fastapi import Depends, HTTPException, status

from context_service.service import ContextService


def require_authenticated(
    context_service: ContextService = Depends(ContextService),
) -> ContextService:
    """
    FastAPI dependency that raises HTTP 401 if the request is not authenticated.
    Returns the ContextService instance so callers can still call .get() on it.

    Example:
        @router.delete("/{user_id}")
        async def delete_user(
            user_id: str,
            context_service: ContextService = Depends(require_authenticated),
        ) -> None:
            ctx = context_service.get()
            if ctx.user_id != user_id:
                raise HTTPException(status_code=403)
            ...
    """
    ctx = context_service.get()
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return context_service
