from app.main import create_app
from fastapi.routing import APIRoute


def test_create_app_routes_exist():
    app = create_app()
    paths = {r.path for r in app.router.routes if isinstance(r, APIRoute)}
    assert "/health" in paths
    assert "/plan_trip" in paths
    # runs path includes param
    assert any(p.startswith("/runs/") for p in paths)
