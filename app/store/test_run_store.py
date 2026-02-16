import pytest
import json

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
