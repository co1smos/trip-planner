import uuid

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.store._test_fakes import FakeRedis


@pytest.mark.anyio
async def test_post_plan_trip_returns_run_id_only_and_background_completes(monkeypatch):
    fake = FakeRedis()

    import app.api.routes_trip as mod

    # Caveat: please be careful to remove this mock since this is pretty buggy
    monkeypatch.setattr(mod, "get_redis", lambda settings: fake)
    monkeypatch.setattr(uuid, "uuid4", lambda: type("U", (), {"hex": "rid"})())

    # Patch run_workflow to a sync stub so BackgroundTasks runs deterministically.
    # from app.store.run_store import RunStore
    # from app.config import get_settings

    # async def stub_run_workflow(self, run_id: str) -> None:
    #     settings = get_settings()
    #     store = RunStore(fake, ttl_s=settings.RUN_TTL_S)
    #     # write final result
    #     # run_store methods are async; but we can do direct JSON patch by reusing internal storage:
    #     # easiest: load JSON record from fake redis and overwrite. Keep it simple:
    #     import json as _json

    #     key = f"run:{run_id}"
    #     raw_record = fake.raw_get(key)
    #     assert raw_record is not None
    #     data = _json.loads(raw_record)
    #     data["status"] = "SUCCEEDED"
    #     data["result"] = {"message": "done", "run_id": run_id}
    #     fake.raw_set_json(key, data)

    #     state_key = f"state:{run_id}"
    #     raw_state = fake.raw_get(state_key)
    #     assert raw_state is not None

    # monkeypatch.setattr("app.api.routes_trip.WorkflowRunner.run_workflow", stub_run_workflow)

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/plan_trip", json={"query": "go tokyo", "constraints": {"days": 5}})
        assert resp.status_code == 200
        body = resp.json()
        assert body == {"run_id": "rid", "status": "RUNNING"}  # result MUST NOT be present

        # After response, BackgroundTasks executed stub and wrote SUCCEEDED.
        resp2 = await ac.get("/runs/rid")
        assert resp2.status_code == 200
        run = resp2.json()
        assert run["run_id"] == "rid"
        assert run["status"] == "SUCCEEDED"


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