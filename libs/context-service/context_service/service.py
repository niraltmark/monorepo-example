from fastapi.requests import Request

from context_service.models import RequestContext

_ANONYMOUS = RequestContext()


class ContextService:
    def __init__(self, request: Request) -> None:
        self._request = request

    def get(self) -> RequestContext:
        return getattr(self._request.state, "context", _ANONYMOUS)

    def set(self, context: RequestContext) -> None:
        self._request.state.context = context
