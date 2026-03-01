import pytest

from app.store._test_fakes import FakeRedis
from app.store.run_store import RunStore
from app.agent.runner import WorkflowRunner


@pytest.mark.anyio
async def test_runner_checkpoints_each_step_and_succeeds(monkeypatch):
    """
    Strong expectations:
    - runner must checkpoint state multiple times (>= 5): start + 4 nodes
    - final run record is SUCCEEDED and has result + last_node
    """
    fake = FakeRedis()
    store = RunStore(fake, ttl_s=60)

    # deterministic run_id
    import uuid
    monkeypatch.setattr(uuid, "uuid4", lambda: type("U", (), {"hex": "rid"})())

    rec = await store.create_run({"query": "go", "constraints": {"days": 2}})
    assert rec.run_id == "rid"

    # Spy on save_state calls
    calls = []
    orig_save_state = RunStore.save_state

    async def spy_save_state(self, state):  # noqa: ANN001
        calls.append(state.last_node)
        return await orig_save_state(self, state)

    monkeypatch.setattr(RunStore, "save_state", spy_save_state)

    runner = WorkflowRunner(store)
    await runner.run_workflow("rid")

    # Must have checkpoints: start + each node => >= 5
    assert len(calls) >= 5
    # Strong ordering expectation (your node names should include these tokens)
    joined = " -> ".join(str(x).lower() for x in calls)
    assert "class" in joined
    assert "plan" in joined
    assert "exec" in joined
    assert "synth" in joined

    loaded = await store.load_run("rid")
    assert loaded is not None
    assert loaded.status == "SUCCEEDED"
    assert loaded.result is not None


@pytest.mark.anyio
async def test_runner_checkpoints_and_marks_failed_on_node_error(monkeypatch):
    """
    Strong expectations:
    - If a node throws, runner must:
      - save_state at/around failing node
      - set run status FAILED
      - persist error with node info
    """
    fake = FakeRedis()
    store = RunStore(fake, ttl_s=60)

    import uuid
    monkeypatch.setattr(uuid, "uuid4", lambda: type("U", (), {"hex": "rid"})())
    await store.create_run({"query": "go", "constraints": None})

    # Force plan node to raise
    import app.agent.graph as graph_mod

    async def boom(state):  # noqa: ANN001
        raise RuntimeError("boom")

    monkeypatch.setattr(graph_mod, "plan_node", boom)

    # Spy save_state
    calls = []
    orig_save_state = RunStore.save_state

    async def spy_save_state(self, state):  # noqa: ANN001
        calls.append(state.last_node)
        return await orig_save_state(self, state)

    monkeypatch.setattr(RunStore, "save_state", spy_save_state)

    runner = WorkflowRunner(store)

    # runner may raise or may return an error result; we accept either,
    # but record MUST be marked FAILED.
    try:
        await runner.run_workflow("rid")
    except Exception:
        pass

    assert len(calls) >= 2  # at least start + classify, likely failing at plan
    joined = " -> ".join(str(x).lower() for x in calls)
    assert "plan" in joined or "class" in joined

    loaded = await store.load_run("rid")
    assert loaded is not None
    assert loaded.status == "FAILED"
    assert loaded.errors is not None
    # error should include which node failed (you decide the exact key names)
    assert any(k in loaded.errors for k in ("node", "failed_node", "last_node"))