"""
ContextMiddleware
=================

FastAPI/Starlette middleware that sets ``request.state.context`` at the
start of every HTTP request.

Flow
----
1. Request arrives.
2. Middleware decodes the Bearer JWT from the Authorization header.
3. Builds a ``RequestContext`` from the token claims.
4. Stores it as ``request.state.context``.
5. The request proceeds — route handlers, services, and repositories
   can all read the context via ``ContextService.get()``.

Anonymous requests (no token or invalid token) receive an empty
``RequestContext`` with ``is_authenticated == False``.

Usage
-----
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

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"


class ContextMiddleware(BaseHTTPMiddleware):
    """
    Sets ``request.state.context`` from the JWT on every HTTP request.
    No ContextVar, no token management — just a plain attribute on the
    Starlette Request state object.
    """

    def __init__(self, app, secret_key: str) -> None:
        super().__init__(app)
        self._secret_key = secret_key

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request.state.context = self._resolve_context(request)
        return await call_next(request)

    def _resolve_context(self, request: Request) -> RequestContext:
        """
        Decode the Bearer token and build a RequestContext.
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
