from httpx import AsyncClient

from app.main import create_app
from app.store._test_fakes import FakeRedis


async def test_health_redis_ok(monkeypatch):
    import app.api.routes_health as mod
    monkeypatch.setattr(mod, "get_redis", lambda settings: FakeRedis(ping_ok=True))

    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/health")
        data = resp.json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert data["redis"] == "ok"


async def test_health_redis_down(monkeypatch):
    import app.api.routes_health as mod
    monkeypatch.setattr(mod, "get_redis", lambda settings: FakeRedis(ping_ok=False))

    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/health")
        data = resp.json()
        assert resp.status_code == 200
        assert data["ok"] is False
        assert data["redis"] == "down"
