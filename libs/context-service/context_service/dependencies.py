"""
FastAPI dependency helpers for ContextService.

The primary injection pattern is simply:

    context_service: ContextService = Depends(ContextService)

This module provides one additional guard for routes that must reject
unauthenticated requests:

    context_service: ContextService = Depends(require_authenticated)

``require_authenticated`` resolves a ``ContextService`` instance, checks
``context_service.get().is_authenticated``, and raises HTTP 401 if the
request carries no valid JWT. It returns the ``ContextService`` instance
so callers can still call ``.get()`` on it.
"""

from fastapi import Depends, HTTPException, status

from context_service.service import ContextService


def require_authenticated(
    context_service: ContextService = Depends(ContextService),
) -> ContextService:
    """
    FastAPI dependency that raises HTTP 401 if the request is not authenticated.

    Example:
        @router.get("/me")
        async def get_me(
            context_service: ContextService = Depends(require_authenticated),
            user_service: UserService = Depends(UserService),
        ) -> UserRead:
            ctx = context_service.get()
            return await user_service.get_user(ctx.user_id)
    """
    if not context_service.get().is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return context_service
