from app.main import create_app


def test_create_app_routes_exist():
    app = create_app()
    paths = {r.path for r in app.router.routes}
    assert "/health" in paths
    assert "/plan_trip" in paths
    # runs path includes param
    assert any(p.startswith("/runs/") for p in paths)
