"""
ContextMiddleware
=================

FastAPI/Starlette middleware that populates the ContextService at the start
of every HTTP request and clears it when the response is sent.

Flow
----
1. Request arrives.
2. Middleware extracts the Bearer token from the Authorization header.
3. Token is decoded using the shared SECRET_KEY.
4. A RequestContext is built from the token claims and stored via ContextService.set().
5. The request proceeds through the rest of the stack (routes, services, repos).
6. On the way out, ContextService.clear() is called to avoid context leaks.

Anonymous requests (no token, or invalid token) receive an empty RequestContext
with is_authenticated == False. It is the route handler's responsibility to
reject unauthenticated requests if needed.

Usage
-----
In each FastAPI service's create_application():

    from context_service.middleware import ContextMiddleware

    app.add_middleware(ContextMiddleware, secret_key=settings.SECRET_KEY)
"""

import logging
from collections.abc import Callable

from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from context_service.models import RequestContext
from context_service.service import ContextService

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"


class ContextMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that resolves the current user from the JWT
    and stores it in ContextService for the duration of the request.
    """

    def __init__(self, app, secret_key: str) -> None:
        super().__init__(app)
        self._secret_key = secret_key

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        context = self._resolve_context(request)
        token = ContextService.set(context)
        try:
            response = await call_next(request)
        finally:
            # Restore previous context (important for test scenarios where
            # the same event loop reuses tasks across requests).
            ContextService._var.reset(token)
        return response

    def _resolve_context(self, request: Request) -> RequestContext:
        """
        Attempt to decode the Bearer token and build a RequestContext.
        Returns an anonymous context on any failure.
        """
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return RequestContext()

        raw_token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(raw_token, self._secret_key, algorithms=[ALGORITHM])
            return RequestContext(
                user_id=payload.get("sub"),
                username=payload.get("username"),
                email=payload.get("email"),
                is_active=payload.get("is_active", True),
                roles=payload.get("roles", []),
            )
        except JWTError:
            logger.debug("ContextMiddleware: invalid or expired JWT — anonymous context.")
            return RequestContext()
