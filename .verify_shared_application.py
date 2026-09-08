from __future__ import annotations

import importlib

main_module = importlib.import_module("app.main")
application = main_module.app

assert application.state.database_session_manager is not None
assert any(route.path == "/health" for route in application.routes)
assert any(route.path.startswith("/api/v1/") for route in application.routes)
print(f"{application.title}: shared application and database wiring verified")
