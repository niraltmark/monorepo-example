# This file is intentionally minimal.
#
# Authentication and context resolution are now handled by ContextMiddleware
# (from libs/context-service), which decodes the JWT on every request and
# stores the user details in ContextService (a ContextVar-backed store).
#
# Route handlers that require an authenticated user should use:
#
#     from context_service.dependencies import require_authenticated
#     from context_service.models import RequestContext
#
#     async def my_route(context: RequestContext = Depends(require_authenticated)):
#         user_id = context.user_id
#
# The old get_current_user() function has been removed — it performed a DB
# round-trip on every authenticated request. ContextService reads from an
# in-process ContextVar, which is zero-cost and requires no DB access.
