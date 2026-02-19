import pytest

from app.store._test_fakes import FakeRedis
from app.store.run_store import RunStore


@pytest.mark.asyncio
async def test_runner_runs_workflow_and_persists(monkeypatch):
    # Arrange: create run in store
    r = FakeRedis()
    store = RunStore(r, ttl_s=60)

    import uuid
    monkeypatch.setattr(uuid, "uuid4", lambda: type("U", (), {"hex": "rid"})())
    rec = await store.create_run({"query": "go", "constraints": {"days": 2}})

    # Act: run workflow
    from app.agent.runner import run_workflow
    result = await run_workflow(rec.run_id)

    assert isinstance(result, dict)

    # Assert: run updated in redis (status/result/state)
    loaded = await store.load_run("rid")
    assert loaded is not None
    assert loaded.status in ("SUCCEEDED", "FAILED")
    if loaded.status == "SUCCEEDED":
        assert loaded.result is not None
