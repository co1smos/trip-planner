import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.store._test_fakes import FakeRedis


@pytest.mark.anyio
async def test_plan_trip_and_get_run(monkeypatch):
    fake = FakeRedis()

    import app.api.routes_trip as mod
    monkeypatch.setattr(mod, "get_redis", lambda settings: fake)
    monkeypatch.setattr(uuid, "uuid4", lambda: type("U", (), {"hex": "rid"})())

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create run
        resp = await ac.post("/plan_trip", json={"query": "go tokyo", "constraints": {"days": 5}})
        assert resp.status_code == 200
        body = resp.json()
        assert body["run_id"] == "rid"
        assert body["status"] == "CREATED"

        # Get run
        resp2 = await ac.get("/runs/rid")
        assert resp2.status_code == 200
        run = resp2.json()
        assert run["run_id"] == "rid"
        assert run["status"] == "CREATED"
        assert run["request"]["query"] == "go tokyo"
        assert run["request"]["constraints"]["days"] == 5


@pytest.mark.anyio
async def test_get_run_404(monkeypatch):
    fake = FakeRedis()

    import app.api.routes_trip as mod
    monkeypatch.setattr(mod, "get_redis", lambda settings: fake)

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/runs/not-exist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "run not found"
