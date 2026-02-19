import pytest

from app.store.run_store import RunStore
from app.store._test_fakes import FakeRedis


@pytest.mark.anyio
async def test_run_store_create_and_load_ok(monkeypatch):
    r = FakeRedis()
    store = RunStore(r, ttl_s=60)

    # Make uuid deterministic to keep test simple
    import uuid
    monkeypatch.setattr(uuid, "uuid4", lambda: type(
        "U", (), {"hex": "fixedid"})())

    rec = await store.create_run({"query": "q", "constraints": {"days": 3}})
    assert rec.run_id == "fixedid"

    loaded = await store.load_run("fixedid")
    assert loaded is not None
    assert loaded.request["query"] == "q"


@pytest.mark.anyio
async def test_run_store_load_missing_returns_none():
    r = FakeRedis()
    store = RunStore(r, ttl_s=60)
    assert await store.load_run("nope") is None


@pytest.mark.anyio
async def test_run_store_load_corrupted_json_returns_none():
    r = FakeRedis()
    store = RunStore(r, ttl_s=60)

    r.raw_set_str("run:bad", "{not-json")
    assert await store.load_run("bad") is None


@pytest.mark.asyncio
async def test_run_store_save_and_load_state(monkeypatch):
    r = FakeRedis()
    store = RunStore(r, ttl_s=60)

    # Deterministic run_id
    import uuid
    monkeypatch.setattr(uuid, "uuid4", lambda: type("U", (), {"hex": "rid"})())

    rec = await store.create_run({"query": "x", "constraints": None})
    assert rec.run_id == "rid"

    state = {
        "run_id": "rid",
        "trace_id": "tid",
        "request": {"query": "x", "constraints": None},
        "category": "city",
        "plan_steps": [{"tool": "dummy", "args": {}}],
        "observations": [{"tool": "dummy", "ok": True}],
        "result": {"message": "ok"},
        "last_node": "synthesize",
        "errors": [],
    }

    # MUST exist in M1
    await store.save_state("rid", state, last_node="synthesize")
    loaded = await store.load_state("rid")

    assert loaded is not None
    assert loaded["run_id"] == "rid"
    assert loaded["last_node"] == "synthesize"
    assert loaded["result"]["message"] == "ok"
